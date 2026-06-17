import pygame
from constants import TILE
from utils import make_tile_surf

CRATE_PX = [
    "LLLLLLLLLLLLLL",
    "LDDDDDDDDDDDDL",
    "LDOOOOOOOOOODL",
    "LDOODDDDDOODL",
    "LDOODLLLLDOODL",
    "LDOODLLLLDOODL",
    "LDOODDDDDOODL",
    "LDOOOOOOOOOODL",
    "LDDDDDDDDDDDDL",
    "LLLLLLLLLLLLLL",
]
CRATE_PAL = {'L': (190, 130, 50), 'D': (130, 85, 25), 'O': (210, 160, 80)}

WALL_PX = [
    "AAAABBBBAAAABB",
    "AAAABBBBAAAABB",
    "CCCCDDDDCCCCDD",
    "CCCCDDDDCCCCDD",
    "BBBBAAAABBBBAA",
    "BBBBAAAABBBBAA",
    "DDDDCCCCDDDDCC",
    "DDDDCCCCDDDDCC",
    "AAAABBBBAAAABB",
    "AAAABBBBAAAABB",
]
WALL_PAL = {'A': (90, 80, 68), 'B': (72, 64, 54), 'C': (80, 70, 58), 'D': (62, 54, 44)}

TREE_PX = [
    "......LLLL....",
    "....LLLLLLLL..",
    "...LLLGGGGLL..",
    "..LLLGGGGGGL..",
    "..LLGGGGGGLL..",
    "..LLGGGGGGLL..",
    "...LLLGGGLLL..",
    "....LLLLLL....",
    "......TTTT....",
    "......TTTT....",
    "......TTTT....",
]
TREE_PAL = {'L': (28, 110, 28), 'G': (44, 170, 44), 'T': (110, 72, 32)}

BARREL_PX = [
    "...BBBBBBBB...",
    "..BHHHHHHHHB..",
    "..BHHBBHHHHHB.",
    "..BBBBBBBBBBB.",
    ".BBBBBBBBBBBBB",
    ".BDDDDDDDDDDB.",
    ".BDDDDDDDDDDB.",
    ".BBBBBBBBBBBBB",
    "..BBBBBBBBBBB.",
    "..BBBBBBBBB...",
    "...BBBBBBB....",
]
BARREL_PAL = {'B': (110, 55, 18), 'H': (170, 85, 28), 'D': (90, 45, 12)}

_OBS_SURFS = None

def obs_surfs():
    global _OBS_SURFS
    if _OBS_SURFS is None:
        _OBS_SURFS = {
            "crate":  make_tile_surf(CRATE_PX,  CRATE_PAL),
            "wall":   make_tile_surf(WALL_PX,   WALL_PAL),
            "tree":   make_tile_surf(TREE_PX,   TREE_PAL),
            "barrel": make_tile_surf(BARREL_PX, BARREL_PAL),
        }
    return _OBS_SURFS

class Obstacle:
    def __init__(self, x, y, w=32, h=32, kind="crate"):
        self.x = x; self.y = y
        self.width = w; self.height = h
        self.kind = kind
        self.rect = pygame.Rect(x, y, w, h)
        self._surf = None

    def _build(self):
        base = obs_surfs().get(self.kind, obs_surfs()["crate"])
        if self.width == 32 and self.height == 32:
            self._surf = base.copy()
        else:
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for tx in range(0, self.width, 32):
                for ty in range(0, self.height, 32):
                    s.blit(base, (tx, ty))
            self._surf = s

    def blocks(self, r): return self.rect.colliderect(r)

    def draw(self, screen):
        if self._surf is None: self._build()
        shadow = pygame.Surface((self.width + 4, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
        screen.blit(shadow, (self.x - 2, self.y + self.height - 6))
        screen.blit(self._surf, (self.x, self.y))
        pygame.draw.rect(screen, (0, 0, 0, 80), self.rect, 1)