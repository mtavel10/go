"""
Fake implementations of GoBase.

We provide a GoStub implementation, and you must
implement a GoFake implementation.
"""
from copy import deepcopy
from copy import copy
from abc import abstractmethod
from base import GoBase, BoardGridType, ListMovesType
from typing import Optional

from board import Board


class GoStub(GoBase):
    """
    Stub implementation of GoBase.

    This stub implementation behaves according to the following rules:

    - It only supports two players and boards of size 2x2 and above.

    - The board is always initialized with four pieces in the four
      corners of the board. Player 1 has pieces in the northeast and
      southwest corners of the board, and Player 2 has pieces in the
      southeast and northwest corners of the board.
    - Players are allowed to place pieces in any position of the board
      they want, even if there is already a piece in that position
      (placing a piece in such a position replaces the previous piece
      with the new one). The ko and superko rule do not apply.
    - The game ends after four moves. Whatever player has a piece in
      position (0,1) wins. If there is no piece in that position,
      the game ends in a tie.
    - The scores are always reported as 100 for Player 1 and 200 for
      Player 2. Note how the scores do not play a role in determining
      the outcome of the game.
    - It does not validate board positions. If a method is called with
      a position outside the board, the method will likely cause an exception.
    - It does not implement the load_game or simulate_moves method.
    """

    _grid: BoardGridType
    _turn: int
    _num_moves: int

    def __init__(self, side: int, players: int, superko: bool = False):
        """
        See GoBase.__init__
        """
        if players != 2:
            raise ValueError(
                "The stub implementation " "only supports two players"
            )

        super().__init__(side, players, superko)

        self._grid = [[None] * side for _ in range(side)]
        self._grid[0][-1] = 1
        self._grid[-1][0] = 1
        self._grid[0][0] = 2
        self._grid[-1][-1] = 2

        self._turn = 1
        self._num_moves = 0

    @property
    def grid(self) -> BoardGridType:
        """
        See GoBase.grid
        """
        return deepcopy(self._grid)

    @property
    def turn(self) -> int:
        """
        See GoBase.turn
        """
        return self._turn

    @property
    def available_moves(self) -> ListMovesType:
        """
        See GoBase.available_moves
        """
        moves = []
        for r in range(self._side):
            for c in range(self._side):
                moves.append((r, c))

        return moves

    @property
    def done(self) -> bool:
        """
        See GoBase.done
        """
        return self._num_moves == 4

    @property
    def outcome(self) -> list[int]:
        """
        See GoBase.outcome
        """
        if not self.done:
            return []

        if self._grid[0][1] is None:
            return [1, 2]
        else:
            return [self._grid[0][1]]

    def piece_at(self, pos: tuple[int, int]) -> int | None:
        """
        See GoBase.piece_at
        """
        r, c = pos
        return self._grid[r][c]

    def legal_move(self, pos: tuple[int, int]) -> bool:
        """
        See GoBase.legal_move
        """
        return True

    def apply_move(self, pos: tuple[int, int]) -> None:
        """
        See GoBase.apply_move
        """
        r, c = pos
        self._grid[r][c] = self._turn
        self.pass_turn()

    def pass_turn(self) -> None:
        """
        See GoBase.pass_turn
        """
        self._turn = 2 if self._turn == 1 else 1
        self._num_moves += 1

    def scores(self) -> dict[int, int]:
        """
        See GoBase.scores
        """
        return {1: 100, 2: 200}

    def load_game(self, turn: int, grid: BoardGridType) -> None:
        """
        See GoBase.load_game
        """
        raise NotImplementedError

    def simulate_move(self, pos: tuple[int, int] | None) -> "GoBase":
        """
        See GoBase.simulate_move
        """
        raise NotImplementedError


