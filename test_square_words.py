import unittest

import square_words as square


class TestSquareWords(unittest.TestCase):
    def test_count_chars_empty_grid(self):
        grid = square.Grid()
        self.assertEqual(grid.tot_chars, 0)
        self.assertEqual(grid.empty, 64)

    def test_set_value_in_grid_line_only_modifies_cell(self):
        grid = square.Grid()
        grid[0][0] = 'a'
        self.assertEqual(grid[0][1], square.EMPTY)
        self.assertEqual(grid[1][0], square.EMPTY)

    def test_grid_with_values(self):
        grid = square.Grid()
        grid[0][0] = 'a'
        self.assertEqual(grid.tot_chars, 1)

    def test_lines_columns(self):
        grid = square.Grid()
        grid[0][0] = 'a'
        grid[0][1] = 'b'
        first_line = list(grid.lines())[0]
        self.assertEqual(first_line[1], 'b')
        first_col = list(grid.columns())[0]
        self.assertEqual(first_col[1], square.EMPTY)

    def test_words_in_line(self):
        line = [square.EMPTY, square.EMPTY, 'b', 'a', square.EMPTY, 'c', 'b', 'a']
        words = ['ba', 'cba']
        self.assertEqual(square.words_in_line(line), words)

        line_two = ['a', 'c', square.EMPTY, square.EMPTY]
        self.assertEqual(square.words_in_line(line_two), ['ac'])

    def test_words_in_grid(self):
        grid = square.Grid()
        grid[0][0] = 'a'
        grid[0][1] = 'b'
        grid[1][0] = 'c'
        desired = ['ab', 'ac']
        self.assertEqual(grid.words, desired)

    def test_placing_too_big_word(self):
        grid = square.Grid(3)
        with self.assertRaises(AssertionError):
            grid.place_word('verylong')

    def test_placing_word_vertical(self):
        grid = square.Grid(5)
        new_grid = grid.place_word('aaa', pos=(1, 0), direction=square.VERTICAL)
        # check that the old grid is not touched
        self.assertEqual(grid[1][0], square.EMPTY)
        self.assertEqual(new_grid[1][0], 'a')
        self.assertEqual(new_grid[2][0], 'a')
        self.assertTrue(new_grid.is_valid(square.Words()))

    def test_placing_word_twice(self):
        grid = square.Grid(5)
        new_grid = grid.place_word('aaa', pos=(1, 0), direction=square.VERTICAL)
        with self.assertRaises(AssertionError):
            new_grid.place_word('bbb', (1, 0), direction=square.HORIZONTAL)

    def test_check_grid(self):
        grid = square.Grid(3)
        grid[0][0] = 'a'
        grid[0][1] = 'b'
        self.assertTrue(not grid.is_valid(square.Words()))

    def test_empty_cells(self):
        grid = square.Grid(3)
        gen = grid.empty_cells()
        self.assertEqual(gen.next(), (0, 0))

    def test_string_list_to_grid(self):
        tr = ["r cecar"] * 8
        grid = square.Grid.grid_from_string_list(tr)
        self.assertEqual(grid[0][1], square.EMPTY)


class TestWords(unittest.TestCase):
    def setUp(self):
        self.words = square.Words()

    def test_simple_word_found(self):
        self.assertTrue('aaa' in self.words)

    def test_get_words_match_prototypes(self):
        # find word 'aberdeen'
        to_find = 'a er ee '
        all_an = self.words.match_prototype(to_find)
        self.assertTrue('aberdeen' in all_an)
        self.assertEqual(len(all_an), 1)

    def test_matching_length(self):
        res = list(self.words.length_word(3))
        self.assertEqual(res[0], 'dna')
