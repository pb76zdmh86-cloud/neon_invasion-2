import random
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size","kind")

    def __init__(self, x, y, vx, vy, life, color, size,kind="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.size = size
        self.kind = kind


class ParticleSystem:
    """Простая система партиклов для взрывов и попаданий."""

    def __init__(self):
        self.particles = []

    def spawn_burst(self, x, y, color, count=16, speed_range=(60, 220)):
        for _ in range(count):
            angle = random.uniform(0, 6.2832)
            speed = random.uniform(*speed_range)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            life = random.uniform(0.4, 0.9)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, vx, vy, life, color, size,kind="shard"))
            self.particles.append(Particle(x, y, 0, 0, 0.08, (255, 255, 255), 26, kind="flash"))

    def spawn_trail(self, x, y, color):
        vx = random.uniform(-15, 15)
        vy = random.uniform(20, 50)
        self.particles.append(Particle(x, y, vx, vy, 0.25, color, 2))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 90 * dt  # лёгкая гравитация для красоты
            alive.append(p)
        self.particles = alive

    def draw(self, screen):
        for p in self.particles:
            fade = max(0.0, p.life / p.max_life)
            radius = max(1, int(p.size * fade))
            color = tuple(min(255, int(c * fade + 30)) for c in p.color)
            pygame.draw.circle(screen, color, (int(p.x), int(p.y)), radius)

    def clear(self):
        self.particles = []
