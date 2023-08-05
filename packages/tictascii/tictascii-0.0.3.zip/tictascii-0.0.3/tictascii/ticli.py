#!/usr/bin/env python

from tictascii.ticlib.players import HumanPlayer, ComputerPlayer
from tictascii.ticlib.base import Tournament, Board


def get_participating_players(raw_input=raw_input):
    """
   Allows the user to select number of human players.
   Validates input and returns a matching tuple of players.
   """
    no_players = 0
    while no_players != 1 and no_players != 2:
        inp = raw_input("Single player or multiplayer? (1/2): ")
        try:
            no_players = int(inp)
        except ValueError:
            print "Invalid input - please try again"
            pass

    if no_players is 1:
        return (HumanPlayer('X'), ComputerPlayer('O'))
    else:
        return (HumanPlayer('X'), HumanPlayer('O'))


def print_results(player_collection):
    print "Thanks for playing."
    for player in player_collection:
        print "Player", player.marker, "won", player.games_won, "games."


def main(raw_input=raw_input):
    player_collection = get_participating_players()
    tournament = Tournament(player_collection)
    wants_another_game = "y"

    while wants_another_game == "y":
        winner = tournament.play_game()
        try:
            winning_marker = winner.marker
            print "The winner is player", winning_marker
        except:
            print "The game is a tie! Everybody wins!"
        wants_another_game = raw_input("Another game? (y for yes):")

    print_results(player_collection)


if __name__ == "__main__":
    main()
