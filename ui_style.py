from pathlib import Path
import pygame


def load_font(path, size):
    """Load a project font, falling back to pygame's default if the file is absent."""
    try:
        if path and Path(path).exists():
            return pygame.font.Font(path, size)
    except (OSError, TypeError):
        pass
    return pygame.font.Font(None, size)


def dim(color, factor=0.55):
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def draw_diamond(screen, center, size, color, width=0, glow=False, glow_alpha=28):
    cx, cy = int(center[0]), int(center[1])
    size = int(size)
    points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]

    if glow:
        for extra, alpha in ((7, glow_alpha // 2), (4, glow_alpha)):
            s = pygame.Surface((size * 2 + extra * 2 + 4, size * 2 + extra * 2 + 4), pygame.SRCALPHA)
            scx, scy = s.get_width() // 2, s.get_height() // 2
            pts = [
                (scx, scy - size - extra),
                (scx + size + extra, scy),
                (scx, scy + size + extra),
                (scx - size - extra, scy),
            ]
            pygame.draw.polygon(s, (*color, alpha), pts, width=max(1, width or 2))
            screen.blit(s, (cx - scx, cy - scy), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.polygon(screen, color, points, width=width)


def draw_glow_text(screen, text, font, color, center, glow_alpha=42, offsets=(5, 2)):
    """Approximate two-layer neon text glow without blur filters."""
    base = font.render(text, True, color)
    rect = base.get_rect(center=center)

    for radius, alpha in ((offsets[0], glow_alpha // 2), (offsets[1], glow_alpha)):
        glow = font.render(text, True, color)
        glow.set_alpha(alpha)
        for dx, dy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
            screen.blit(glow, rect.move(dx, dy))

    screen.blit(base, rect)
    return rect


def draw_split_logo(screen, left_text, right_text, font, left_color, right_color, center, gap=24):
    left = font.render(left_text, True, left_color)
    right = font.render(right_text, True, right_color)
    total_w = left.get_width() + gap + right.get_width()
    x = int(center[0] - total_w / 2)
    cy = int(center[1])

    left_rect = left.get_rect(midleft=(x, cy))
    right_rect = right.get_rect(midleft=(x + left.get_width() + gap, cy))

    # Two restrained glow layers as defined by the design references.
    for surf, rect, color in ((left, left_rect, left_color), (right, right_rect, right_color)):
        for radius, alpha in ((6, 18), (3, 34)):
            g = surf.copy()
            g.set_alpha(alpha)
            for dx, dy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
                screen.blit(g, rect.move(dx, dy))
        screen.blit(surf, rect)

    return pygame.Rect(left_rect.left, min(left_rect.top, right_rect.top), total_w,
                       max(left_rect.height, right_rect.height))


def draw_thin_rule(screen, y, center_x, width, color, alpha=70, diamond_caps=True):
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    x1 = int(center_x - width / 2)
    x2 = int(center_x + width / 2)
    pygame.draw.line(layer, (*color, alpha), (x1, int(y)), (x2, int(y)), 1)
    screen.blit(layer, (0, 0))
    if diamond_caps:
        draw_diamond(screen, (x1, y), 3, dim(color, 0.65), width=1)
        draw_diamond(screen, (x2, y), 3, dim(color, 0.65), width=1)
