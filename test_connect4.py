

import unittest
import numpy as np
from connect4 import create_board, drop_piece, is_valid_location, get_next_open_row, winning_move, PLAYER_ONE, \
    PLAYER_TWO, EMPTY


class TestConnect4(unittest.TestCase):

    def setUp(self):
        self.board = create_board()

    def test_create_board(self):
        self.assertTrue((self.board == np.zeros((6, 7), dtype=int)).all())

    def test_drop_piece(self):
        drop_piece(self.board, 0, 0, PLAYER_ONE)
        self.assertEqual(self.board[0][0], PLAYER_ONE)

    def test_is_valid_location(self):
        self.assertTrue(is_valid_location(self.board, 0))
        for row in range(6):
            drop_piece(self.board, row, 0, PLAYER_ONE)
        self.assertFalse(is_valid_location(self.board, 0))

    def test_get_next_open_row(self):
        row = get_next_open_row(self.board, 0)
        self.assertEqual(row, 0)
        drop_piece(self.board, 0, 0, PLAYER_ONE)
        row = get_next_open_row(self.board, 0)
        self.assertEqual(row, 1)

    def test_winning_move(self):
        for col in range(4):
            drop_piece(self.board, 0, col, PLAYER_ONE)
        self.assertTrue(winning_move(self.board, PLAYER_ONE))


if __name__ == "__main__":
    unittest.main()

