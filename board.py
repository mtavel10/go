from typing import Optional
from copy import deepcopy
class Board:

    _size: int 
    board: list[list[Optional[int]]]


    #Constructor
    def __init__(self, s: int):
        self._size = s
        self.board = [[None] * s for i in range(s)]



    #Returns size of the board
    @property
    def size(self) -> int:
        return self._size

    
    #Returns the piece at a given position
    def piece_at(self, row: int, col: int) -> Optional[int]:

        if 0 <= row < self._size and 0 <= col < self._size: 
            return self.board[row][col]
        else:
            raise ValueError
    
    def neighbors(self, row: int, col: int) -> set[tuple[int, int]]:
        neighbor_set: set[tuple[int, int]] = set()

        if row - 1 >= 0:
            neighbor_set.add((row - 1, col))
        if row + 1 < self.size:
            neighbor_set.add((row + 1, col))
        if col - 1 >= 0:
            neighbor_set.add((row, col - 1))
        if col + 1 >= 0:
            neighbor_set.add((row, col + 1))

        return neighbor_set
    

    #Places a piece at the given location
    def place_piece(self, row: int, col: int, piece: int | None) -> bool:

        if row >= self._size or col >= self._size:
            raise ValueError
        elif self.piece_at(row, col) is None:
            self.board[row][col] = piece
            return True
        else:
            return False
        
    
    def remove_piece(self, row: int, col: int) -> None:
        if row >= self._size or col >= self._size:
            raise ValueError
        else:
            self.board[row][col] = None


    #Returns matrix representation of the board
    def to_grid(self) -> list[list[Optional[int]]]:
        board_copy: list[list[Optional[int]]] = deepcopy(self.board)
        return board_copy
    
    def __eq__(self, other: object):
        if not isinstance(other, Board): 
            return NotImplemented
        
        if not self.size == other.size:
            return False
        
        for i in range(self.size):
            for j in range(self.size):
                if not self.board[i][j] == other.board[i][j]:
                    return False
                
        return True

    def __hash__(self) -> int: 
        value: int = 0
        for row in self.board: 
            value += hash(tuple(row))
        return value