import functools
import operator
import numpy as np
from statistics import mode, StatisticsError

from core.logger import get_root_logger
from core.transitions import indices, transitions

logger = get_root_logger()

cdef class HiddenMarkov:

    cdef int _start_prob_count, _min_start_count, _min_observations
    cdef int _circular_index, _nr_of_samples
    cdef str _current_room
    cdef float _weight_non_possible_rooms
    cdef dict _counters
    cdef list _circular_buffer


    def __init__(self, min_start_count=20, min_observations=5, weight_non_possible_rooms=0.5):
        self._start_prob_count = 0
        self._min_start_count = min_start_count
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


    cpdef predict(self, quadriliteral_chances):
        print(quadriliteral_chances)
        if not len(quadriliteral_chances):
            return (self._counters, self._current_room, transitions[self._current_room])

        observation = self.__play_the_odds(quadriliteral_chances)

        logger.info('Observed room {}'.format(observation))

        self._nr_of_samples += 1
        possible_rooms = transitions[self._current_room]

        if observation in possible_rooms:
            self._circular_buffer[self._circular_index] = observation
        else:
            self._circular_buffer[self._circular_index] = self._current_room

        self._circular_index = (self._circular_index + 1) % self._min_observations

        try:
            if self._nr_of_samples >= self._min_observations:
                self._current_room = mode(self._circular_buffer)
        except StatisticsError:
            # we have two modi, skip the prediction here
            pass

        return (self._counters, self._current_room, transitions[self._current_room])


    cpdef get_possible_transitions(self):
        return transitions[self._current_room]


    cdef __play_the_odds(self, quadriliterals):
        possible_rooms = transitions[self._current_room]

        flattened = functools.reduce(operator.iconcat, quadriliterals, [])

        if len(flattened) == 0:
            return self._current_room

        # keep a list that tracks which rooms we've already seen
        freq_list = np.zeros(len(indices))

        # keep a list of chances that we're in this room
        chances_here = np.zeros(len(indices))

        # keep a list of chances that we're not in this room
        chances_not_here = np.zeros(len(indices))

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

        max_chance = 0
        max_room = None

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


    cdef __get_max_chance_room(self, quadriliterals):
        maxChance = 0
        maxRoom = None

        rooms = set()

        for quad in quadriliterals:
            if len(quad):
                rooms.add(quad[0][2])

            if len(quad) and quad[0][0] > maxChance:
                maxChance = quad[0][0]
                maxRoom = quad[0][2]

        logger.info('Possibilities: {}'.format(rooms))
        return maxRoom


    cdef __get_most_common_room(self, quadriliterals):
        flattened = functools.reduce(operator.iconcat, quadriliterals, [])
        length = len(flattened)

        means = {}

        for prediction in flattened:
            chance, _, room = prediction

            if room not in means:
                means[room] = 0

            means[room] += chance

        maxMean = 0
        maxRoom = None

        for room, mean in means.items():
            if mean > maxMean:
                maxMean = mean
                maxRoom = room

        return maxRoom


