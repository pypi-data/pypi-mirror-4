
import random
from tictascii.ticlib.exceptions import MarkerOutOfRange, MarkerExists


class Player(object):

    def __init__(self, marker):
        self.marker = marker
        self.games_won = 0

    def increment_wins(self):
        self.games_won += 1

    def get_wins(self):
        return self.games_won

    def make_a_move(self, board):
        raise NotImplementedError()


class HumanPlayer(Player):

    def make_a_move(self, board):
        while True:
            x = int(raw_input("X: "))
            y = int(raw_input("Y: "))

            try:
                board.set_marker(self.marker, x, y)
            except MarkerOutOfRange:
                print "The provided marker isn't within the board range."
            except MarkerExists:
                print "A marker has already been placed at this location."
            else:
                return


class ComputerPlayer(Player):

    def make_a_move(self, board):
        while True:
            x = random.randint(0, board.DIMENSIONS - 1)
            y = random.randint(0, board.DIMENSIONS - 1)

            try:
                board.set_marker(self.marker, x, y)
            except MarkerExists:
                pass  # just retry if there's already a marker here
            else:
                return
