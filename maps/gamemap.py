import pygame
import random
from constants import TILE

class Tile:
    def __init__(self, x, y, is_wall):
        self.x = x; self.y = y; self.is_wall = is_wall

class GameMap:
    def __init__(self, w, h):
        self.width = w; self.height = h
        self.tiles = []
        self.rooms = []
        self._bg = None

    def load_map(self):
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                wall = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
                row.append(Tile(x, y, wall))
            self.tiles.append(row)
        self._build_bg()

    def get_tile(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_room_at(self, x: int, y: int):
        for room in self.rooms:
            if (room["x"] <= x < room["x"] + room["w"] and
                    room["y"] <= y < room["y"] + room["h"]):
                return room
        return None

    def _build_bg(self):
        sw = self.width * TILE; sh = self.height * TILE
        self._bg = pygame.Surface((sw, sh))
        rng = random.Random(42)

        FLOOR_PALETTES = [
            ((14, 28, 14), (0, 8, 0),   (28, 55, 24)),
            ((16, 24, 32), (8, 12, 20),  (24, 40, 52)),
            ((28, 18, 10), (16, 10, 6),  (45, 30, 15)),
            ((22, 10, 28), (12, 6, 16),  (38, 18, 44)),
            ((8,  26, 28), (4,  14, 16), (14, 44, 46)),
            ((26, 24, 8),  (14, 13, 4),  (44, 42, 14)),
        ]

        ACCENT_COLORS = [
            (0, 80, 40),   (0, 50, 80),  (60, 20, 0),
            (50, 0,  60),  (0, 60, 60),  (60, 55, 0),
        ]

        floor_variants = []
        for pi in range(6):
            base_dark, shadow_c, edge_c = FLOOR_PALETTES[pi]
            s = pygame.Surface((TILE, TILE))
            s.fill(base_dark)
            for _ in range(10):
                gx = rng.randint(0, TILE - 4)
                gy = rng.randint(0, TILE - 4)
                dr = rng.randint(-3, 7); dg = rng.randint(-3, 7); db = rng.randint(-3, 7)
                c = (max(0, min(255, base_dark[0] + dr)),
                     max(0, min(255, base_dark[1] + dg)),
                     max(0, min(255, base_dark[2] + db)))
                pygame.draw.rect(s, c, (gx, gy, rng.randint(1, 3), rng.randint(1, 3)))
            if rng.random() < 0.3:
                acc = ACCENT_COLORS[pi]
                for _ in range(3):
                    ax = rng.randint(4, TILE - 8); ay = rng.randint(4, TILE - 8)
                    pygame.draw.rect(s, acc, (ax, ay, 2, 2))
            pygame.draw.line(s, shadow_c, (0, 0), (TILE, 0))
            pygame.draw.line(s, shadow_c, (0, 0), (0, TILE))
            pygame.draw.line(s, edge_c, (TILE - 1, 0), (TILE - 1, TILE))
            pygame.draw.line(s, edge_c, (0, TILE - 1), (TILE, TILE - 1))
            floor_variants.append(s)

        WALL_PALETTES = [
            ((80, 60, 44), (100, 78, 56), (56, 42, 28)),
            ((44, 60, 80), (56, 78, 100), (28, 42, 56)),
            ((72, 44, 80), (90, 56, 100), (48, 28, 56)),
            ((44, 80, 76), (56, 100, 95), (28, 56, 52)),
        ]

        wall_variants = []
        for wpi in range(4):
            wc, wl, wd = WALL_PALETTES[wpi]
            wall_tile = pygame.Surface((TILE, TILE))
            wall_tile.fill(wc)
            for wy in range(0, TILE, 4):
                c = wl if (wy // 4) % 3 == 0 else wd
                pygame.draw.line(wall_tile, c, (0, wy), (TILE, wy))
            pygame.draw.rect(wall_tile, (15, 12, 8), wall_tile.get_rect(), 1)
            inner = pygame.Rect(3, 3, TILE - 6, TILE - 6)
            pygame.draw.rect(wall_tile, wl, inner, 1)
            wall_variants.append(wall_tile)

        for row in self.tiles:
            for tile in row:
                rx = tile.x * TILE; ry = tile.y * TILE
                if tile.is_wall:
                    wi = (tile.x * 3 + tile.y * 7) % len(wall_variants)
                    self._bg.blit(wall_variants[wi], (rx, ry))
                else:
                    seed_val = tile.x * 13 + tile.y * 7
                    v = seed_val % len(floor_variants)
                    self._bg.blit(floor_variants[v], (rx, ry))

        for _ in range(18):
            lx = rng.randint(32, sw - 64)
            ly = rng.randint(32, sh - 64)
            glow_col = random.choice([
                (0, 60, 30, 35), (0, 30, 60, 35), (40, 0, 60, 30),
                (0, 55, 55, 30), (55, 50, 0, 28),
            ])
            glow_r = rng.randint(18, 45)
            gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for gr in range(glow_r, 0, -1):
                a = int(glow_col[3] * (1 - gr / glow_r) * 0.6)
                if a > 0:
                    pygame.draw.circle(gs, (*glow_col[:3], a), (glow_r, glow_r), gr)
            self._bg.blit(gs, (lx - glow_r, ly - glow_r))

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return not self.tiles[y][x].is_wall
        return False

    def draw(self, screen):
        if self._bg:
            screen.blit(self._bg, (0, 0))