#
# Your GoFake implementation goes here
#
class GoFake(GoBase):
    
    _side: int
    _players: int
    _superko: bool
    _prev_boards: list[Board]
    _turn: int
    _board: Board
    _passes: int
    _game_over: bool

    def __init__(
        self,
        side: int,
        players: int,
        superko: bool = False,
    ):
        """
        Constructor

        Args:
            side: Number of squares on each side of the board
            players: Number of players
            superko: If True, the "super ko" rule is in effect:
            a move cannot result in any past state of the board.
            If False, the "simple ko" rule is in effect: a move
            cannot result in the immediately prior state of the
            board.
        """
        if side < 4: 
            raise ValueError
        if players != 2: 
            raise ValueError
        
        self._side = side
        self._players = players
        self._superko = superko
        self._turn = 1
        self._board = Board(side)
        self._passes = 0
        self._game_over = False
        self._prev_boards = [Board(side), Board(side)]
        
    
    # PROPERTIES
    #

    @property
    def size(self) -> int:
        """
        Returns the size of the board (the number of squares per side)
        """
        return self._side

    @property
    def num_players(self) -> int:
        """
        Returns the number of players
        """
        return self._players

    @property
    def grid(self) -> list[list[Optional[int]]]:
        """
        Returns the state of the game board as a list of lists.
        Each entry can either be an integer (meaning there is a
        piece at that location for that player) or None,
        meaning there is no piece in that location. Players are
        numbered from 1.
        """
        return self._board.to_grid()

    @property
    def turn(self) -> int:
        """
        Returns the player number for the player who must make
        the next move (i.e., "whose turn is it?")  Players are
        numbered from 1.

        If the game is over, this property will not return
        any meaningful value.
        """

        if self.done: 
            return -1
        else: 
            return self._turn

    @property
    def available_moves(self) -> ListMovesType:
        """
        Returns the list of positions where the current player
        (as returned by the turn method) could place a piece.

        If the game is over, this property will not return
        any meaningful value.
        """
        moves: list[tuple[int, int]] = []

        for row in range(self.size): 
            for col in range(self.size):
                if (self.legal_move((row, col)) and 
                    self._board.piece_at(row, col) is None): 
                    moves.append((row, col))
        
        return moves

    @property
    def done(self) -> bool:
        """
        Returns True if the game is over, False otherwise.
        """
        if self._passes == self._players:
            return True
        else:
            return self._game_over

    @property
    def outcome(self) -> list[int]:
        """
        Returns the list of winners for the game. If the game
        is not yet done, will return an empty list.
        If the game is done, will return a list of player numbers
        (players are numbered from 1). If there is a single winner,
        the list will contain a single integer. If there is a tie,
        the list will contain more than one integer (representing
        the players who tied)
        """
        winners: list[int] = []
        if not self.done: 
            return winners
        
        max_score: int = 0
        for player, score in self.scores().items(): 
            if score == max_score:
                winners.append(player)
            if score > max_score: 
                winners = [player]
                max_score = score

        return winners

    #
    # METHODS
    #
    
    def switch_turn(self) -> None: 
        if self._turn == 1:
            self._turn = 2
        else:
            self._turn = 1


    def piece_at(self, pos: tuple[int, int]) -> int | None:
        """
        Returns the piece at a given location

        Args:
            pos: Position on the board

        Raises:
            ValueError: If the specified position is outside
            the bounds of the board.

        Returns: If there is a piece at the specified location,
        return the number of the player (players are numbered
        from 1). Otherwise, return None.
        """
        return self._board.piece_at(pos[0], pos[1])
        


    def legal_move(self, pos: tuple[int, int]) -> bool:
        """
        Checks if a move is legal.

        Args:
            pos: Position on the board

        Raises:
            ValueError: If the specified position is outside
            the bounds of the board.

        Returns: If the current player (as returned by the turn
        method) could place a piece in the specified position,
        return True. Otherwise, return False.
        """
        row, col = pos

        temp_base: "GoBase"  = self.simulate_move(pos)

        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        if self.piece_at((row, col)) is not None:
            return False
        
        if self._superko:
            for prev in self._prev_boards:
                if prev == temp_base._board:
                    return False
        else: # otherwise we are in ko case
            if temp_base._board == self._prev_boards[0]:
                return False
        
        return True      


    def apply_move(self, pos: Optional[tuple[int, int]]) -> None:
        """
        Place a piece of the current player (as returned
        by the turn method) on the board.

        The provided position is assumed to be a legal
        move (as returned by available_moves, or checked
        by legal_move). The behaviour of this method
        when the position is on the board, but is not
        a legal move, is undefined.

        After applying the move, the turn is updated to the
        next player.

        Args:
            pos: Position on the board

        Raises:
            ValueError: If the specified position is outside
            the bounds of the board.

        Returns: None
        """
        if pos is None: 
            self.pass_turn()
            return 
        
        row, col = pos

        # Why did we have this? 
        # if self.done == True:
        #     raise ValueError
        
        if row == 0 and col == 0:
            self._board.place_piece(row, col, self._turn)
            self.game_over()
            return

        self._passes = 0
        self._board.place_piece(row, col, self._turn)
        self.capture(pos)

        curr_board: Board = Board(self._side)
        for i in range(self._side): 
            for j in range(self._side): 
                curr_board.place_piece(i, j, self._board.piece_at(i, j))
            
        if self._superko: 
            self._prev_boards.append(curr_board)
        else: # In the Ko case, we'll only store the most recent board
            prev_board = self._prev_boards[1]
            self._prev_boards[0] = prev_board
            self._prev_boards[1] = curr_board
        
        self.switch_turn()

    def game_over(self) -> None:
        """
        Manages the fake mechanism for ending a game (placing a piece in
        position (0, 0)). All empty positions are filled with the piece that was
        placed in (0, 0).

        Returns: Nothing
        """
        self._game_over = True

        winner: int|None = self.piece_at((0, 0))

        for i in range(self.size):
            for j in range(self.size):
                if self.piece_at((i, j)) is None:
                    self._board.place_piece(i, j, winner)


    def pass_turn(self) -> None:
        """
        Causes the current player to pass their turn.

        If all players pass consecutively (with no
        moves between the passes), the game will be
        over.

        Returns: Nothing
        """
        self._passes += 1
        self.switch_turn()

    def scores(self) -> dict[int, int]:
        """
        Computes the current score for each player
        (the number of intersections in their area)

        Returns: Dictionary mapping player numbers to scores
        """
        scores: dict[int, int] = {}
        for player in range(1, self._players + 1):
            scores[player] = 0

        grid_board: list[list[Optional[int]]] = self._board.to_grid()

        for row in grid_board:
            for pos in row:
                if pos is not None:
                    if pos in scores:
                        scores[pos] += 1
                    else:
                        scores[pos] = 1
        
        return scores

    def load_game(self, turn: int, grid: BoardGridType) -> None:
        """
        Loads a new board into the game.

        Note: This will wipe the history of prior board states,
              so violations of the ko rule may not be detected
              after loading a game.

        Args:
            turn: The player number of the player that
            would make the next move ("whose turn is it?")
            Players are numbered from 1.
            grid: The state of the board as a list of lists
            (same as returned by the grid property)

        Raises:
             ValueError:
             - If the value of turn is inconsistent
               with the _players attribute.
             - If the size of the grid is inconsistent
               with the _side attribute.
             - If any value in the grid is inconsistent
               with the _players attribute.

        Returns: None
        """
        raise NotImplementedError

    def simulate_move(self, pos: tuple[int, int] | None) -> "GoBase":
        """
        Simulates the effect of making a move,
        **without** altering the state of the game (instead,
        returns a new object with the result of applying
        the provided move).

        The provided position is not required to be a legal
        move, as this method could be used to check whether
        making a move results in a board that violates the
        ko rule.

        Args:
            pos: Position on the board, or None for a pass

        Raises:
            ValueError: If any of the specified position
            is outside the bounds of the board.

        Returns: An object of the same type as the object
        the method was called on, reflecting the state
        of the game after applying the provided move.
        """
        # Creating a new GoBase and copying all relevant data into it
        simulation: "GoBase" = GoFake(self._side, self._players, self._superko)
        
        for i in range(self._side):
            for j in range(self._side): 
                simulation._board.place_piece(i, j, self._board.piece_at(i, j))
        # simulation._board = deepcopy(self._board)
        
        for i in range(len(self._prev_boards)): 
            simulation._prev_boards.append(self._prev_boards[i])
        # simulation._prev_boards = deepcopy(self._prev_boards)
        
        simulation._turn = self._turn
        simulation._game_over = self._game_over
        simulation._passes = self._passes

        if pos is None:
            simulation.pass_turn()
        else:
            simulation.apply_move(pos)
        
        return simulation 
        
      
    def capture(self, pos: tuple[int, int]) -> None: 
        """
        If there are any pieces belonging to the other player in the positions 
        adjacent (up, down, left, and right) to the piece we just placed, 
        those pieces are captured
        """
        row, col = pos

        up = (row - 1, col)
        down = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)
        
        liberties: list[tuple[int, int]] = [up, down, left, right]

        for l in liberties: 
            if 0 <= l[0] < self.size and 0 <= l[1] < self.size: 
                if self._board.piece_at(l[0], l[1])!= self._board.piece_at(row, col): 
                        self._board.remove_piece(l[0], l[1])
