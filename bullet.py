import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    def __init__(self, ai_game, offset=0):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        self.rect.x += offset  # сдвиг влево/вправо для тройного выстрела

        self.y = float(self.rect.y)
        self.speed = self.settings.bullet_speed  # своя скорость: SuperBullet её переопределяет

    def update(self, dt=1 / 60):
        self.y -= self.speed * dt * 60
        self.rect.y = self.y

    def draw_bullet(self):
        glow_rect = self.rect.inflate(8, 8)
        glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color, 90), glow_surface.get_rect(), border_radius=4)
        self.screen.blit(glow_surface, glow_rect.topleft)
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=2)
class SuperBullet(Bullet):
    def __init__(self, ai_game):
        super().__init__(ai_game)
        self.piercing = True
        self.rect.width = 80              # толще
        self.rect.height = 30            # длиннее
        self.rect.centerx = ai_game.ship.rect.centerx  # после смены размера центр сбросился
        self.color = (255, 220, 60)       # жёлтый — «сейчас случится классное»
        self.speed = self.settings.bullet_speed * 1.5
