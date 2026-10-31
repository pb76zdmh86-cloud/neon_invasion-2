import random
import math
import pygame


class Starfield:
    

    def __init__(self, screen_width, screen_height, layers=3, stars_per_layer=60):
        self.width = screen_width
        self.height = screen_height
        self.layers = []
        speeds = (7, 18, 36)
        sizes = (1, 1, 2)
        base_alpha = (70, 110, 160)

        for layer_index in range(layers):
            speed = 8 + layer_index * 22
            size = 1 + layer_index
            stars = []
            for _ in range(stars_per_layer):
                stars.append({
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(0, self.height),
                    "phase": random.uniform(0, math.tau),
                    "glint": random.random() < 0.055,
                })
            self.layers.append({
                "speed": speeds[min(layer_index, len(speeds) - 1)],
                "size": sizes[min(layer_index, len(sizes) - 1)],
                "alpha": base_alpha[min(layer_index, len(base_alpha) - 1)],
                "stars": stars,
            })
        self.time = 0.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        for layer in self.layers:
            for star in layer["stars"]:
                star["x"] = min(star["x"], width - 1)
                star["y"] = min(star["y"], height - 1)

    def update(self, dt):
        self.time += dt
        for layer in self.layers:
            for star in layer["stars"]:
                star["y"] += layer["speed"] * dt
                if star["y"] > self.height:
                    star["y"] = 0
                    star["x"] = random.uniform(0, self.width)

    def draw(self, screen):
        layer_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for layer in self.layers:
            for star in layer["stars"]:
                twinkle = 0.55 + 0.45 * math.sin(self.time * 2.2 + star["phase"])
                alpha = int(layer["alpha"] * (0.55 + 0.45 * twinkle))
                x, y = int(star["x"]), int(star["y"])
                color = (255, 247, 0, alpha)
                pygame.draw.circle(layer_surface, color, (x, y), layer["size"])

                if star["glint"] and twinkle > 0.92:
                    ray = 4 + layer["size"] * 2
                    ray_color = (255, 247, 0, min(150, alpha))
                    pygame.draw.line(layer_surface, ray_color, (x - ray, y), (x + ray, y), 1)
                    pygame.draw.line(layer_surface, ray_color, (x, y - ray), (x, y + ray), 1)

        screen.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
