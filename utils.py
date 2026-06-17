import pygame
from constants import font

def draw_pixel_art(surface, pixel_grid, palette, scale=2):
    for ri, row in enumerate(pixel_grid):
        for ci, ch in enumerate(row):
            if ch == '.':
                continue
            color = palette.get(ch, (255, 0, 255))
            rect = pygame.Rect(ci * scale, ri * scale, scale, scale)
            pygame.draw.rect(surface, color, rect)

def make_tile_surf(px, pal, w=32, h=32):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = len(px[0])
    rows = len(px)
    pw = max(1, w // cols)
    ph = max(1, h // rows)
    for ri, row in enumerate(px):
        for ci, ch in enumerate(row):
            if ch == '.':
                continue
            color = pal.get(ch, (255, 0, 255))
            pygame.draw.rect(s, color, (ci * pw, ri * ph, pw, ph))
    return s

def _new_particle(sw, sh):
    import random
    return {
        "x": float(random.randint(32, sw - 32)),
        "y": float(random.randint(32, sh - 32)),
        "vy": random.uniform(-0.25, -0.06),
        "vx": random.uniform(-0.05, 0.05),
        "life": random.randint(80, 200),
        "max_life": 0,
        "size": random.randint(1, 2),
        "hue": random.choice([
            (0, 200, 80), (0, 160, 60), (0, 240, 100),
            (0, 180, 220), (180, 0, 220), (220, 160, 0),
            (0, 220, 200), (220, 80, 0),
        ]),
    }