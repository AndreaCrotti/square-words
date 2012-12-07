__metaclass__ = type
import string

# might be a nice javascript application to test out the various possibilities
GRID_SIZE = 8

DICT_FILE = 'cracklib-small'
# if the dictionary is not too small it can be simply loaded up-front
DICT = set(x.strip() for x in open(DICT_FILE))
CHARS = string.ascii_uppercase


def is_valid_word(word):
    return word in DICT


class Grid:
    def __init__(self, length=GRID_SIZE):
        self.length = length
        self.grid = []
        for _ in range(self.length):
            self.grid.append([None] * self.length)

    def __getitem__(self, item):
        return self.grid[item]

    def lines(self):
        return iter(self.grid[:])

    def columns(self):
        for n in range(self.length):
            yield [self.grid[i][n] for i in range(self.length)]

    @property
    def chars(self):
        res = 0
        for line in self.grid:
            for val in line:
                if (val is not None) and (val in CHARS):
                    res += 1

        return res

    @property
    def empty(self):
        return self.length ** 2
