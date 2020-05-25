from collections import defaultdict

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
    'V': 37,
    'ENTRANCE': 38
}

entrance = ['1', '2', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'II', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'V']

neighbour_list = {
    '1': ['1', '2', 'II'],
    '2': ['1', '2', '5'],
    '5': ['2', '5', '7', 'II'],
    '6': ['6', '7', '9', 'II'],
    '7': ['5', '6', '7', '8', '9'],
    '8': ['7', '8', '13'],
    '9': ['6', '7', '9', '10'],
    '10': ['9', '10', '11'],
    '11': ['10', '11', '12'],
    '12': ['11', '12', '19', 'V', 'L', 'S'],
    '13': ['8', '13', '14', '16', '17'],
    '14': ['13', '14', '15', '16'],
    '15': ['14', '15', '16'],
    '16': ['13', '14', '15', '16', '17', '18', '19'],
    '17': ['13', '16', '17', '18', '19'],
    '18': ['16', '17', '18', '19'],
    '19': ['16', '17', '18', '19', 'V', '12', 'L'],
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
    'L': ['K', 'L', '19', 'V', '12', 'S'],
    'M': ['H', 'M', 'N', 'P', 'Q'],
    'N': ['M', 'N', 'O', 'P'],
    'O': ['N', 'O', 'P'],
    'P': ['M', 'N', 'O', 'P', 'Q', 'R', 'S'],
    'Q': ['M', 'P', 'Q', 'R', 'S'],
    'R': ['P', 'Q', 'R', 'S'],
    'S': ['P', 'Q', 'R', 'S', 'V', 'L', '12'],
    'V': ['19', 'S', 'V', '12', 'L']
}

# defaultdict(int) gives 0 as standard when the key is not present
# this is what we want! This way we don't need to add every missing
# room with 0 as a chance
transitions = {
    'ENTRANCE': defaultdict(int)
}

DECREASE_FACTOR = 2

for room in entrance:
    transitions['ENTRANCE'][room] = 1

for room in neighbour_list.keys():
    queue = list([(room, 1, 0)])
    neighbours = defaultdict(int)

    # add the immediate neighbours with the same chance
    for immediate_neighbour in neighbour_list[room]:
        queue.append((immediate_neighbour, 1, 1))

    # find 2nd degree neighbours
    while len(queue) is not 0:
        neighbour, chance, level = queue[0]
        queue.pop(0)

        if level > 2:
            continue

        if neighbour not in neighbours:
            neighbours[neighbour] = chance

            level += 1

            for decendant in neighbour_list[neighbour]:
                if decendant not in neighbours:
                    queue.append((decendant, chance / DECREASE_FACTOR, level))

    transitions[room] = neighbours
