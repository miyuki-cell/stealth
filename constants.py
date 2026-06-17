import pygame

# Initialize Pygame early for color & font usage
pygame.init()
pygame.mixer.init()

TILE = 32

# Colors
C_BG          = (8, 12, 8)
C_FLOOR_A     = (18, 32, 16)
C_FLOOR_B     = (22, 38, 20)
C_WALL        = (38, 30, 22)
C_WALL_LIT    = (52, 42, 30)
C_WALL_DARK   = (24, 18, 12)
C_GREEN       = (0, 220, 80)
C_GREEN_DIM   = (0, 110, 40)
C_GREEN_DARK  = (0, 55, 20)
C_RED         = (220, 40, 40)
C_AMBER       = (220, 140, 20)
C_CYAN        = (40, 220, 180)
C_WHITE       = (220, 210, 190)
C_SHADOW      = (0, 0, 0, 120)
C_GOLD        = (255, 215, 0)

# Skin presets
SKIN_PRESETS = [
    {"name": "Default",    "skin": (200, 160, 110), "suit": (10, 70, 10),   "outline": (25, 25, 25)},
    {"name": "Stealth",    "skin": (180, 140, 90),  "suit": (20, 20, 40),   "outline": (10, 10, 20)},
    {"name": "Desert",     "skin": (210, 170, 120), "suit": (160, 110, 50), "outline": (90, 60, 20)},
    {"name": "Crimson",    "skin": (200, 150, 100), "suit": (120, 15, 15),  "outline": (60, 5, 5)},
    {"name": "Arctic",     "skin": (210, 210, 220), "suit": (190, 200, 210),"outline": (120, 130, 150)},
    {"name": "Neon",       "skin": (190, 240, 180), "suit": (0, 200, 120),  "outline": (0, 80, 50)},
    {"name": "Shadow",     "skin": (90, 80, 70),    "suit": (30, 30, 30),   "outline": (10, 10, 10)},
    {"name": "Gold",       "skin": (230, 180, 100), "suit": (180, 130, 0),  "outline": (100, 70, 0)},
]

_FONT_CACHE: dict = {}

def font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont("Courier", size, bold=bold)
    return _FONT_CACHE[key]