import os
import sys
import math
from typing import Optional
import pygame
import pygame.gfxdraw
import click


from fakes import GoFake, GoStub
from go import Go
from board import Board
from bot import minimax_move, random_move

# The music (Cheeki Breeki)
from pygame import mixer
mixer.init()
pygame.mixer.music.load('Bandit Radio (Cheeki Breeki) Accordion.mp3')

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

BROWN = (252, 186, 3)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
INDIGO = (75, 0, 130)
VIOLET = (143, 0, 255)

BOX_SIZE = 25
PIECE_RADIUS = BOX_SIZE//2
BORDER = BOX_SIZE * 2
FONT_SIZE = 26

NUM_PLAYERS: int
BOARD_SIZE: int
SUPER_KO: bool

class DisplayGame:
    """
    Draws out the board, with pieces in each corner
    """
    width: int
    total_width: int
    surface: pygame.surface.Surface
    clock: pygame.time.Clock
    player_colors: dict[int, tuple[int, int, int]]
    go: Go
    font: pygame.font.Font
    num_players: int
    super_ko: bool
    pygame.mixer.music.play(-1)

    def __init__(self, size, num_players, super_ko, bot):
        """
        Constructor

        Parameters:
            size : int : the size of the board to be constructed
            width : int : width of window
            height : int : height of window
            border : int : number of pixels to use as border around the board
        """
        # Initialize Pygame
        pygame.init()

        self.size: int = size
        self.width = (self.size - 1) * BOX_SIZE
        self.total_width = self.width + 2 * BORDER
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.num_players = num_players
        self.super_ko = super_ko
        self.bot = bot

        self.go = Go(self.size, self.num_players, self.super_ko)
        
        self.player_colors = {1 :  WHITE, 2 : BLACK, 3: RED, 4: ORANGE, 
                              5: YELLOW, 6: GREEN, 7: BLUE, 8: INDIGO, 
                              9: VIOLET}

        #pygame.display.set_caption("Go board")
        self.surface = pygame.display.set_mode((self.total_width,
                                                self.total_width))
        self.clock = pygame.time.Clock()

        self.event_loop()

    def draw_grid(self) -> None:
        """
        Draws the grid, for a certain size
        """
        for x in range(BORDER, self.width + BORDER, BOX_SIZE):
            for y in range(BORDER, self.width + BORDER, BOX_SIZE):
                rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)
                pygame.draw.rect(self.surface, BLACK, rect, 1)

    def draw_piece(self, center: tuple[int, int], player: int) -> None:
        """
        Draws a piece


        Parameters:
            radius : int : radius of piece
            center : Tuple[int, int] : center coordinates of circle
            player : int : the player who placed the piece


        Returns: nothing
        """
        pygame.gfxdraw.filled_circle(self.surface, center[0], center[1], 
                                     PIECE_RADIUS, self.player_colors[player])
        
    def draw_turn(self) -> None:
        """
        Draws the text at the top of the display which shows the current player
        turn

        Parameters: none beyond self

        Returns: nothing
        """
        label = self.font.render(f"Player {self.go.turn} to move", True, BLACK)
        text_topleft = ((self.total_width - label.get_width()) // 2,
                        (BORDER - label.get_height()) // 2)
        self.surface.blit(label, text_topleft)

    def draw_pass_turn(self) -> pygame.Rect:
        """
        Draws the buttons that allows a player to pass their turn at the bottom
        of the display

        Parameters: none beyond self

        Returns: the rectangle that was drawn
        """
        label = self.font.render("Pass", True, BLACK, WHITE)
        text_topleft = ((self.total_width - label.get_width()) // 2,
                        self.total_width - ((BORDER + label.get_height()) // 2))
        self.surface.blit(label, text_topleft)

        return pygame.Rect(text_topleft[0], text_topleft[1], label.get_width(), 
                           label.get_height())

    def draw_game_over(self) -> None:
        """
        Draws the contents of the board if the game is over

        Parameters: none beyond self

        Returns: nothing
        """
        self.surface.fill(BROWN)
        str_outcomes: list[str] = [str(player) for player in
                                    self.go.outcome]

        # The winner(s)
        if len(str_outcomes) == 1:
            label = self.font.render(f"Player {str_outcomes[0]} wins", True, BLACK)
        else:
            winners: str = " and ".join(str_outcomes)
            label = self.font.render(f"Players {winners} win", True, BLACK)


        text_topleft = ((self.total_width - label.get_width()) // 2,
                        self.total_width // 2 - (2 * label.get_height()))
        self.surface.blit(label, text_topleft)

        # The scores
        label = self.font.render(f"Scores: {self.go.scores()}", True, BLACK)
        text_topleft = ((self.total_width - label.get_width()) // 2,
                        self.total_width // 2)
        self.surface.blit(label, text_topleft)

    def draw_game(self) -> None:
        """
        Draws the contents of the window

        Parameters: none beyond self

        Returns: nothing
        """
        if self.go.done:
            self.draw_game_over

        else:
            self.surface.fill(BROWN)
            self.draw_grid()
            self.draw_turn()
            self.draw_pass_turn()

            for i in range(self.size):
                for j in range(self.size):
                    piece: Optional[int] = self.go.piece_at((i, j))
                    if piece is not None:
                        self.draw_piece(self.to_coordinates((i, j)), piece)
            
            # If mouse hovering, it will draw the piece anyways
            hovered_address: Optional[tuple[int, int]] = self.to_address(pygame.mouse.get_pos())

            if hovered_address is not None:
                if self.go.piece_at(hovered_address) is None:
                    if hovered_address in self.go.available_moves:
                        self.draw_piece(self.to_coordinates((hovered_address)), self.go.turn)

    def to_coordinates(self, address: tuple[int, int]) -> tuple[int, int]:
        """
        Converts the address of a piece to its coordinates on the board

        Parameters:
            address : tuple[int, int] : the address to convert

        Returns : tuple[int, int] : the converted address
        """
        x_coord: int = BOX_SIZE * address[0] + BORDER
        y_coord: int = BOX_SIZE * address[1] + BORDER

        return (x_coord, y_coord)

    def to_address(self, location: tuple[int, int]) -> \
        Optional[tuple[int, int]]:
        """
        Converts the coordinates of a piece to its address on the board, or None

        Parameters:
            location : tuple[int, int] : the coordinates to convert

        Returns : tuple[int, int] : the address
        """
        for i in range(self.size):
            for j in range(self.size):
                if math.dist(location, self.to_coordinates((i, j))) <= \
                    PIECE_RADIUS:
                    return (i, j)
        return None

    def get_position(self, location: tuple[int, int]) -> \
        Optional[tuple[int, int] | str]:
        """
        Converts coordinates on the board to either the unoccupied piece's
        address, the "pass" button, or None

        Parameters:
            location : tuple[int, int] : the coordinates on the board

        Returns : Optional[tuple[int, int] | str] : either the piece's address,
        the "pass" button, or None
        """
        # If the location is the "pass" button
        if self.draw_pass_turn().collidepoint(location[0], location[1]):
            return "pass"

        # If the location is an unoccupied address on the board
        address: Optional[tuple[int, int]] = self.to_address(location)
        if address is not None:
            if self.go.piece_at(address) is None:
                return address

        # Otherwise
        return None

    def event_loop(self) -> None:
        """
        Handles user interactions

        Parameters : none beyond self

        Returns : nothing
        """
        while True:
            # Process Pygame events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP and not self.go.done:
                    clicked: Optional[tuple[int, int] | str] = \
                        self.get_position(event.pos)
                    
                    if clicked is not None:
                        if clicked == "pass":
                            self.go.pass_turn()

                        else:
                            assert isinstance(clicked, tuple)
                            if self.go.legal_move(clicked):
                                self.go.apply_move(clicked)
                
                if self.bot and self.go.turn == 2:
                    self.go.apply_move(minimax_move(self.go))
                    #self.go.apply_move(random_move(self.go))

                if self.go.done:
                    self.draw_game_over()
                
            # Update the display
            self.draw_game()
            pygame.display.update()
            self.clock.tick(24)

@click.command()
@click.option("-n", "--num-players", default = 2, help = 'Number of players.')
@click.option("-s", "--size", default = 19, help = "Board size.")
@click.option("--simple-ko/--super-ko", default = False, 
              help = "Play with simple-ko or super-ko.")
@click.option("--no-bot/--bot", default = False, help = "Bot or not.")

def cmd(num_players, size, simple_ko, no_bot):
    is_bot = not bool(no_bot)
    is_simple_ko = not bool(simple_ko)

    DisplayGame(size, num_players, is_simple_ko, is_bot)

if __name__ == "__main__":
    cmd()
