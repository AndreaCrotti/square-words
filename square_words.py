__metaclass__ = type

# TODO: one possible euristic is to detect the most used characters
# and try to use words that are using these characters

from copy import deepcopy
from itertools import groupby, chain
from string import ascii_uppercase

# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 8
EMPTY = ' '

DICT_FILE = 'cracklib-small'
# if the dictionary is not too small it can be simply loaded up-front
DICT = set(x.strip() for x in open(DICT_FILE))
VERTICAL = 'V'
HORIZONTAL = 'H'


def is_valid_word(word):
    return word in DICT


def words_in_line(line):
    """Return the words in the list of chars
    """
    grouped = groupby(line, lambda x: x == EMPTY)
    ls = [list(x[1]) for x in grouped if not x[0]]
    return [''.join(x) for x in ls]


class Grid:
    def __init__(self, length=GRID_SIZE, cells=None):
        self.length = length
        if cells:
            self.cells = cells
        else:
            self.cells = []
            for _ in range(self.length):
                self.cells.append([EMPTY] * self.length)

    def __str__(self):
        return '\n'.join(''.join(x) for x in self)

    def __getitem__(self, item):
        return self.cells[item]

    def __iter__(self):
        return chain(self.lines(), self.columns())

    def lines(self):
        return iter(self.cells[:])

    def columns(self):
        for n in range(self.length):
            yield [self.cells[i][n] for i in range(self.length)]

    def is_valid(self):
        """Return true if all the words in the grid are valid words
        """
        return all(is_valid_word(x) for x in self.words)

    @property
    def words(self):
        unflat = [words_in_line(line) for line in self]
        flat = reduce(lambda x, y: x + y, unflat)
        # TODO: check if the filtering should be done in words_per_line?
        return [x for x in flat if len(x) > 1]

    @property
    def tot_chars(self):
        res = 0
        for line in self.cells:
            res += len([x for x in line if x in ascii_uppercase])
        return res

    def empty_cells(self):
        for i in range(self.length):
            for j in range(self.length):
                if self.cells[i][j] == EMPTY:
                    yield i, j

    @property
    def empty(self):
        return self.length ** 2

    def place_word(self, word, pos=None, direction=VERTICAL):
        """Place a word in the grid returning a new grid object
        """
        assert len(word) <= self.length, "word does not fit in the grid"
        cells = deepcopy(self.cells)
        for i in range(len(word)):
            if direction == VERTICAL:
                pos = i, pos[1]
            else:
                pos = pos[0], i

            cells[pos[0]][pos[1]] = word[i]

        grid = Grid(self.length, cells=cells)
        return grid
