import unittest

import square_words as square


class TestSquareWords(unittest.TestCase):
    def test_is_valid_word(self):
        self.assertTrue(square.is_valid_word("valid"))
        self.assertTrue(not square.is_valid_word("ndfkjlk"))

    def test_count_chars_empty_grid(self):
        grid = square.Grid()
        self.assertEqual(grid.tot_chars, 0)
        self.assertEqual(grid.empty, 64)

    def test_set_value_in_grid_line_only_modifies_cell(self):
        grid = square.Grid()
        grid[0][0] = 'A'
        self.assertEqual(grid[0][1], square.EMPTY)
        self.assertEqual(grid[1][0], square.EMPTY)

    def test_grid_with_values(self):
        grid = square.Grid()
        grid[0][0] = 'A'
        self.assertEqual(grid.tot_chars, 1)

    def test_lines_columns(self):
        grid = square.Grid()
        grid[0][0] = 'A'
        grid[0][1] = 'B'
        first_line = list(grid.lines())[0]
        self.assertEqual(first_line[1], 'B')
        first_col = list(grid.columns())[0]
        self.assertEqual(first_col[1], square.EMPTY)

    def test_words_in_line(self):
        line = [square.EMPTY, square.EMPTY, 'B', 'A', square.EMPTY, 'C', 'B', 'A']
        words = ['BA', 'CBA']
        self.assertEqual(square.words_in_line(line), words)

        line_two = ['A', 'C', square.EMPTY, square.EMPTY]
        self.assertEqual(square.words_in_line(line_two), ['AC'])

    def test_words_in_grid(self):
        grid = square.Grid()
        grid[0][0] = 'A'
        grid[0][1] = 'B'
        grid[1][0] = 'C'
        desired = ['AB', 'AC']
        self.assertEqual(grid.words, desired)

    def test_placing_too_big_word(self):
        grid = square.Grid(3)
        with self.assertRaises(AssertionError):
            grid.place_word('VERYLONG')

    def test_check_grid(self):
        grid = square.Grid(3)
        grid[0][0] = 'A'
        grid[0][1] = 'B'
        self.assertTrue(not grid.is_valid())
