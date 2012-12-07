import unittest

import square_words as square


class TestSquareWords(unittest.TestCase):
    def test_is_valid_word(self):
        self.assertTrue(square.is_valid_word("valid"))
        self.assertTrue(not square.is_valid_word("ndfkjlk"))
