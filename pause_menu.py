import pygame
from button import Button


class PauseMenu:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        self.hint_font = pygame.font.SysFont("consolas", 16)
        self.high_font = pygame.font.Font(self.settings.font_file, 16)
        self.title_font = pygame.font.Font(self.settings.font_file, 80)

        screen_rect = self.screen.get_rect()
        cx = screen_rect.centerx
        h = screen_rect.height


        # Три кнопки столбиком, начиная чуть ниже середины экрана.
        # Шаг между ними — 90 px (кнопка 60 px + зазор 30 px).

        self.buttons = [
                    Button(ai_game, "Resume",     (cx, int(h * 0.52)),self.settings.soft_blue_play,font_size=20),
                    Button(ai_game, "Settings", (cx, int(h * 0.55) + 60),self.settings.violet_settings_button,font_size=20),
                    Button(ai_game, "Menu",     (cx, int(h * 0.58) + 120),self.settings.orange_exit_button,font_size=20),
                ]
        self.selected = 0

    def handle_click(self, mouse_pos):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                return button.msg
        return None

    def update(self, dt, mouse_pos):
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.selected = i
        for i, button in enumerate(self.buttons):
            button.update(dt, mouse_pos)
            button.hovered = i == self.selected

    def draw(self):
       screen_rect=self.screen.get_rect()


       title_img=self.title_font.render("PAUSE",True,self.settings.neon_cyan)
       title_rect=title_img.get_rect(centerx=screen_rect.centerx,y=int(screen_rect.height * 0.3))
       self.screen.blit(title_img,title_rect)


       high_score_img = self.high_font.render(f"YOUR RECORD: {round(self.stats.high_score, -1):,}", True, self.settings.neon_magenta)
       high_score_rect = high_score_img.get_rect(centerx=screen_rect.centerx, y=int(screen_rect.height * 0.425))
       self.screen.blit(high_score_img, high_score_rect)

       for button in self.buttons:
           button.draw_button()

       btn_rect = self.buttons[self.selected].rect

       tri_h = 26
       tri_w = 22
       gap = 24

       x_tip = btn_rect.left - gap
       x_base = x_tip - tri_w
       cy = btn_rect.centery

       points = [
           (x_base, cy - tri_h // 2),
           (x_base, cy + tri_h // 2),
           (x_tip, cy),
       ]
       pygame.draw.polygon(self.screen, self.buttons[self.selected].border_color, points)

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.buttons)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)
        elif key == pygame.K_RETURN:
            return self.buttons[self.selected].msg


