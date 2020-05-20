import functools
import operator
from time import time
import numpy as np
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


    def __init__(self, min_observations=5):
        self._start_prob_count = 0
        self._current_room = 'ENTRANCE'
        self.__init_counters()

        # we're going to keep the last `min_observations` in a circular array
        self._min_observations = min_observations
        self._circular_index = 0
        self._circular_buffer = []
        self._nr_of_samples = 0
        self._initialized = False


    cpdef __init_counters(self):
        self._counters = {}

        for room, _ in indices.items():
            self._counters[room] = 1


    cpdef predict(self, object quadrilateral_chances):
        cdef list flattened = functools.reduce(operator.iconcat, quadrilateral_chances, [])
        logger.info(flattened)

        cdef str observation = self._current_room

        if len(flattened):
            observation = self.__play_the_odds(flattened)

        logger.info('Observed room {}'.format(observation))

        self._nr_of_samples += 1
        cdef dict possible_rooms = transitions[self._current_room]

        if observation in possible_rooms:
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
        cdef int index, max_count = 0
        cdef str max_room = 'ENTRANCE'
        cdef dict freq_list = {}

        for room in self._circular_buffer:
            if room not in freq_list:
                freq_list[room] = 0

            freq_list[room] += 1


        for room, count in freq_list.items():
            # strict greater count OR
            # equal count but strict greater chance
            if count > max_count or (count == max_count and self._counters[room] > self._counters[max_room]):
                max_count = count
                max_room = room

        return max_room



    cdef __play_the_odds(self, object quadrilaterals):
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
        cdef dict possible_rooms = transitions[self._current_room]

        # keep a list that tracks which rooms we've already seen
        cdef object chances_here = np.zeros(len(indices))

        # keep a list of chances that we're not in this room
        cdef object chances_not_here = np.zeros(len(indices))

        cdef int index
        cdef float chance
        cdef str room
        cdef int current_room_predicted = False

        # collect the current chances in the arrays above
        for room, chance in possible_rooms.items():
            if chance > 0:
                index = indices[room]
                chances_here[index] = self._counters[room]
                chances_not_here[index] = 1 - self._counters[room]

        # loop over all predictions and determine the chances that we are or aren't in a given room
        for prediction in quadrilaterals:
            chance, _, room = prediction
            current_room_predicted = room == self._current_room

            index = indices[room]
            # multiply the chance by its weight
            chance *= possible_rooms[room]

            chances_here[index] *= chance
            chances_not_here[index] *= (1 - chance)

        cdef double total = 0, new_chance

        # calculate the combined chances for each room and find the room with the highest value
        for room in self._counters.keys():
            index = indices[room]

            if room in possible_rooms and possible_rooms[room] > 0:
                nominator = chances_here[index]
                denominator = chances_here[index] + chances_not_here[index]

                if denominator > 0:
                    new_chance = nominator / denominator
                elif room != 'ENTRANCE':
                    new_chance = 0

                total += new_chance
            else:
                new_chance = 0

            chances_here[index] = new_chance

        total *= 1.02

        chances_here /= total
        return chances_here

