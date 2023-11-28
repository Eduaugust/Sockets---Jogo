import pygame
from typing import List


class TelaInicial:
    def __init__(self, width, height, games: dict):
        self.width = width
        self.height = height
        self.games = games
        self.win = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(None, 32)
        self.username = ""
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color_background = pygame.Color('grey12')
        self.color_background1 = pygame.Color('white')
        self.color = pygame.Color('lightskyblue1')
        self.active = False
        self.beHost = False
        self.gameSelected = None

    def draw_text(self, text, x, y):
        txt_surface = self.font.render(text, True, self.color)
        self.win.blit(txt_surface, (x, y))
    
    def draw_button(self, text, x, y, w, h, ic, ac, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            pygame.draw.rect(self.win, ac, (x, y, w, h))
            if click[0] == 1 and action is not None:
                action()
        else:
            pygame.draw.rect(self.win, ic, (x, y, w, h))

        # draw text centered in the button
        self.draw_text(text, x + (w / 6), y + (h / 3))

    def draw_game_list(self, start_y):
        for game in self.games:
            self.draw_text(f"Nome jogador criado: {game} {self.games[game]}/6", 100, start_y)
            start_y += 40

    def draw(self):
        self.win.fill(self.color_background1)  # Define a cor de fundo
        self.draw_text("Nome do usuário:", 100, 50)
        pygame.draw.rect(self.win, self.color, self.input_box, 2)
        self.draw_text(self.username, self.input_box.x + 10, self.input_box.y + 5)
        self.draw_button("Ser um host", 100, 200, 200, 50, self.color_inactive, self.color_active, self.host_game)
        self.draw_game_list(300)
        pygame.display.flip()

    def host_game(self):
        print("Hosting game...")
        self.beHost = True

    def get_clicked_username(self, start_y, mouse_pos) -> str | None:
        print("Enter in a existing game")
        for game in self.games:
            if start_y <= mouse_pos[1] <= start_y + 40:
                self.gameSelected = game
                print("Clicked on username", game)
                return game
            start_y += 40
        return None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            userNameSelected = self.get_clicked_username(300, event.pos)
            if userNameSelected is not None:
                print("Clicked on username", userNameSelected)
                self.color = self.color_active if self.active else self.color_background
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                else:
                    self.username += event.unicode
                    
