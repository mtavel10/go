from base import GoBase, BoardGridType, ListMovesType
from typing import Any, Optional
from copy import deepcopy
from board import Board

class Go(GoBase):

    _side: int
    _players: int
    _superko: bool
    _prev_boards: list[int]
    _turn: int
    _board: Board
    _passes: int
    _done: bool

    def __init__(
        self,
        side: int,
        players: int,
        superko: bool = False,
    ):
        super().__init__(side, players, superko)
        self._turn = 1
        self._board = Board(side)
        self._passes = 0
        self._done = False
        self._prev_states = []
        self._prev_boards = [hash(self._board), hash(self._board)]

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
    def board(self) -> Board: 
        """
        Returns the board object that represents the game board
        """
        return self._board
    
    @property
    def grid(self) -> Any:
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
    def available_moves(self) -> Any:
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
        if self._passes >= self._players:
            return True
        else:
            return False
    

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
    
    def switch_turn(self) -> None: 
        """
        Switches the turn
        """
        self._turn += 1
        if self._turn > self.num_players: 
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

        temp_base: "Go"  = self.simulate_move(pos)

        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        if self.piece_at((row, col)) is not None:
            return False
        
        hashed_board: int = hash(temp_base._board)
        
        if self._superko:
            if hashed_board in self._prev_boards: 
                return False

        else: # otherwise we are in ko case
            if hashed_board == self._prev_boards[0]:
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

        self._passes = 0
        self._board.place_piece(row, col, self._turn)
        self.capture(pos)
        for neighbor in self.get_neighbors(pos):
            self.capture(neighbor)

        curr_board: int = hash(self._board)
            
        if self._superko: 
            self._prev_boards.append(curr_board)
        else: # In the Ko case, we'll only store the most recent board
            prev_board = self._prev_boards[1]
            self._prev_boards[0] = prev_board
            self._prev_boards[1] = curr_board
        
        self.switch_turn()


    def capture(self, pos: tuple[int, int]) -> None: 
        """
        If a move captures an opponent's piece(s)
        """
        for neighbor in self.get_neighbors(pos): 

            to_capture: set[tuple[int, int]] = set()

            if self.piece_at(neighbor) != None and \
                            self.piece_at(neighbor) != self.piece_at(pos):
                to_capture.add(neighbor)
                # Updates to_capture destructively
                if not self.has_liberties(neighbor, to_capture): 
                    for loc in to_capture: 
                        row, col = loc
                        self._board.remove_piece(row, col)
                to_capture = set()
    

    def has_liberties(self, pos: tuple[int, int], targeted: set) -> bool:
        """
        If a piece or any of its chained neighbors have liberties
        Destructively updates targeted set to mark which locations must be deleted
        """
        neighbor_liberties: bool = False

        for neighbor in self.get_neighbors(pos):
            if self.piece_at(neighbor) is None:
                return True
            if self.piece_at(neighbor) == self.piece_at(pos) and \
                                                    not neighbor in targeted:
                targeted.add(neighbor)
                if self.has_liberties(neighbor, targeted):
                    neighbor_liberties = True
                    break
        
        return neighbor_liberties

    
    def get_neighbors(self, pos: tuple[int, int]) -> set[tuple[int, int]]: 
        row, col = pos
        neighbors: set[tuple[int, int]] = set()

        up = (row - 1, col)
        down = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)
        
        if up[0] >= 0: 
            neighbors.add(up)
        if down[0] < self.size: 
            neighbors.add(down)
        if left[1] >= 0: 
            neighbors.add(left)
        if right[1] < self.size: 
            neighbors.add(right)

        return neighbors

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
        Computes the current score for each player ()

        Returns: Dictionary mapping player numbers to scores
        """
        scores: dict[int, int] = {}

        for player in range(1, self._players + 1):
            scores[player] = 0
            for i in range(self.size):
                for j in range(self.size):
                    vis: set = set()
                    sides: set = set()
                    if self.in_territory(player, (i, j), vis, sides):
                        scores[player] += 1
                        
    
        return scores

    def load_game(self, turn: int, grid: list[list[int]]) -> None:
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
        new_board: Board = Board(self.size)
        new_board.board = grid

        #Erase previous history
        self._prev_boards = [hash(new_board), hash(new_board)]
        self._passes = 0
        
        #Load in new game information
        self._board = new_board
        self._turn = turn
    

    def simulate_move(self, pos: Optional[tuple[int, int]]) -> "Go":
        """
        Simulates the effect of making a move
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
        # Creating a new Go game and copying all relevant data into it
        simulation: "Go" = Go(self._side, self._players, self._superko)
        
        for i in range(self._side): 
            for j in range(self._side): 
                simulation.board.place_piece(i, j, self._board.piece_at(i, j))
        
        for i in range(len(self._prev_boards)): 
            simulation._prev_boards.append(self._prev_boards[i])
        
        simulation._turn = self._turn
        simulation._passes = self._passes

        if pos is None:
            simulation.pass_turn()
        else:
            simulation.apply_move(pos)
        
        return simulation 
    
    def in_territory(self, 
                     player: int, 
                     pos: tuple[int, int], 
                     visited: set[tuple[int, int]] = set(),
                     edges_reached: set[str] = set()) -> bool:
        """
        Returns if a position is in the territory of a player (for two players)

        Args:
            player : int : The player in question
            pos : tuple[int, int] : Position on the board
            visited : set[tuple[int][int]] : The set of all posions which have
                already been visited
            edges_reached: set[str] : The set of edges which have already been 
                reached (if 4, it's not a valid territory).
        
        Returns : int | None : either the player number for whom the piece
            counts, or None
        """
        
        if self.piece_at(pos) == player: # Base case; returns True
            return True

        neighbors: list[bool] = []

        for i in {-1, 1}: # Checking the top and bottom neighbors
            neighbor_pos: tuple[int, int] = (pos[0] + i, pos[1])

            if not neighbor_pos in visited:
                if not (0 <= neighbor_pos[0] < self.size):
                    if i == 1:
                        edges_reached.add("top")
                    if i == -1:
                        edges_reached.add("bottom")
                        
                else:
                    visited.add(neighbor_pos)
                    neighbors.append(self.in_territory(player, neighbor_pos, 
                                                        visited, edges_reached))

        for j in {-1, 1}: # Checking the right and left neighbors
            neighbor_pos: tuple[int, int] = (pos[0], pos[1] + j)

            if not neighbor_pos in visited:
                if not (0 <= neighbor_pos[1] < self.size):
                    if j == 1:
                        edges_reached.add("right")
                    if j == -1:
                        edges_reached.add("left")
                        
                else:
                    visited.add(neighbor_pos)
                    neighbors.append(self.in_territory(player, neighbor_pos, 
                                                        visited, edges_reached))
        
        # Reaching all four edges means a territory is not valid
        if len(edges_reached) == 4 or False in neighbors: 
            return False
        
        return True
