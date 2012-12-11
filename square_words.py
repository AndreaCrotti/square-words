__metaclass__ = type

# TODO: one possible euristic is to detect the most used characters
# and try to use words that are using these characters

# another possible heuristic is to use the length of the words trying
# to maximize every time the size we're inserting
import re

from collections import defaultdict
from copy import deepcopy
from itertools import groupby, chain
from string import ascii_lowercase

# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 8
EMPTY = ' '

DICT_FILE = 'cracklib-small'
# if the dictionary is not too small it can be simply loaded up-front
DICT = set(x.strip() for x in open(DICT_FILE))
VERTICAL = 'V'
HORIZONTAL = 'H'


class Words:
    """Class encapsulating the words, to make it easier to manipulate
    them
    """
    def __init__(self, dictfile=DICT_FILE):
        self.dictfile = dictfile
        self.dict = set(x.strip() for x in open(DICT_FILE))
        self.dict_per_length = self.match_length()

    def __contains__(self, val):
        return val in self.dict

    def match_length(self):
        dic_len = defaultdict(list)
        for word in self.dict:
            dic_len[len(word)].append(word)

        return dic_len

    def match_prototype(self, to_find):
        """Given a word with spaces, return the list of strings that
        would match that
        """
        to_find = to_find.replace(EMPTY, '[a-z]')
        return [x for x in self.dict if re.match(to_find, x)]

    def length_word(self, dim):
        return iter(self.dict_per_length[dim])


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

    def is_valid(self, word_dict):
        """Return true if all the words in the grid are valid words
        """
        return all((x in word_dict) for x in self.words)

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
            res += len([x for x in line if x in ascii_lowercase])
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
        # take the first available place
        if pos is None:
            pos = self.empty_cells().next()

        cells = deepcopy(self.cells)
        for i in range(len(word)):
            if direction == VERTICAL:
                pos = i, pos[1]
            else:
                pos = pos[0], i

            assert cells[pos[0]][pos[1]] == EMPTY, "%s Must be empty" % str(pos)
            cells[pos[0]][pos[1]] = word[i]

        grid = Grid(self.length, cells=cells)
        return grid


def main():
    grid = Grid()


if __name__ == '__main__':
    main()
