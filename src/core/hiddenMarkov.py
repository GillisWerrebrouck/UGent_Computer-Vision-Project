import functools
import operator
import numpy as np
from hmmlearn.hmm import MultinomialHMM
from statistics import mode, StatisticsError

from core.logger import get_root_logger

logger = get_root_logger()

indices = {
    '1': 0,
    '2': 1,
    '5': 2,
    '6': 3,
    '7': 4,
    '8': 5,
    '9': 6,
    '10': 7,
    '11': 8,
    '12': 9,
    '13': 10,
    '14': 11,
    '15': 12,
    '16': 13,
    '17': 14,
    '18': 15,
    '19': 16,
    'A': 17,
    'B': 18,
    'C': 19,
    'D': 20,
    'E': 21,
    'F': 22,
    'G': 23,
    'H': 24,
    'I': 25,
    'II': 26,
    'J': 27,
    'K': 28,
    'L': 29,
    'M': 30,
    'N': 31,
    'O': 32,
    'P': 33,
    'Q': 34,
    'R': 35,
    'S': 36,
    'V': 37
}

transitions = {
    'INKOM': ['1', '2', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'II', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'V'],
    '1': ['1', '2', 'II'],
    '2': ['1', '2', '5'],
    '5': ['2', '5', '7', 'II'],
    '6': ['6', '7', '9', 'II'],
    '7': ['5', '6', '7', '8', '9'],
    '8': ['7', '8', '13'],
    '9': ['6', '7', '9', '10'],
    '10': ['9', '10', '11'],
    '11': ['10', '11', '12'],
    '12': ['11', '12'],
    '13': ['8', '13', '14', '16', '17'],
    '14': ['13', '14', '15', '16'],
    '15': ['14', '15', '16'],
    '16': ['13', '14', '15', '16', '17', '18', '19'],
    '17': ['13', '16', '17', '18', '19'],
    '18': ['16', '17', '18', '19'],
    '19': ['16', '17', '18', '19', 'V'],
    'A': ['A', 'B', 'II'],
    'B': ['A', 'B', 'C', 'D', 'E'],
    'C': ['B', 'C', 'D'],
    'D': ['B', 'C', 'D', 'E', 'G', 'H'],
    'E': ['B', 'D', 'E', 'G', 'II'],
    'F': ['G', 'F', 'I', 'II'],
    'G': ['D', 'E', 'F', 'G', 'H', 'I'],
    'H': ['D', 'G', 'H', 'M'],
    'I': ['G', 'F', 'I', 'J'],
    'II': ['1', '5', '6', 'A', 'E', 'F', 'II'],
    'J': ['I', 'J', 'K'],
    'K': ['J', 'K', 'L'],
    'L': ['K', 'L'],
    'M': ['H', 'M', 'N', 'P', 'Q'],
    'N': ['M', 'N', 'O', 'P'],
    'O': ['N', 'O', 'P'],
    'P': ['M', 'N', 'O', 'P', 'Q', 'R', 'S'],
    'Q': ['M', 'P', 'Q', 'R', 'S'],
    'R': ['P', 'Q', 'R', 'S'],
    'S': ['P', 'Q', 'R', 'S', 'V'],
    'V': ['19', 'S', 'V']
}

class HiddenMarkov:

    def __init__(self, min_start_count=20, min_observations=5):
        self._counters = np.zeros(len(indices))
        self._start_prob_count = 0
        self._min_start_count = min_start_count
        self._currentRoom = 'INKOM'
        self.__init_counters()

        # we're going to keep the last `min_observations` in a circular array
        self._min_observations = min_observations
        self._circular_index = 0
        self._circular_buffer = [None] * min_observations
        self._nr_of_samples = 0


    def __init_counters(self):
        self._counters = {}

        for room, _ in indices.items():
            self._counters[room] = 0 # every room is likely


    def __pick_start_room(self):
        maxCount = 0
        maxRoom = None

        for room, count in self._counters.items():
            if count > maxCount:
                maxRoom = room
                maxCount = count

        self._currentRoom = maxRoom
        self._counters = None


    def predict(self, quadriliteral_chances):
        # observation = self.__get_most_common_room(quadriliteral_chances)
        self.__play_the_odds(quadriliteral_chances)
        observation = self.__get_max_chance_room(quadriliteral_chances)

        logger.info('Observed room {}'.format(observation))

        self._nr_of_samples += 1
        possible_rooms = transitions[self._currentRoom]

        if observation in possible_rooms:
            self._circular_buffer[self._circular_index] = observation
        else:
             self._circular_buffer[self._circular_index] = self._currentRoom
        self._circular_index = (self._circular_index + 1) % self._min_observations

        try:
            if self._nr_of_samples >= self._min_observations:
                self._currentRoom = mode(self._circular_buffer)
        except StatisticsError:
            # we have two modi, skip the prediction here
            pass

        return self._currentRoom


    def __play_the_odds(self, quadriliterals):
        for quad in quadriliterals:
            if len(quad):
                chance = quad[0][0]
                room = quad[0][2]
                self._counters[room] += chance


    def __get_max_chance_room(self, quadriliterals):
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


    def __get_most_common_room(self, quadriliterals):
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


