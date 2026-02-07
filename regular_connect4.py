import pygame, sys

class Board:
    def __init__(self, game):
        self.game = game
        self.width = 7
        self.height = 6
        self.square_size = (int(self.game.width//self.width), int(self.game.height//self.height))
        self.assets = {
            "background": pygame.transform.scale(pygame.image.load("graphics/background.png"),
                                                 (self.square_size[0] + 2, self.square_size[1])),
            "red_piece": pygame.transform.scale(pygame.image.load("graphics/red_piece.png"), self.square_size),
            "yellow_piece": pygame.transform.scale(pygame.image.load("graphics/yellow_piece.png"), self.square_size),
        }
        self.squares = self.squares = [(row, col) for row in range(self.height) for col in range(self.width)]
        self.cells = [Cell(self, cords) for cords in self.squares]
        self.board_state = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.hovered_col = None
        self.move_buffer = 0

    def reset(self):
        self.game.turn = 0
        self.game.clicked = False
        self.squares = [(row, col) for row in range(self.height) for col in range(self.width)]
        self.cells = [Cell(self, cords) for cords in self.squares]
        self.board_state = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.hovered_col = None
        self.move_buffer = 0
        self.game.win_text_timer = 255

    def get_top_empty_row(self, col):
        for row in range(self.height - 1, -1, -1):
            if self.board_state[row][col] == 0:
                return row
        return None

    def drop_piece(self, col):
        player = 1 if self.game.turn % 2 == 0 else 2
        top_row = self.get_top_empty_row(col)
        if top_row is not None:
            self.board_state[top_row][col] = player
            return top_row
        return None

    def check_win(self, piece):
        # Check horizontal locations for win
        for c in range(self.width - 3):
            for r in range(self.height):
                if self.board_state[r][c] == piece and self.board_state[r][c + 1] == piece and self.board_state[r][c + 2] == piece and self.board_state[r][c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(self.width):
            for r in range(self.height - 3):
                if self.board_state[r][c] == piece and self.board_state[r + 1][c] == piece and self.board_state[r + 2][c] == piece and self.board_state[r + 3][c] == piece:
                    return True

        # Check positively sloped diaganols
        for c in range(self.width - 3):
            for r in range(self.height - 3):
                if self.board_state[r][c] == piece and self.board_state[r + 1][c + 1] == piece and self.board_state[r + 2][c + 2] == piece and self.board_state[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diaganols
        for c in range(self.width - 3):
            for r in range(3, self.height):
                if self.board_state[r][c] == piece and self.board_state[r - 1][c + 1] == piece and self.board_state[r - 2][c + 2] == piece and self.board_state[r - 3][c + 3] == piece:
                    return True
        return False

    def move(self, cell_clicked):
        top_row = self.drop_piece(cell_clicked.col)
        if top_row is not None:
            for cell in self.cells:
                if cell.col == cell_clicked.col and cell.row == top_row:
                    if self.game.turn % 2 == 0:
                        cell.img = self.assets["red_piece"]
                    else:
                        cell.img = self.assets["yellow_piece"]
                    self.game.turn += 1
                    self.move_buffer = 20
                    break

    def update(self):
        #move piece into cell if buffer time is up
        self.move_buffer -= 1
        for cell in self.cells:
            if self.game.clicked:
                if cell.rect.collidepoint(self.game.mouse_pos):
                    if self.move_buffer < 0:
                        self.move(cell)
            #draw ghost piece
            elif cell.rect.collidepoint(self.game.mouse_pos):
                top_row = self.get_top_empty_row(cell.col)
                if top_row is not None:
                    for top_cell in self.cells:
                        if top_cell.col == cell.col and top_cell.row == top_row:
                            if self.game.turn % 2 == 0:
                                overlay_piece = self.assets["red_piece"].copy()
                                overlay_piece.set_alpha(128)
                            else:
                                overlay_piece = self.assets["yellow_piece"].copy()
                                overlay_piece.set_alpha(110)
                            self.game.screen.blit(overlay_piece, (top_cell.x + 1, top_cell.y))
                            self.hovered_col = top_cell.col

            cell.draw()

        for cell in self.cells:
            self.game.screen.blit(cell.background, cell.rect)

        if self.check_win(1):
            self.game.last_winner = "red"
            self.reset()
        if self.check_win(2):
            self.game.last_winner = "yellow"
            self.reset()


class Cell:
    def __init__(self, board, cords):
        self.img = None
        self.board = board
        self.background = board.assets["background"]
        self.row, self.col = cords
        self.x = self.col * self.board.square_size[0]
        self.y = self.row * self.board.square_size[1]
        self.falling_y = -self.board.square_size[1]
        self.rect = pygame.Rect((self.x, self.y), self.board.square_size)
        self.overlay_on = False
        self.overlay = pygame.Surface(self.board.square_size, pygame.SRCALPHA)
        self.overlay.fill((255, 255, 255, 120))

    def draw(self):
        if self.img:
            if not self.falling_y <= self.y:
                self.board.game.screen.blit(self.img, (self.x + 1, self.y))
            else:
                self.board.game.screen.blit(self.img, (self.x + 1, self.falling_y))
                self.falling_y += 11

        #---highlight on square you'll move to if you click---
        #if self.board.get_top_empty_row(self.col) == self.row and self.board.hovered_col == self.col:
         #   self.board.game.screen.blit(self.overlay, self.rect)


class Tictactoe:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Connect 4')
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.frame_rate = 60
        self.board = Board(self)
        self.mouse_pos = pygame.mouse.get_pos()
        self.clicked = False
        self.turn = 0
        self.game_over = False
        self.font = pygame.font.SysFont("comicsans", 45)
        self.win_text_timer = 0
        self.last_winner = None

    def win_text(self, text):
        if self.last_winner == "red":color = (255, 0, 0)
        else: color = (255, 255, 0)
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.width // 2, 100))
        text_surf.set_alpha(self.win_text_timer)
        self.screen.blit(text_surf, text_rect)
        self.win_text_timer -= 1

    def take_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.clicked = True
            else:
                self.clicked = False

    def run(self):
        while True:
            self.mouse_pos = pygame.mouse.get_pos()
            self.screen.fill(pygame.Color('grey'))
            self.take_input()
            self.board.update()
            if self.win_text_timer > 0:
                self.win_text(f"{self.last_winner} won")

            pygame.display.flip()
            self.clock.tick(self.frame_rate)

game = Tictactoe()
game.run()