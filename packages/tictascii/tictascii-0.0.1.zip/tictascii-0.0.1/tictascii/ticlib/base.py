from itertools import chain, cycle
import string
from tictascii.ticlib.exceptions import MarkerExists, MarkerOutOfRange


class Board(object):
    DIMENSIONS = 3

    def __init__(self):
        self.player_moves = self._get_none_matrix(self.DIMENSIONS)

    def __str__(self):
        return self._print_board(self.player_moves)

    def _print_board(self, matrix):
        ROW_WIDTH = 7
        COLUMN_SEPARATOR = u"|"
        ROW_SEPARATOR = u"-"

        # Create a horizontal line to separate rows.
        row = (ROW_SEPARATOR * ROW_WIDTH for _ in xrange(self.DIMENSIONS))
        horizontal_line = u"+".join(row)

        # Create a list of strings, one for each row.
        row_strings = []
        for x in xrange(self.DIMENSIONS):

            # Create a list of cell strings, one for each column.
            column_strings = []
            for y in xrange(self.DIMENSIONS):
                marker = matrix[x][y]
                cell_value = marker if marker else "({0},{1})".format(x, y)
                padded_cell_string = string.center(cell_value, ROW_WIDTH)
                column_strings.append(padded_cell_string)

            # Add a horizontal line in front of each row, for all but the
            # first line.
            is_first_row = x > 0
            if is_first_row:
                row_strings.append(horizontal_line)

            # Join columns by their separators to generate the final row
            # string.
            row_string = COLUMN_SEPARATOR.join(column_strings)
            row_strings.append(row_string)

        return u"\n".join(row_strings)

    def _get_rows(self, matrix):
        return matrix

    def _get_columns(self, matrix):
        for colno in xrange(self.DIMENSIONS):
            yield [matrix[i][colno] for i in xrange(self.DIMENSIONS)]

    def _get_none_matrix(self, dimensions):
        """
        Returns an NxN list of lists with values initialized to `None`,
        where N is the provided `dimensions`.
        """
        get_none_row = lambda length: [None for _ in range(length)]
        return [get_none_row(dimensions) for _ in range(dimensions)]

    def _get_winning_marker(self, matrix):
        """
        Returns the winning marker for a given board matrix if a winner
        exists for the matrix, otherwise `None`.  A winner is defined is
        someone who has a marker across the entire board matrix.
        """
        matrix_indices = range(self.DIMENSIONS)

        # Create a list of marker 3-sequences
        sequences = []
        sequences.extend(self._get_rows(matrix))
        sequences.extend(self._get_columns(matrix))

        # Diagonal li from top-left to bottom-right.
        sequences.append((matrix[i][i] for i in matrix_indices))

        # Diagonal line from bottom-left to top-right.
        sequences.append((matrix[i][(self.DIMENSIONS - 1) - i]
                          for i in matrix_indices))

        # Check whether there's any winning sequence by going through all
        # possible sequences and determining whether they only consist of
        # a single marker.
        for sequence in sequences:
            try:
                [winning_marker] = set(sequence)  # set removes duplicates
            except ValueError:  # unpacking error if not exactly 1 marker
                pass  # just move on to the next sequence
            else:
                # don't consider `None` sequences as winners
                if winning_marker:
                    return winning_marker

    def _is_game_over(self, matrix):
        """
        Returns `True` if the game is over, either because all rows have been
        filled (a tie), or because there is a winning marker.
        """
        rows = self._get_rows(matrix)
        if all(chain.from_iterable(rows)):
            return True

        if self._get_winning_marker(matrix):
            return True

    @property
    def is_game_over(self):
        return self._is_game_over(self.player_moves)

    def get_winning_marker(self):
        return self._get_winning_marker(self.player_moves)

    def set_marker(self, marker, x, y):
        """
        Set the position (x, y) to `marker` and check for errors.

        Raises:
            MarkerOutOfRange -- if the `x` and `y` given are invalid
            MarkerExists -- if there's already a marker at this location
        """
        try:
            current_mark = self.player_moves[x][y]
        except IndexError:
            raise MarkerOutOfRange("This marker doesn't fit on the board.")
        else:
            if current_mark:
                raise MarkerExists("This marker already exists.")
            self.player_moves[x][y] = marker


class Tournament(object):
    """
    A tournament tracks statistics over a number of games and is
    responsible for running the main game loop, `play_game`.
    """

    def __init__(self, player1, player2):
        self.players = (player1, player2)

    def _get_player_by_marker(self, marker):
        """
        Returns the player using a given marker.  Raises `ValueError` if
        that doesn't happen to be exactly one player.
        """
        [player] = [p for p in self.players if p.marker == marker]
        return player

    def _get_winner_or_none(self, winning_marker):
        """
        Returns the winner of a game given a `winning_marker` or `None` if the
        game was a tie.
        """
        if winning_marker:
            winner = self._get_player_by_marker(winning_marker)
            winner.increment_wins()
            return winner
        return

    def play_game(self):
        """
        Plays a game.  Returns a `Player` instance for the winner unless
        the game was a tie; in that case, returns `None`.  The wins for
        the winning player are incremented.
        """
        board = Board()
        for next_player in cycle(self.players):
            next_player.make_a_move(board)
            if board.is_game_over:
                winning_marker = board.get_winning_marker()
                return self._get_winner_or_none(winning_marker)
