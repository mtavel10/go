import sys
from random import randrange, choice
from typing import Optional, Callable
import click
from base import GoBase
from fakes import GoStub, GoFake
from go import Go


## Bot Strategies ##

def random_move(base: GoBase) -> Optional[tuple[int, int]]: 
    """
    Chooses a move randomly
    """
    moves: list[Optional[tuple[int, int]]] = base.available_moves
    # if (0, 0) in moves: 
    #     moves.remove((0, 0))
    moves.append(None) # The random bot can pass
    return choice(moves)

def minimax_move(base: GoBase) -> Optional[tuple[int, int]]: 
    """
    Chooses the move with the highest average number of pieces on the board,
    based on possible moves their opponent can make next. 
    Returns None if passed. 
    """
    max_value: int = 0
    best_move: Optional[tuple[int, int]] = None

    available_moves: list[Optional[tuple[int, int]]]= base.available_moves
    # if (0, 0) in available_moves: 
    #     available_moves.remove((0, 0))
    available_moves.append(None)

    for move in available_moves: 

        simulated_base: GoBase = base.simulate_move(move)

        # Possible moves that the opponent can make as a result of applying this move
        next_m: list[tuple[int, int]] = simulated_base.available_moves
        # if (0, 0) in next_m: 
        #     next_m.remove((0, 0))

        # Average number of pieces on the board (for the player) after each opponent move
        value_m: int = 0
        for op_move in next_m:
            next_simulated_base: GoBase = simulated_base.simulate_move(op_move)
            if base.turn != -1: 
                value_m += next_simulated_base.scores()[base.turn]
        
        # Case where applying this move would end the game (opponent has no available moves)
        if len(next_m) == 0: 
            return move
        else: 
            value_m /= len(next_m)

        if value_m > max_value: 
            max_value = value_m
            best_move = move
    
    return best_move
    


## Strategy Implementation ##

def bot_battle(board_size: int, 
               num_games: int, 
               p1_strategy: Callable[[GoBase], Optional[tuple[int, int]]], 
               p2_strategy: Callable[[GoBase], Optional[tuple[int, int]]]) -> list[int]: 
    """
    This method simulates a specified number of games between two bots

    Inputs
        board_size (int): the size of the board
        num_games (int): the number of games played
    
    Returns
        outcome_tally (list[int]): A list of ints where the 0th element 
        represents the number of total moves made. 
        The next element is the number of ties. 
        Subsequent elements represent the number of wins per player. 
    """
    outcome_tally: list[int] = [0, 0, 0, 0]

    for i in range(num_games):
        game = Go(board_size, 2)
        total_moves = 0

        while not game.done:
            move1 = p1_strategy(game)
            game.apply_move(move1)  # Bot 1 moves
            move2 = p2_strategy(game)
            game.apply_move(move2)   # Bot 2 moves

            if move1 is None and move2 is None: 
                break

            total_moves+= 2
            if total_moves >= 256: 
                game.pass_turn()
                game.pass_turn()
        
        outcome_tally[0] += total_moves

        outcome: list[int] = game.outcome
        if outcome == [1, 2]: # A tie
            outcome_tally[1] += 1
        if outcome == [1]: # Player 1 wins
            outcome_tally[2] += 1
        if outcome == [2]: # Player 2 wins
            outcome_tally[3] += 1
    
    return outcome_tally


@click.command()
@click.option("-n", "--num-games", type = click.INT, default = 20)
@click.option("-s", "--size", type = click.INT, default = 6)
@click.option("-1", "--player1", type = click.Choice(["smart", "random"]), default = "random")
@click.option("-2", "--player2", type = click.Choice(["smart", "random"]), default = "random")
def cmd(num_games, size, player1, player2):
    STRATEGY1: Callable[[GoBase], Optional[tuple[int, int]]]
    STRATEGY2: Callable[[GoBase], Optional[tuple[int, int]]]

    if player1 == "random": 
        STRATEGY1 = random_move
    elif player1 == "smart": 
        STRATEGY1 = minimax_move
    else:
        raise ValueError
    
    if player2 == "random": 
        STRATEGY2 = random_move
    elif player2 == "smart":
        STRATEGY2 = minimax_move
    else: 
        raise ValueError
    
    results: list[int] = bot_battle(size, num_games, STRATEGY1, STRATEGY2)

    print("Player 1 wins: " + f"{results[2]/ num_games:.2%}")
    print("Player 2 wins: " + f"{results[3] / num_games:.2%}")
    print("Ties: " + f"{results[1] / num_games:.2%}")
    print("Average moves: " + f"{results[0] / num_games}")
    

if __name__ == "__main__": 
    cmd()