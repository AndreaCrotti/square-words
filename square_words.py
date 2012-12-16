__metaclass__ = type

# TODO: one possible euristic is to detect the most used characters
# and try to use words that are using these characters

# another possible heuristic is to use the length of the words trying
# to maximize every time the size we're inserting

# TODO: check which methods are doing some mutations and try to make
# them more functional
import re

from collections import defaultdict
from copy import deepcopy
from functools import reduce
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


class NotEmptyCell(Exception): pass
class NotValidGrid(Exception): pass


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
        """Generates a dictionary with length and word list
        """
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
        """Return an iterator over the list of words per given length
        """
        return iter(self.dict_per_length[dim])


def words_in_line(line):
    """Return the words in the list of chars
    """
    grouped = groupby(line, lambda x: x == EMPTY)
    ls = [list(x[1]) for x in grouped if not x[0]]
    return [''.join(x) for x in ls]


def cell_pos(pos, direction, length):
    for i in range(length):
        if direction == VERTICAL:
            yield i + pos[0], pos[1]
        else:
            yield pos[0], i + pos[1]


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
        return '\n'.join(''.join(x) for x in self.lines())

    def __getitem__(self, item):
        return self.cells[item]

    def __iter__(self):
        return chain(self.lines(), self.columns())

    @classmethod
    def grid_from_string_list(cls, string_list):
        length_strings = map(len, string_list)
        assert len(string_list) > 0, "empty list passed in"
        assert len(set(length_strings)) == 1, "should give equal length strings"
        cells = [list(x) for x in string_list]
        return cls(len(string_list[0]), cells=cells)

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
        all_words_per_line = [words_in_line(line) for line in self]
        flattened_words = reduce(lambda x, y: x + y, all_words_per_line)
        return [x for x in flattened_words if len(x) > 1]

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
        return (self.length ** 2) - self.tot_chars

    def place_word(self, word, pos=None, direction=VERTICAL):
        """Place a word in the grid returning a new grid object
        """
        assert len(word) <= self.length, "word does not fit in the grid"
        # take the first available place, but this also depends on the
        # direction we want to go
        if pos is None:
            pos = self.empty_cells().next()

        cells = deepcopy(self.cells)
        for idx, (x, y) in enumerate(cell_pos(pos, direction, len(word))):
            if cells[x][y] != EMPTY:
                raise NotEmptyCell("%d, %d Must be empty" % (x, y))

            cells[x][y] = word[idx]

        new_grid = Grid(self.length, cells=cells)
        if not new_grid.is_valid:
            raise NotValidGrid("Grid %s contains some non words" % str(new_grid))

        return new_grid


def alternate_dir_pos(length):
    for n in range(0, length, 2):
        yield (n, 0), VERTICAL
        yield (0, n), HORIZONTAL


def maximize_step(grid, words):
    # TODO: we might want to pass some kind of hint to the
    # maximization or define a class of possible behaviours that can
    # be applied to transform the grid automatically
    for length in range(grid.length, 1, -1):
        ws = words.length_word(length)
        while True:
            word = ws.next()
            try:
                # TODO: place word should fail in case the produced
                # thing is not valid
                new_grid = grid.place_word(word)
            except AssertionError:
                continue
            else:
                return new_grid


def main():
    words = Words()
    old_grid = Grid()
    while True:
        next_grid = maximize_step(old_grid, words)
        print("New grid:\n {}\n has {} tot chars".format(next_grid, next_grid.tot_chars))
        if next_grid.tot_chars == old_grid.tot_chars:
            break
        else:
            old_grid = next_grid


if __name__ == '__main__':
    print(main())
