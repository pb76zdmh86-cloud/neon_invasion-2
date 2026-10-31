from pathlib import Path
import pygame
from pygame.sprite import Sprite


def _build_ship_image(color, width=54, height=44):
    """Рисует неоновый корабль-треугольник с мягким свечением, без bmp-файла."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    tip = (width // 2, 2)
    left = (4, height - 6)
    right = (width - 4, height - 6)

    # свечение — несколько полупрозрачных увеличенных копий контура
    for glow in range(6, 0, -2):
        glow_color = (*color, 22)
        glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(
            glow_surface, glow_color,
            [(tip[0], tip[1] - glow), (left[0] - glow, left[1] + glow),
             (right[0] + glow, right[1] + glow)]
        )
        surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.polygon(surface, color, [tip, left, right])
    pygame.draw.polygon(surface, (255, 255, 255), [tip, left, right], width=2)
    # маленький "кокпит"
    pygame.draw.circle(surface, (10, 10, 20), (width // 2, height - 16), 5)
    return surface


class Ship(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        image_path = Path(__file__).parent / "images" / "ship.png"
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()

        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 14
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False
        self.firing = False
        self.shield_active = False
        self.triple_shot_timer = 0.0

        self.engine_timer = 0.0



    def update(self, dt=1 / 60):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed * dt * 60
        elif self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed * dt * 60

        self.x = max(0, min(self.x, self.screen_rect.width - self.rect.width))
        self.rect.x = self.x

        self.engine_timer += dt

        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
            self.triple_shot_timer = max(0, self.triple_shot_timer)

    def engine_glow_pos(self):
        """Точка под кораблём — сюда сыплются частицы двигателя."""
        return self.rect.centerx, self.rect.bottom - 4

    def blitme(self):
        self.screen.blit(self.image, self.rect)
        if self.shield_active:
            self.shield_radius = max(self.rect.width, self.rect.height) // 2 + 10
            pygame.draw.circle(self.screen, self.settings.neon_cyan, 
                               self.rect.center, self.shield_radius, 2)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 14
        self.x = float(self.rect.x)
