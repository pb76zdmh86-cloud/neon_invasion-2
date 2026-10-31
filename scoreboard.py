import pygame.font
from pygame.sprite import Group
from ship import Ship


class Scoreboard:
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        self.text_color = self.settings.text_color
        self.accent_color = self.settings.neon_cyan
        self.combo_color = self.settings.neon_yellow

        # scoreboard.py, строки 18–20 — вся тройка SysFont уходит, вместо неё:
        self.font = pygame.font.Font(self.settings.font_file_digits, 34)
        self.label_font = pygame.font.Font(self.settings.font_file_digits, 14)
        self.combo_font = pygame.font.Font(self.settings.font_file_digits, 26)

        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def _render(self, text, font, color):
        return font.render(text, True, color)

    def prep_score(self):
        score_str = f"{round(self.stats.score, -1):,}"
        self.score_image = self._render(score_str, self.font, self.accent_color)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 24
        self.score_rect.top = 44

    def prep_high_score(self):
        high_score_str = f"{round(self.stats.high_score, -1):,}"
        dim_cyan = tuple(int(c * 0.6) for c in self.settings.neon_cyan)
        self.high_score_image = self._render(high_score_str, self.font, dim_cyan)
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def prep_level(self):
        level_str = f"LV {self.stats.level}"
        self.level_image = self._render(level_str, self.font, self.settings.neon_green)
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 8

    def prep_ships(self):
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 20 + ship_number * (ship.rect.width + 10)
            ship.rect.y = 20
            self.ships.add(ship)

    def show_score(self):
        for label, rect, color in [
            ("SCORE", self.score_rect, self.accent_color),
            ("BEST", self.high_score_rect, self.settings.neon_magenta),
            ("LEVEL", self.level_rect, self.settings.neon_green),
        ]:
            label_img = self.label_font.render(label, True, color)
            label_rect = label_img.get_rect()
            label_rect.centerx = rect.centerx
            label_rect.bottom = rect.top - 2
            self.screen.blit(label_img, label_rect)

        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

        self._draw_combo_hud()

    def _draw_progress_bar(self, y, progress, color,x):
        """Рисует шкалу: progress = 0 — пустая, progress = 1 — полная."""
        progress = max(0.0, min(1.0, progress))
        width = min(220, self.screen_rect.width - 48)
        bar_rect = pygame.Rect(0, y, width, 8)
        bar_rect.centerx = x

        # Сначала фон, затем заполнение и тонкая рамка.
        background = tuple(int(c * 0.12) for c in color)
        border = tuple(int(c * 0.45) for c in color)
        pygame.draw.rect(self.screen, background, bar_rect, border_radius=4)
        fill_width = round(width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=4)
        pygame.draw.rect(self.screen, border, bar_rect, width=1, border_radius=4)
        return bar_rect.bottom

    def _draw_hud_label(self, text, y, color,x):
        """Рисует подпись по центру и возвращает её нижнюю координату."""
        image = self.label_font.render(text, True, color)
        rect = image.get_rect(centerx=x, top=y)
        self.screen.blit(image, rect)
        return rect.bottom

    def _draw_combo_hud(self):
        """Показывает время обычного комбо и отдельный заряд суперпули."""
        combo_x = self.high_score_rect.right + 150
        super_x = self.high_score_rect.left - 150
        y = self.high_score_rect.top

        combo_color = self.settings.neon_yellow
        super_color = self.settings.neon_cyan

        # Обычное комбо: шкала убывает за combo_window_ms после убийства.
        bullet_mult = self.stats.bullet_multiplier()
        combo_text = f"COMBO {self.stats.combo_count} | AMMO x{bullet_mult}"
        y = self._draw_hud_label(combo_text, y, combo_color, combo_x) + 5
        progress = self.stats.combo_timer_ms / self.settings.combo_window_ms
        y = self._draw_progress_bar(y, progress, combo_color, combo_x) + 12

        # В текущей механике суперпуля заряжается за 20 убийств.
        y = self.high_score_rect.top
        if self.stats.super_ready:
            super_text = "SUPER READY"
            charge = 1.0
            super_color = self.settings.neon_yellow
            hint = "AUTO FIRE ON SPACE"
        else:
            super_text = f"SUPER {self.stats.combo}/20"
            charge = self.stats.combo / 20
            # Это отдельная цепочка: она прерывается через 3 секунды.
            remaining = max(0.0, self.stats.combo_timer)
            hint = f"CHAIN TIME {remaining:.1f}s" if self.stats.combo > 0 else "20 KILLS | 3s BETWEEN KILLS"

        y = self._draw_hud_label(super_text, y, super_color,super_x) + 5
        y = self._draw_progress_bar(y, charge, super_color,super_x) + 5
        hint_color = tuple(int(c * 0.6) for c in self.settings.text_color)
        y = self.high_score_rect.bottom + 12
        self._draw_hud_label(hint, y, hint_color, self.screen_rect.centerx)

    def check_high_score(self):
        if self.settings.zen_mode or not self.stats.ranked_run:
            return False  # в zen-режиме рекорды не обновляем
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()
            return True
        return False
