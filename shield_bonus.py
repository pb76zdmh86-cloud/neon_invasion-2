import pygame
from pygame.sprite import Sprite

class ShieldBonus(Sprite):
    def __init__(self, ai_game, center):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.image,ai_game.settings.neon_cyan,(16, 16),14,2)
        self.rect = self.image.get_rect(center=center)
        self.y = float(self.rect.y)

    def update(self, dt):
        self.y += self.settings.shield_bonus_speed * dt
        self.rect.y = self.y 
        if self.rect.top >= self.screen.get_height():
            self.kill()
