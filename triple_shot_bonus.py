import pygame
from shield_bonus import ShieldBonus


class TripleShotBonus(ShieldBonus):
    """Падающий бонус: тройной выстрел на 10 секунд."""

    def __init__(self, ai_game, center):
        super().__init__(ai_game, center)
        # перерисовываем иконку: три циановые капсулы-пули в жёлтом кольце
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.settings.neon_yellow, (16, 16), 14, 2)
        for dx in (-7, 0, 7):
            pygame.draw.rect(self.image, self.settings.neon_cyan,
                             (16 + dx - 2, 8, 4, 16), border_radius=2)