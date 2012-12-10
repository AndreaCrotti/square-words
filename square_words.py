__metaclass__ = type

from itertools import groupby, chain
from string import ascii_uppercase

# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 8
EMPTY = ' '

DICT_FILE = 'cracklib-small'
# if the dictionary is not too small it can be simply loaded up-front
DICT = set(x.strip() for x in open(DICT_FILE))


def is_valid_word(word):
    return word in DICT


def words_in_line(line):
    """Return the words in the list of chars
    """
    grouped = groupby(line, lambda x: x == EMPTY)
    ls = [list(x[1]) for x in grouped if not x[0]]
    return [''.join(x) for x in ls]


class Grid:
    def __init__(self, length=GRID_SIZE):
        self.length = length
        self.grid = []
        for _ in range(self.length):
            self.grid.append([EMPTY] * self.length)

    def __str__(self):
        return '\n'.join(''.join(x) for x in self)

    def __getitem__(self, item):
        return self.grid[item]

    def __iter__(self):
        return chain(self.lines(), self.columns())

    def lines(self):
        return iter(self.grid[:])

    def columns(self):
        for n in range(self.length):
            yield [self.grid[i][n] for i in range(self.length)]

    @property
    def words(self):
        unflat = [words_in_line(line) for line in self]
        flat = reduce(lambda x, y: x + y, unflat)
        # TODO: check if the filtering should be done in words_per_line?
        return [x for x in flat if len(x) > 1]

    @property
    def tot_chars(self):
        res = 0
        for line in self.grid:
            res += len([x for x in line if x in ascii_uppercase])
        return res

    @property
    def empty(self):
        return self.length ** 2
