from __future__ import division

import argparse
import re

from collections import defaultdict, Counter
from copy import deepcopy
from functools import reduce
from itertools import groupby, chain
from random import random
from string import ascii_lowercase

LINES_STEP = 2
# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 10
EMPTY = ' '

DICTS_FILE = ['british']# 'cracklib-small']
RESULTS = 'results.txt'

VERTICAL = 'V'
HORIZONTAL = 'H'


class InvalidCellSet(Exception): pass
class NotValidGrid(Exception): pass


class Words(object):
    """Class encapsulating the words, to make it easier to manipulate
    them
    """
    def __init__(self, dictfiles=DICTS_FILE, randomize=False, most_common_strategy=False):
        self.most_common_strategy = most_common_strategy
        self.dict = self._init_dict(dictfiles)
        self.dict_per_length = self.match_length()
        self.most_common = dict(self.most_common_chars())
        self.tot_chars = sum(self.most_common.values())
        self.randomize = randomize

    def _init_dict(self, dictfiles):
        dic = set()
        for dicf in dictfiles:
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
        res = len(word)
        if self.most_common_strategy:
            res *= self.rank_word(word)

        if self.randomize:
            res *= random()

        return res

    def longest_prototype(self, prototype, limit):
        """Generator that yields the words that maximize the ranking
        function
        """
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


def alternate_dir_pos(length, lines_step):
    for n in range(0, length, lines_step):
        yield (0, n), VERTICAL
        yield (n, 0), HORIZONTAL


def maximize_step(grid, words, pos=None, direction=None):
    max_length = grid.max_length(pos, direction)
    for word_length in range(max_length, 1, -1):
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


def loop_solutions(words, grid, lines_step):
    old_grid = grid
    with open(RESULTS, 'a') as res:
        for pos, direction in alternate_dir_pos(old_grid.length, lines_step):
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Crossword')
    parser.add_argument('-l', '--skip_n_lines', default=LINES_STEP, type=int)
    parser.add_argument('-g', '--grid_size', default=GRID_SIZE, type=int)
    parser.add_argument('-r', '--randomize', action='store_true')
    parser.add_argument('-m', '--most_common_strategy', action='store_true')

    return parser.parse_args()


def main():
    ns = parse_arguments()
    words = Words(randomize=ns.randomize, most_common_strategy=ns.most_common_strategy)
    grid = Grid(words, ns.grid_size)
    loop_solutions(words, grid, ns.skip_n_lines)


if __name__ == '__main__':
    main()
