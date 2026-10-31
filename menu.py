from pathlib import Path
import pygame
from button import Button
from ui_style import dim


class Menu:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        screen_rect = self.screen.get_rect()
        cx = screen_rect.centerx
        h = screen_rect.height

        self.hint_font = pygame.font.SysFont("consolas", 16)
        self.high_font = pygame.font.Font(self.settings.font_file, 16)
        self.title_font = pygame.font.Font(self.settings.font_file, 80)
        self.logo = pygame.image.load(Path(__file__).resolve().parent / "logo.png").convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo,(screen_rect.width * 0.8,250))


        self.buttons = [
            Button(ai_game, "Play",     (cx, int(h * 0.44)), self.settings.soft_blue_play),
            Button(ai_game, "Settings", (cx, int(h * 0.44) + 90), self.settings.violet_settings_button, font_size=20),
            Button(ai_game, "Records",  (cx, int(h * 0.44) + 180), self.settings.neon_yellow, font_size=20),
            Button(ai_game, "Exit",     (cx, int(h * 0.44) + 270), self.settings.orange_exit_button),
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
        screen_rect = self.screen.get_rect()
        cx, h = screen_rect.centerx, screen_rect.height

        logo = self.logo

        logo_rect = logo.get_rect(
                   center=(cx, int(h * 0.18)))
        self.screen.blit(logo, logo_rect)

        record = self.high_font.render(
            f"BEST  {round(self.stats.high_score, -1):,}", True, self.settings.neon_magenta
        )
        self.screen.blit(record, record.get_rect(center=(cx, int(h * 0.35))))

        for button in self.buttons:
            button.draw_button()

        hint = self.hint_font.render(
            "ARROWS / MOUSE  SELECT     ENTER  CONFIRM     F11  FULLSCREEN",
            True, dim(self.settings.text_color, 0.42),
        )
        self.screen.blit(hint, hint.get_rect(center=(cx, int(h * 0.92))))

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.buttons)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)
        elif key == pygame.K_RETURN:
            return self.buttons[self.selected].msg


