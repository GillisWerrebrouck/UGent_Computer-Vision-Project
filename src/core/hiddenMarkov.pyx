import functools
import operator
from time import time
import numpy as np
import pickle
import json
from statistics import mode, StatisticsError

from core.logger import get_root_logger
from core.transitions import indices, transitions

logger = get_root_logger()

cdef class HiddenMarkov:

    cdef int _start_prob_count, _min_observations
    cdef int _circular_index, _nr_of_samples
    cdef str _current_room
    cdef dict _counters
    cdef list _circular_buffer
    cdef int _initialized
    cdef dict _room_factors


    def __init__(self, min_observations=5):
        """
        Initialize a Hidden Markov model.

        Parameters
        ----------
        - min_observations -- The number of observations to make before
        choosing the initial room (default: 5).
        """
        self._start_prob_count = 0
        self._current_room = 'ENTRANCE'
        self.__init_counters()

        # we're going to keep the last `min_observations` in a circular array
        self._min_observations = min_observations
        self._circular_index = 0
        self._circular_buffer = []
        self._nr_of_samples = 0
        self._initialized = False
        self.__load_room_factors()


    cpdef __load_room_factors(self):
        cdef dict temp_room_factors
        self._room_factors = {}

        with open('./room_calibrations.pickle', 'rb') as handle:
            temp_room_factors = pickle.load(handle)

        for room in temp_room_factors:
            if 1 < temp_room_factors[room][1]:
                temp_room_factors[room] = (temp_room_factors[room][0], 1)
            self._room_factors[room] = 1 - temp_room_factors[room][1]

            # interpolate to other range
            self._room_factors[room] = np.interp(self._room_factors[room], [0, 1], [1, 2.2])

        logger.info("Calibrated room factors: " + str(json.dumps(self._room_factors)))


    cpdef __init_counters(self):
        """
        Initialize every room's chance to 1, so every room is possible.

        Parameters
        ----------
        None

        Returns
        -------
        Nothing
        """
        self._counters = {}

        for room, _ in indices.iteritems():
            self._counters[room] = 1


    cpdef predict(self, object quadrilateral_chances):
        """
        Predict the current room given the chances. These steps are performed:
        1. Combine all chances into one chance per room
        2. Determine the (accessible) room with the highest chance
        3. Check if the predicted room is possible
        4. If so, return it. Else, return the current room.

        This method does not return a value until enough predictions where made.
        This is determined by the parameter `min_observations`. If enough predictions
        were made, the most common room is taken as the initial room. Then every
        predicted room is returned if it's accessible from within the current room.

        Parameters
        ----------
        - quadrilaterals -- Array of chances, format: [chance, filename, room]

        Returns
        -------
        The predicted room.
        """
        cdef object flattened = np.array(functools.reduce(operator.iconcat, quadrilateral_chances, []))
        logger.info(flattened)

        cdef str observation = self._current_room

        if len(flattened):
            observation = self.__play_the_odds(flattened)

        logger.info('Observed room {}'.format(observation))

        self._nr_of_samples += 1
        # object because it's a default dict
        cdef object possible_rooms = transitions[self._current_room]

        if observation in possible_rooms and possible_rooms[observation] == 0:
            observation = self._current_room

        if self._initialized:
            self._current_room = observation
        elif len(self._circular_buffer) < self._min_observations:
            self._circular_buffer.append(observation)
        else:
            self._current_room = self.__get_most_common_room()
            self._initialized = True

        logger.debug(self._counters)

        return (self._counters, self._current_room)


    cdef __get_most_common_room(self):
        """
        Find the most common room in the history of predictions.
        This history is used to determine the starting room
        of the video.

        Parameters
        ----------
        None

        Returns
        -------
        The most common room in the history.
        """
        cdef int index, max_count = 0
        cdef str max_room = 'ENTRANCE'
        cdef dict freq_list = {}

        for room in self._circular_buffer:
            if room not in freq_list:
                freq_list[room] = 0

            freq_list[room] += 1


        for room, count in freq_list.iteritems():
            # strict greater count OR
            # equal count but strict greater chance
            if count > max_count or (count == max_count and self._counters[room] > self._counters[max_room]):
                max_count = count
                max_room = room

        return max_room


    cdef __play_the_odds(self, object quadrilaterals):
        """
        Predict the current room given the chances passed as a parameter.
        This function calculates a chance per possible room (from within
        the current room) and normalizes these chances. Then it searches
        and returns the room with the highest chance as a prediction.

        Parameters
        ----------
        - quadrilaterals -- Array of chances, format: [chance, filename, room]

        Returns
        -------
        The predicted room.
        """
        # first get the updated chances for each room
        cdef object chances = self.__combine_chances(quadrilaterals)

        cdef int index
        cdef float chance, max_chance = 0
        cdef str max_room = self._current_room

        # update the dict with all chances per room
        for room in self._counters.keys():
            index = indices[room]
            chance = chances[index]
            self._counters[room] = chance

            if chance > max_chance:
                max_room = room
                max_chance = chance

        return max_room


    cdef __combine_chances(self, object quadrilaterals):
        """
        Given a list of possibly multiple chances per room, combine
        them into one chance per room. This chance takes the current
        chance for each room into account if the room is accessible
        from within the current room.

        Parameters
        ----------
        - quadrilaterals -- Array of chances, format: [chance, filename, room]

        Returns
        -------
        An array of chances per room, indexed by indices stored in the
        dictionary in the transitions module.
        """
        # object because it's a default dict
        cdef object possible_rooms = transitions[self._current_room]

        # delete the filename
        quadrilaterals = np.delete(quadrilaterals, 1, 1)

        # result array with chances per room
        cdef int index
        cdef float chance, total = 0
        cdef str room
        cdef object chances = np.zeros(len(indices)), quad, chance_np_str, room_np_str
        cdef dict grouped_chances = {}

        # add the existing chances if possible from within current room
        for room, chance in self._counters.iteritems():
            if room in possible_rooms and possible_rooms[room] > 0:
                quadrilaterals = np.append(quadrilaterals, [chance, room])

        # reshape because numpy flattens when not asked for
        quadrilaterals = np.reshape(quadrilaterals, (-1, 2))

        # group all chances by room
        for chance_np_str, room_np_str in quadrilaterals:
            chance = float(chance_np_str)
            room = str(room_np_str)
            if room not in grouped_chances:
                grouped_chances[room] = np.array([], dtype=np.float64)

            grouped_chances[room] = np.append(grouped_chances[room], float(chance))

        # calculate an aggregated chance per room
        for room, chances_for_room in grouped_chances.iteritems():
            chance_here = np.prod(chances_for_room)
            chance_not_here = np.prod(1 - chances_for_room)

            chance_here *= self._room_factors[room]
            chance_not_here *= (self._room_factors[room])
            print(self._room_factors)

            chance = chance_here / (chance_here + chance_not_here)

            index = indices[room]
            chances[index] = chance

        # normalize all chances (so the total sum is between 0 and 1)
        for room in self._counters.keys():
            index = indices[room]

            if room in possible_rooms and possible_rooms[room] > 0:
                total += chances[index]
            else:
                chances[index] = 0

        # we must be sure that a room doesn't get 100% chance
        # then, we would never be able to escape that room
        total *= 1.02

        chances /= total
        return chances

