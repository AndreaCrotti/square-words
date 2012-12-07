import unittest

import square_words as square


class TestSquareWords(unittest.TestCase):
    def test_is_valid_word(self):
        self.assertTrue(square.is_valid_word("valid"))
        self.assertTrue(not square.is_valid_word("ndfkjlk"))

    def test_count_chars_empty_grid(self):
        grid = square.Grid()
        self.assertEqual(grid.chars, 0)
        self.assertEqual(grid.empty, 64)

    def test_grid_with_values(self):
        grid = square.Grid()
        grid[0][0] = 'A'
        self.assertEqual(grid.chars, 1)
