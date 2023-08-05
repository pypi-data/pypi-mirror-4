from ticlib.players import HumanPlayer, ComputerPlayer
from ticlib.base import Tournament, Board
from ticli import get_participating_players

import unittest


def one_raw_input(prompt):
    return "1"


def two_raw_input(prompt):
    return "2"


class MainTest(unittest.TestCase):

    def test_getting_1_players(self):
        player_collection = get_participating_players(one_raw_input)
        self.assertNotEqual(player_collection, None)

    def test_getting_2_players(self):
        player_collection = get_participating_players(two_raw_input)
        self.assertNotEqual(player_collection, None)

    def test_if_1_player_have_correct_marks(self):
        player_collection = get_participating_players(one_raw_input)
        player_1 = player_collection[0]
        player_2 = player_collection[1]
        self.assertEquals('X', player_1.marker)
        self.assertEquals('O', player_2.marker)

    def test_if_2_player_have_correct_marks(self):
        player_collection = get_participating_players(two_raw_input)
        player_1 = player_collection[0]
        player_2 = player_collection[1]
        self.assertEquals('X', player_1.marker)
        self.assertEquals('O', player_2.marker)

    def test_if_1_player_instances_of_correct_type(self):
        player_collection = get_participating_players(one_raw_input)
        player_1 = player_collection[0]
        player_2 = player_collection[1]
        assert isinstance(player_1, HumanPlayer)
        assert isinstance(player_2, ComputerPlayer)

    def test_if_1_player_instances_of_correct_type(self):
        player_collection = get_participating_players(two_raw_input)
        player_1 = player_collection[0]
        player_2 = player_collection[1]
        assert isinstance(player_1, HumanPlayer)
        assert isinstance(player_2, HumanPlayer)
