import pygame
import math
import random
from constants import TILE, SKIN_PRESETS, C_GREEN, C_GREEN_DIM
from utils import draw_pixel_art

PLAYER_PIXELS = [
    "....BBBBBB....",
    "...BSSSSSSB...",
    "...BSSSSSSB...",
    "...BSSSSSSB...",
    "....BBBBBB....",
    "...GGGGGGGG...",
    "..GGGGGGGGGG..",
    "..GG.GGGG.GG..",
    "..GG.GGGG.GG..",
    "...GGGGGGGG...",
    "....GGGGGG....",
    "...GG....GG...",
    "...GG....GG...",
    "..GGG....GGG..",
    "..GG......GG..",
    ".............",
]

def make_player_surf(skin_preset=None):
    if skin_preset is None:
        skin_preset = SKIN_PRESETS[0]
    pal = {
        'B': skin_preset["outline"],
        'S': skin_preset["skin"],
        'G': skin_preset["suit"],
    }
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    draw_pixel_art(s, PLAYER_PIXELS, pal, 2)
    return s

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_preset=None):
        super().__init__()
        self.x = float(x); self.y = float(y)
        self.width = 32; self.height = 32; self.speed = 5
        self.rect = pygame.Rect(x, y, 32, 32)
        self.health = 100
        self.inventory = []
        self.is_hidden = False
        self.noise_level = 0
        self.hack_skill = 1
        self.visibility_level = 100
        self.skin_preset = skin_preset if skin_preset else SKIN_PRESETS[0]
        self.image = make_player_surf(self.skin_preset)
        self._dmg_flash = 0
        self._footsteps: list = []
        self._enemy_dmg_timer = 0
        self._enemy_dmg_cooldown = 1000

    def take_damage_flash(self):
        self._dmg_flash = 400

    def update_visibility(self):
        if not self.is_hidden:
            self.visibility_level = 100

    def add_footstep(self):
        self._footsteps.append({
            "x": self.rect.centerx + random.randint(-4, 4),
            "y": self.rect.centery + random.randint(-4, 4),
            "life": 40,
        })

    def hide(self):
        self.is_hidden = True
        self.noise_level = 0
        self.visibility_level = 0

    def interact(self, obj):
        if hasattr(obj, 'on_interact'):
            obj.on_interact(self)

    def draw(self, screen):
        shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        screen.blit(shadow, (self.rect.x + 2, self.rect.bottom - 8))
        screen.blit(self.image, self.rect)
        if self._dmg_flash > 0:
            fl = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            a = int(160 * (self._dmg_flash / 400))
            fl.fill((255, 0, 0, a))
            screen.blit(fl, self.rect)
        for fp in self._footsteps:
            a = int(80 * (fp["life"] / 40))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 200, 80, a), (2, 2), 2)
            screen.blit(s, (fp["x"] - 2, fp["y"] - 2))

    def move(self, dx, dy, game_map=None):
        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        if game_map:
            tx = int(nx // TILE); ty = int(ny // TILE)
            if game_map.is_walkable(tx, ty):
                self.x = nx; self.y = ny
        else:
            self.x = nx; self.y = ny
        self.rect.x = int(self.x); self.rect.y = int(self.y)

    def update(self):
        self.rect.x = int(self.x); self.rect.y = int(self.y)

    def check_collision(self, other):
        return self.rect.colliderect(other.rect)