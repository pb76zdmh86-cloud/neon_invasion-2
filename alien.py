from pathlib import Path
import math
import random
import pygame
from pygame.sprite import Sprite

ALIEN_SIZE = 44  # используется и здесь, и в alien_invasion.py для расчёта волн


def _build_alien_image(color, size=ALIEN_SIZE):
    """Рисует неонового пришельца-кристалл (ромб) со свечением, без bmp-файла."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = [(cx, 2), (size - 4, cy), (cx, size - 2), (4, cy)]

    for glow in range(8, 0, -2):
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        expanded = [(cx, 2 - glow), (size - 4 + glow, cy), (cx, size - 2 + glow), (4 - glow, cy)]
        pygame.draw.polygon(glow_surface, (*color, 20), expanded)
        surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 255, 255), points, width=2)
    pygame.draw.circle(surface, (10, 10, 20), (cx, cy), 4)
    return surface


class Alien(Sprite):
    FILES = {0: "alien_cyan.png", 1: "alien_magenta.png", 2: "alien_orange.png"}
    images = {} 
    def __init__(self, ai_game, tier=0):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.tier = tier % len(self.settings.alien_tier_colors)
        self.color = self.settings.alien_tier_colors[self.tier]     # ← вернуть!
        self.points = self.settings.aliens_points + self.settings.alien_tier_bonus[self.tier]

        if self.tier not in Alien.images: 
            path = Path(__file__).parent / "images" / Alien.FILES[self.tier]
            Alien.images[self.tier] = pygame.image.load(path).convert_alpha()
        self.image = Alien.images[self.tier]                
        self.rect = self.image.get_rect()


        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        self.x = float(self.rect.x)
        self.base_y = float(self.rect.y)

        self.bob_phase = random.uniform(0, math.tau)
        self.bob_timer = 0.0

    def check_edges(self):
        screen_rect = self.screen.get_rect()
        return self.rect.right > screen_rect.right or self.rect.left <= 0

    def update(self, dt=1 / 60):
        self.x += self.settings.alien_speed * self.settings.fleet_direction * dt * 60
        self.rect.x = self.x

        # лёгкое покачивание для живости — не влияет на позицию для коллизий по X
        self.bob_timer += dt
        bob_offset = math.sin(self.bob_timer * 3 + self.bob_phase) * 2
        self.rect.y = self.base_y + bob_offset
