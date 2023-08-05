from itertools import chain
import unittest

from tictascii.ticlib.base import Board, Tournament
from tictascii.ticlib.exceptions import MarkerOutOfRange, MarkerExists
from tictascii.ticlib.players import ComputerPlayer, HumanPlayer, Player


class BoardTest(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.player = ComputerPlayer('X')

    def testBoardToString(self):
        self.board.player_moves = [
            ['X', 'O', 'X'],
            ['X', None, 'X'],
            ['X', 'X', 'O'],
        ]

        self.assertEqual(str(self.board), (
            "   X   |   O   |   X   \n"
            "-------+-------+-------\n"
            "   X   | (1,1) |   X   \n"
            "-------+-------+-------\n"
            "   X   |   X   |   O   "
        ))

    def testInitialMatrix(self):
        self.assertEquals(self.board._get_none_matrix(3), [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ])

    def testHorizontalWinningMarker(self):
        self.assertEquals('X', self.board._get_winning_marker([
            ['X', 'X', 'X'],
            [None, None, None],
            [None, None, None],
        ]))

    def testVerticalWinningMarker(self):
        self.assertEquals('O', self.board._get_winning_marker([
            ['O', None, None],
            ['O', None, None],
            ['O', None, None],
        ]))

    def testDownRightDiagonalWinningMarker(self):
        self.assertEquals('O', self.board._get_winning_marker([
            ['O', None, None],
            [None, 'O', None],
            [None, None, 'O'],
        ]))

    def testDownLeftDiagonalWinningMarker(self):
        self.assertEquals('X', self.board._get_winning_marker([
            [None, None, 'X'],
            [None, 'X', None],
            ['X', None, None],
        ]))

    def testNoWinningMarker(self):
        self.assertEquals(None, self.board._get_winning_marker([
            ['O', 'O', 'X'],
            ['X', None, 'X'],
            ['X', 'X', 'O'],
        ]))

    def testSetMarkerOutOfRange(self):
        with self.assertRaises(MarkerOutOfRange):
            self.board.set_marker(self.player.marker, 4, 1)

    def testSetMarkerExists(self):
        set_marker = lambda: self.board.set_marker(self.player.marker, 2, 1)

        set_marker()
        with self.assertRaises(MarkerExists):
            set_marker()


class PlayerTest(unittest.TestCase):

    def setUp(self):
        self.player = Player('O')

    def testInitialPlayer(self):
        self.assertEquals(self.player.games_won, 0)

    def testIncrementWins(self):
        self.player.increment_wins()
        self.assertEquals(self.player.games_won, 1)

    def testGamesWon(self):
        self.assertEquals(self.player.games_won, 0)

    def testMakeAMoveAsUnimplemented(self):
        board = Board()
        with self.assertRaises(NotImplementedError):
            self.player.make_a_move(board)


class HumanPlayerTest(unittest.TestCase):

    def setUp(self):
        self.player = HumanPlayer('O')


class ComputerPlayerTest(unittest.TestCase):

    def setUp(self):
        self.player = ComputerPlayer('O')
        self.board = Board()

    def testMakeAMove(self):
        marker = self.player.marker
        flatten = chain.from_iterable

        moves = flatten(self.board.player_moves)
        self.assertFalse(marker in moves)

        self.player.make_a_move(self.board)

        moves = flatten(self.board.player_moves)
        self.assertTrue(marker in moves)


class TournamentTest(unittest.TestCase):
    def setUp(self):
        self.player1 = ComputerPlayer('X')
        self.player2 = ComputerPlayer('O')
        self.players = (self.player1, self.player2)
        self.tournament = Tournament(self.players)

    def testPlayedGameEnds(self):
        winner = None
        while not winner:
            winner = self.tournament.play_game()
        self.assertEquals(1, winner.games_won)

    def testGetWinnerOrNone(self):
        self.assertIs(self.tournament._get_winner_or_none(None), None)
        self.assertIs(self.tournament._get_winner_or_none('O'),
                      self.player2)
