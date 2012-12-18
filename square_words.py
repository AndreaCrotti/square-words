from __future__ import division

__metaclass__ = type
# TODO: when we reduce the size for a line, don't give it for lost
# and try again
import re

from collections import defaultdict, Counter
from copy import deepcopy
from functools import reduce
from itertools import groupby, chain
from random import random
from string import ascii_lowercase

LINES_STEP = 1
# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 10
EMPTY = ' '

DICTS_FILE = ['british', 'cracklib-small']
RESULTS = 'results.txt'

VERTICAL = 'V'
HORIZONTAL = 'H'


class InvalidCellSet(Exception): pass
class NotValidGrid(Exception): pass


class Words:
    """Class encapsulating the words, to make it easier to manipulate
    them
    """
    # we can choose here which kind of strategy might be used first
    MOST_USED_FIRST = 1
    LONGEST_FIRST = 1

    def __init__(self, dictfiles=DICTS_FILE, randomize=False):
        self.dict = self._init_dict(dictfiles)
        self.dict_per_length = self.match_length()
        self.most_common = dict(self.most_common_chars())
        self.tot_chars = sum(self.most_common.values())
        self.randomize = randomize

    def _init_dict(self, dictfiles):
        dic = set()
        for dicf in dictfiles:
            # TODO: if we want to skip the names we have to filter the
            # uppercase words
            dic.update(x.strip().lower() for x in open(dicf))
        print("Using a dictionary with %d words" % len(dic))
        return dic

    def __contains__(self, val):
        return val in self.dict

    def most_common_chars(self):
        """Return a dictionary with the most common chars, and their
        frequency
        """
        all_chars = reduce(lambda x, y: x + y, self.dict)
        count = Counter(all_chars)
        return count.most_common()

    def rank_word(self, word):
        """Average on the length of the word of the average chars
        """
        return sum(self.most_common[x] for x in word) / len(word)

    def match_length(self):
        """Generates a dictionary with length and word list
        """
        dic_len = defaultdict(list)
        for word in self.dict:
            dic_len[len(word)].append(word)

        return dic_len

    def sorting_key_function(self, word):
        """Maximize the length of the function and the ranking
        """
        res = len(word) * self.rank_word(word)
        if self.randomize:
            res *= random()

        return res

    def longest_prototype(self, prototype, limit):
        all_prototypes = self.match_prototype(prototype)
        in_bound = [w for w in all_prototypes if len(w) <= limit]
        for w in sorted(in_bound, key=self.sorting_key_function, reverse=True):
            yield w

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
    def __init__(self, dic, length=GRID_SIZE, cells=None):
        self.dic = dic
        self.length = length
        if cells:
            self.cells = cells
        else:
            self.cells = []
            for _ in range(self.length):
                self.cells.append([EMPTY] * self.length)

    def __getitem__(self, item):
        return self.cells[item]

    def __iter__(self):
        return chain(self.lines(), self.columns())

    def __str__(self):
        border = '+{}+'.format('-' * (self.length * 2 - 1))

        def pretty_line(line):
            return '|{}|'.format('|'.join(line))

        content = '\n'.join(pretty_line(x) for x in self.lines())
        return '\n'.join([border, content, border])

    def max_length(self, pos, direction):
        if direction == VERTICAL:
            return self.length - pos[0]
        else:
            return self.length - pos[1]

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

    def is_valid(self):
        """Return true if all the words in the grid are valid words
        """
        return all((x in self.dic) for x in self.words)

    def get_prototype(self, pos, direction, length):
        all_pos = cell_pos(pos, direction, length)
        return ''.join(self.cells[x][y] for x, y in all_pos)

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

    @property
    def empty(self):
        return (self.length ** 2) - self.tot_chars

    def place_word(self, word, pos=(0, 0), direction=VERTICAL):
        """Place a word in the grid returning a new grid object
        """
        assert len(word) <= self.length, "word does not fit in the grid"

        cells = deepcopy(self.cells)
        for idx, (x, y) in enumerate(cell_pos(pos, direction, len(word))):
            # the cell does not need to be empty if we want to set the same char
            if cells[x][y] != EMPTY:
                if cells[x][y] != word[idx]:
                    raise InvalidCellSet("Position %d, %d is already set to %s" % (x, y, cells[x][y]))
            else:
                cells[x][y] = word[idx]

        new_grid = Grid(self.dic, self.length, cells=cells)
        if not new_grid.is_valid():
            raise NotValidGrid("Grid %s contains some non words in the list %s" % (str(new_grid), str(new_grid.words)))

        return new_grid


def alternate_dir_pos(length):
    for n in range(0, length, LINES_STEP):
        yield (0, n), VERTICAL
        yield (n, 0), HORIZONTAL


def maximize_step(grid, words, pos=None, direction=None):
    for word_length in range(grid.length, 1, -1):
        proto = grid.get_prototype(pos, direction, word_length)
        proto_gen = words.longest_prototype(proto, limit=word_length)
        # TODO: if we get a word which is not the full length try to
        # fit something else in
        while True:
            try:
                next_matching = proto_gen.next()
            except StopIteration:
                break
            else:
                try:
                    # need to find a word that fits!
                    return grid.place_word(next_matching, pos, direction)
                except NotValidGrid:
                    continue


def loop_solutions(words):
    old_grid = Grid(words)
    with open(RESULTS, 'a') as res:
        for pos, direction in alternate_dir_pos(old_grid.length):
            next_grid = maximize_step(old_grid, words, pos, direction)
            if next_grid is None:
                break

            msg = "{} total chars:\n{}".format(next_grid.tot_chars, next_grid)
            after = "{} total words = {}\n".format(len(next_grid.words), next_grid.words)
            print(msg)
            print(after)
            if next_grid.tot_chars >= 70:
                print("Got a wonderful result")
                res.write(msg + '\n')

            old_grid = next_grid


def main():
    words = Words(randomize=True)
    # for n in range(100):
    loop_solutions(words)


if __name__ == '__main__':
    main()
