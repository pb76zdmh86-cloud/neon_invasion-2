import pygame
from button import Button
from ui_style import draw_diamond, draw_glow_text


class RecordsScreen:
    """Зал славы: топ all-time и топ дня из Leaderboard."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        w, h = self.screen.get_rect().size
        cx = w // 2
        self.cx, self.h = cx, h

        self.title_font = pygame.font.Font(self.settings.font_file, 44)
        self.section_font = pygame.font.Font(self.settings.font_file, 16)
        self.row_font = pygame.font.Font(self.settings.font_file_digits, 24)

        self.back_button = Button(ai_game, "Back", (cx, int(h * 0.88)),
                                  self.settings.orange_exit_button, font_size=20)

    def update(self, dt, mouse_pos):
        self.back_button.update(dt, mouse_pos)

    def handle_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_RETURN):
            return "menu"

    def handle_click(self, mouse_pos):
        if self.back_button.rect.collidepoint(mouse_pos):
            return "menu"

    def _draw_section(self, title, records, top, title_color):
        
        title_img = self.section_font.render(title, True, title_color)
        self.screen.blit(title_img, title_img.get_rect(center=(self.cx, top)))
        y = top + 30
        if not records:
            empty = self.row_font.render("NO RECORDS YET", True,
                                         tuple(int(c * 0.55) for c in self.settings.neon_cyan))
            self.screen.blit(empty, empty.get_rect(center=(self.cx, y)))
            return
        for i, record in enumerate(records):
            color = self.settings.neon_cyan if i == 0 \
                else tuple(int(c * 0.55) for c in self.settings.neon_cyan)
            # ромбик-маркер слева, имя, очки справа
            draw_diamond(self.screen, (self.cx - 260, y + 12), 8, color,
                         width=0, glow=(i == 0))
            name_img = self.row_font.render(f"{i + 1}. {record['name']}", True, color)
            self.screen.blit(name_img, name_img.get_rect(midleft=(self.cx - 235, y + 12)))
            score_img = self.row_font.render(f"{record['score']:,}", True, color)
            self.screen.blit(score_img, score_img.get_rect(midright=(self.cx + 260, y + 12)))
            y += 30

    def draw(self):
        lb = self.ai_game.leaderboard
        draw_glow_text(self.screen, "HALL OF FAME", self.title_font,
                       self.settings.neon_magenta, (self.cx, int(self.h * 0.13)))
        self._draw_section("ALL TIME", lb.top_all_time(5),
                           int(self.h * 0.28), self.settings.neon_magenta)
        self._draw_section("TODAY", lb.top_daily(5),
                           int(self.h * 0.60), self.settings.neon_yellow)
        self.back_button.draw_button()