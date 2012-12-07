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
    def __init__(self):
        pass

    def count_chars(self):
        return 0
