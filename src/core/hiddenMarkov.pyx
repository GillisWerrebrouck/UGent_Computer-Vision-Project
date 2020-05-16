import functools
import operator
import numpy as np
from statistics import mode, StatisticsError

from core.logger import get_root_logger
from core.transitions import indices, transitions

logger = get_root_logger()

cdef class HiddenMarkov:

    cdef int _start_prob_count, _min_observations
    cdef int _circular_index, _nr_of_samples
    cdef str _current_room
    cdef float _weight_non_possible_rooms
    cdef dict _counters
    cdef list _circular_buffer


    def __init__(self, min_observations=5, weight_non_possible_rooms=0.5):
        self._start_prob_count = 0
        self._current_room = 'INKOM'
        self._weight_non_possible_rooms = weight_non_possible_rooms
        self.__init_counters()

        # we're going to keep the last `min_observations` in a circular array
        self._min_observations = min_observations
        self._circular_index = 0
        self._circular_buffer = [None] * min_observations
        self._nr_of_samples = 0


    cpdef __init_counters(self):
        self._counters = {}

        for room, _ in indices.items():
            self._counters[room] = 1

        self._counters['INKOM'] = 1


    cpdef predict(self, object quadrilateral_chances):
        logger.info(quadrilateral_chances)

        if not len(quadrilateral_chances):
            return (self._counters, self._current_room, transitions[self._current_room])

        cdef str observation = self.__play_the_odds(quadrilateral_chances)

        logger.info('Observed room {}'.format(observation))

        self._nr_of_samples += 1
        cdef list possible_rooms = transitions[self._current_room]

        if observation in possible_rooms:
            self._circular_buffer[self._circular_index] = observation
        else:
            self._circular_buffer[self._circular_index] = self._current_room

        self._circular_index = (self._circular_index + 1) % self._min_observations

        logger.debug(self._circular_buffer)
        logger.debug(self._counters)
        try:
            if self._nr_of_samples >= self._min_observations:
                self._current_room = mode(self._circular_buffer)
        except StatisticsError:
            # we have two modi, skip the prediction here
            pass

        return (self._counters, self._current_room, transitions[self._current_room])


    cpdef get_possible_transitions(self):
        return transitions[self._current_room]


    cdef __play_the_odds(self, object quadriliterals):
        cdef list possible_rooms = transitions[self._current_room]

        cdef list flattened = functools.reduce(operator.iconcat, quadriliterals, [])

        if len(flattened) == 0:
            return self._current_room

        # keep a list that tracks which rooms we've already seen
        cdef object freq_list = np.zeros(len(indices))

        # keep a list of chances that we're in this room
        cdef object chances_here = np.zeros(len(indices))

        # keep a list of chances that we're not in this room
        cdef object chances_not_here = np.zeros(len(indices))

        cdef int index
        cdef float chance, weight
        cdef str filename, room
        for prediction in flattened:
            chance, _, room = prediction
            index = indices[room]
            weight = 1 if room in possible_rooms else self._weight_non_possible_rooms
            chance *= weight

            if freq_list[index] == 0:
                # we've not had this room before, set the chance to 1, this is easier for the maths
                chances_here[index] = 1
                chances_not_here[index] = 1
                freq_list[index] = 1

            chances_here[index] *= chance
            chances_not_here[index] *= (1 - chance)

        cdef float max_chance = 0
        cdef str max_room = None

        cdef float nominator = 0, denominator = 0, new_chance = 0
        for room, chance in self._counters.items():
            index = indices[room]
            chances_here[index] *= chance if chance != 0 else 1
            chances_not_here[index] *= (1 - chance) if chance != 1 else 1

            nominator = chances_here[index]
            denominator = chances_here[index] + chances_not_here[index]
            new_chance = nominator / denominator if denominator > 0 else 0
            self._counters[room] = new_chance

            if new_chance > max_chance:
                max_room = room
                max_chance = new_chance

        return max_room


    cdef __get_max_chance_room(self, object quadriliterals):
        cdef int max_chance = 0
        cdef str max_room = None

        cdef set rooms = set()

        for quad in quadriliterals:
            if len(quad):
                rooms.add(quad[0][2])

            if len(quad) and quad[0][0] > max_chance:
                max_chance = quad[0][0]
                max_room = quad[0][2]

        logger.info('Possibilities: {}'.format(rooms))
        return max_room


    cdef __get_most_common_room(self, object quadriliterals):
        cdef list flattened = functools.reduce(operator.iconcat, quadriliterals, [])
        cdef int length = len(flattened)

        cdef dict means = {}

        for prediction in flattened:
            chance, _, room = prediction

            if room not in means:
                means[room] = 0

            means[room] += chance

        cdef float max_mean = 0
        cdef str max_room = None

        for room, mean in means.items():
            if mean > max_mean:
                max_mean = mean
                max_room = room

        return max_room


