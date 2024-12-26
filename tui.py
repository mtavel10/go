from typing import Optional

import click

from go import Go
from board import Board
from bot import minimax_move

def print_board(grid: list[list[Optional[int]]], num_players: int):
    """
    Prints the state of the board as a grid of strings.

    Returns [str]
    """
    nrows: int = len(grid)
    ncols: int = len(grid[0])

    crow: str = ""
    for r in range(nrows):
        for c in range(ncols):
            v = grid[r][c]

            if v is not None: #adding player piece or middle board piece
                if c != 0:
                    crow += "-"
                for i in range(0, num_players+1):
                    if v == i:
                        crow += str(i)
                if c == ncols -1:
                    crow += "\n"

            elif r == 0: #top edge piece
                if c == 0:
                    crow += "┌"
                elif c == ncols-1:
                    crow += "─┐\n"
                else:
                    crow += "─┬"

            elif r == nrows-1: #bottom edge piece
                if c == ncols-1:
                    crow += "─┘\n"
                elif c == 0:
                    crow += "└"
                else:
                    crow += "─┴"

            elif c == 0: #left edge piece
                crow += "├"

            elif c == ncols-1: #right edge piece
                crow += "─┤\n"

            else:
                crow += "─┼"

    return crow

def go_game_initiator(num_players, size, super_ko):
    """
    Initialises the go game board by taking inputs from click commands.
    """
    go_game: Go = Go(size, num_players, super_ko)
    colors: dict[int, str] = {1:"Player 1", 2:"Player 2", 3:"Player 3", \
                              4:"Player 4", 5:"Player 5", 6:"Player 6", \
                                7:"Player 7", 8:"Player 8", 9:"Player 9"}

    print(print_board(go_game.grid, num_players))

    while not go_game.done:
        print(f"It is {colors[go_game.turn]}'s turn. Please enter a move " \
            f"[press Enter to pass]:")
        user_command = input("> ")

        #Additional Enhancement: Bot provides hint upon typing hint
        if user_command == "hint":
            print(f"Try this move: {minimax_move(go_game)}")
            continue

        #If a player passes (no input)
        if user_command == "":
            print(f"{colors[go_game.turn]} has passed their turn")
            go_game.pass_turn()
            if go_game._passes == num_players:
                print("Game Over! All players passed their turn.")
                print(f"Scores: {go_game.scores()}")

                str_outcomes: list[str] = [str(player) for player in \
                                           go_game.outcome]
                if len(str_outcomes) == 1:
                    print(f"The winner is Player {str_outcomes[0]}")
                else:
                    winners = " and ".join(str_outcomes)
                    print(f"The winners are Player's {winners}")
            continue

        #If a player enters a position on board
        inputs = user_command.split()
        row: int = int(inputs[0])
        col: int = int(inputs[1])

        if not go_game.legal_move((row, col)):
            print("Error: Invalid move") #checks valid move to provide error
        else:
            go_game.apply_move((row, col))

        print(print_board(go_game.grid, num_players))

@click.command(name="go-tui")
@click.option("-n", "--num-players", default = 2, help = 'Number of players.')
@click.option("-s", "--size", default = 19, help = "Board size.")
@click.option("--simple-ko/--super-ko", default = False, \
              help = "Simple or super ko mode")

def cmd(num_players, size, simple_ko):
    super_ko_mode: bool = False
    if not simple_ko:
        super_ko_mode = True #implements super ko mode
    go_game_initiator(num_players, size, super_ko_mode)

if __name__ == "__main__":
    cmd()
