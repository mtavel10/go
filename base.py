"""
Abstract base class for Go
"""
from abc import ABC, abstractmethod

# Type for representing the state of the game board (the "grid")
# as a list of lists. Each entry will either be an integer (meaning
# there is a piece at that location for that player) or None,
# meaning there is no piece in that location. Players are
# numbered from 1.
BoardGridType = list[list[int | None]]

# Type for representing lists of moves on the board.
ListMovesType = list[tuple[int, int]]


class GoBase(ABC):
    """
    Abstract base class for the game of Go
    """

    _side: int
    _players: int
    _superko: bool

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
        self._side = side
        self._players = players
        self._superko = superko

    #
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
    @abstractmethod
    def grid(self) -> BoardGridType:
        """
        Returns the state of the game board as a list of lists.
        Each entry can either be an integer (meaning there is a
        piece at that location for that player) or None,
        meaning there is no piece in that location. Players are
        numbered from 1.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def turn(self) -> int:
        """
        Returns the player number for the player who must make
        the next move (i.e., "whose turn is it?")  Players are
        numbered from 1.

        If the game is over, this property will not return
        any meaningful value.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def available_moves(self) -> ListMovesType:
        """
        Returns the list of positions where the current player
        (as returned by the turn method) could place a piece.

        If the game is over, this property will not return
        any meaningful value.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def done(self) -> bool:
        """
        Returns True if the game is over, False otherwise.
        """
        raise NotImplementedError

    @property
    @abstractmethod
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
        raise NotImplementedError

    #
    # METHODS
    #

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def apply_move(self, pos: tuple[int, int]) -> None:
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
        raise NotImplementedError

    @abstractmethod
    def pass_turn(self) -> None:
        """
        Causes the current player to pass their turn.

        If all players pass consecutively (with no
        moves between the passes), the game will be
        over.

        Returns: Nothing
        """
        raise NotImplementedError

    @abstractmethod
    def scores(self) -> dict[int, int]:
        """
        Computes the current score for each player
        (the number of intersections in their area)

        Returns: Dictionary mapping player numbers to scores
        """
        raise NotImplementedError

    @abstractmethod
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

    @abstractmethod
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
        raise NotImplementedError
