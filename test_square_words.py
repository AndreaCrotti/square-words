import unittest

import square_words as square


class TestSquareWords(unittest.TestCase):
    def setUp(self):
        self.grid = square.Grid()

    def test_count_chars_empty_grid(self):
        self.assertEqual(self.grid.tot_chars, 0)
        self.assertEqual(self.grid.empty, 100)

    def test_count_chars_not_empty_grid(self):
        self.grid[0][1] = 'a'
        self.assertEqual(self.grid.tot_chars, 1)
        self.assertEqual(self.grid.empty, 99)

    def test_set_value_in_grid_line_only_modifies_cell(self):
        self.grid[0][0] = 'a'
        self.assertEqual(self.grid[0][1], square.EMPTY)
        self.assertEqual(self.grid[1][0], square.EMPTY)

    def test_grid_with_values(self):
        self.grid[0][0] = 'a'
        self.assertEqual(self.grid.tot_chars, 1)

    def test_lines_columns(self):
        self.grid[0][0] = 'a'
        self.grid[0][1] = 'b'
        first_line = list(self.grid.lines())[0]
        self.assertEqual(first_line[1], 'b')
        first_col = list(self.grid.columns())[0]
        self.assertEqual(first_col[1], square.EMPTY)

    def test_words_in_line(self):
        line = [square.EMPTY, square.EMPTY, 'b', 'a', square.EMPTY, 'c', 'b', 'a']
        words = ['ba', 'cba']
        self.assertEqual(square.words_in_line(line), words)

        line_two = ['a', 'c', square.EMPTY, square.EMPTY]
        self.assertEqual(square.words_in_line(line_two), ['ac'])

    def test_words_in_grid(self):
        self.grid[0][0] = 'a'
        self.grid[0][1] = 'b'
        self.grid[1][0] = 'c'
        desired = ['ab', 'ac']
        self.assertEqual(self.grid.words, desired)

    def test_placing_too_big_word(self):
        with self.assertRaises(AssertionError):
            self.grid.place_word('verylongveryvery')

    def test_placing_word_vertical(self):
        new_grid = self.grid.place_word('aaa', pos=(1, 0), direction=square.VERTICAL)
        # check that the old grid is not touched
        self.assertEqual(self.grid[1][0], square.EMPTY)
        self.assertEqual(new_grid[1][0], 'a')
        self.assertEqual(new_grid[2][0], 'a')
        self.assertTrue(new_grid.is_valid(square.Words()))

    def test_placing_word_twice(self):
        new_grid = self.grid.place_word('aaa', pos=(1, 0), direction=square.VERTICAL)
        with self.assertRaises(square.InvalidCellSet):
            new_grid.place_word('bbb', (1, 0), direction=square.HORIZONTAL)

    def test_get_prototype_function(self):
        self.grid[0][0] = 'a'
        self.grid[0][2] = 'a'
        self.assertEqual(self.grid.get_prototype((0, 0), square.HORIZONTAL, 8), 'a a     ')

    def test_check_grid(self):
        self.grid[0][0] = 'a'
        self.grid[0][1] = 'b'
        self.assertTrue(not self.grid.is_valid(square.Words()))

    def test_string_list_to_grid(self):
        tr = ["r cecar"] * 8
        grid = square.Grid.grid_from_string_list(tr)
        self.assertEqual(grid[0][1], square.EMPTY)

    def test_position_and_direction_give_right_coordinates(self):
        desired = [(0, 0), (0, 1), (0, 2)]
        got = square.cell_pos(pos=(0, 0), direction=square.HORIZONTAL, length=3)
        self.assertListEqual(list(got), desired)
        des_vert = [(1, 1), (2, 1), (3, 1)]
        got = square.cell_pos(pos=(1, 1), direction=square.VERTICAL, length=3)
        self.assertListEqual(list(got), des_vert)


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

    def test_get_longest_prototype(self):
        to_match = 'aberdeen'
        lg_gen = self.words.longest_prototype('a er ee ', limit=8)
        self.assertEqual(lg_gen.next(), to_match)

    def test_matching_length(self):
        res = list(self.words.length_word(3))
        self.assertEqual(res[0], 'dna')


class TestMaximizeProblem(unittest.TestCase):
    def test_more_words_placed_increase_the_count(self):
        gr1 = square.Grid()
        gr2 = gr1.place_word('racecar')
        self.assertTrue(gr2.tot_chars > gr1.tot_chars)
        self.assertTrue(gr2.is_valid)
        gr3 = gr2.place_word('racecar', pos=(0, 4))
        self.assertTrue(gr3.tot_chars > gr2.tot_chars)

    def test_maximize_function_returns_a_better_grid(self):
        grid = square.Grid()
        words = square.Words()
        ng = square.maximize_step(grid, words, (0, 0), direction=square.HORIZONTAL)
        self.assertEqual(ng.tot_chars, 10)

    def test_alternate_positions(self):
        desired = [((0, 0), square.VERTICAL),
                   ((0, 0), square.HORIZONTAL),
                   ((0, 2), square.VERTICAL),
                   ((2, 0), square.HORIZONTAL)]

        self.assertListEqual(list(square.alternate_dir_pos(3)), desired)
