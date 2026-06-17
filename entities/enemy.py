import pygame
import math
import random
from abc import ABC, abstractmethod
from constants import TILE, C_GREEN, C_GREEN_DIM, C_AMBER, font
from utils import draw_pixel_art
from systems.vision import VisionSystem

ENEMY_PIXELS = [
    "....RRRRRR....",
    "...RRRRRRRR...",
    "...RWWRWWRR...",
    "...RRRRRRRR...",
    "....RRRRRR....",
    "..DDDDDDDDDD..",
    "..DDDDDDDDDD..",
    "..DD.DDDD.DD..",
    "..DD.DDDD.DD..",
    "...DDDDDDDD...",
    "....DDDDDD....",
    "...DD....DD...",
    "...DD....DD...",
    "..DDD....DDD..",
    "..DD......DD..",
    ".............",
]
PATROL_PAL = {'R': (50, 80, 180), 'W': (200, 220, 255), 'D': (30, 50, 110)}
CHASE_PAL  = {'R': (220, 30, 30),  'W': (255, 220, 100), 'D': (130, 20, 20)}
SEARCH_PAL = {'R': (200, 120, 20), 'W': (255, 230, 120), 'D': (100, 65, 15)}

def make_enemy_surf(palette):
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    draw_pixel_art(s, ENEMY_PIXELS, palette, 2)
    return s

class EnemyState(ABC):
    def __init__(self, name): self.state_name = name
    @abstractmethod
    def enter(self, e): pass
    @abstractmethod
    def execute(self, e, p): pass
    @abstractmethod
    def exit(self, e): pass

class PatrolState(EnemyState):
    def __init__(self):
        super().__init__("Patrol")
        self.pt_idx = 0; self.stay_t = 0
    def enter(self, e):
        e.alert_level = 0
        e.image = make_enemy_surf(PATROL_PAL)
        self.pt_idx = 0
    def execute(self, e, p):
        if e.detect(p): e.change_state(ChaseState()); return
        if not e.patrol_points: return
        tx, ty = e.patrol_points[self.pt_idx]
        dx = tx - e.x; dy = ty - e.y
        dist = math.hypot(dx, dy)
        now = pygame.time.get_ticks()
        if dist < 5:
            if self.stay_t == 0: self.stay_t = now
            if now - self.stay_t > 1000:
                self.pt_idx = (self.pt_idx + 1) % len(e.patrol_points)
                self.stay_t = 0
        else:
            e.move(dx / dist, dy / dist)
    def exit(self, e): pass

class ChaseState(EnemyState):
    def __init__(self):
        super().__init__("Chase")
        self.last_seen = (0, 0); self._orig_spd = 0
    def enter(self, e):
        e.alert_level = 100
        self._orig_spd = e.speed
        e.speed = int(e.speed * 1.5)
        e.image = make_enemy_surf(CHASE_PAL)
    def execute(self, e, p):
        if e.detect(p):
            self.last_seen = (p.x, p.y)
            self._go(e, p.x, p.y)
        else:
            dx = self.last_seen[0] - e.x; dy = self.last_seen[1] - e.y
            if math.hypot(dx, dy) > 10:
                self._go(e, *self.last_seen)
            else:
                e.change_state(SearchState(self.last_seen))
    def _go(self, e, tx, ty):
        dx = tx - e.x; dy = ty - e.y
        d = math.hypot(dx, dy)
        if d > 0: e.move(dx / d, dy / d)
    def exit(self, e): e.speed = self._orig_spd

class SearchState(EnemyState):
    def __init__(self, pos):
        super().__init__("Search")
        self.pos = pos; self.timer = 5.0
        self.t0 = 0; self.sub = None
    def enter(self, e):
        e.alert_level = 50
        self.t0 = pygame.time.get_ticks()
        self._gen(e)
        e.image = make_enemy_surf(SEARCH_PAL)
    def _gen(self, e):
        r = random.uniform(20, 80); a = random.uniform(0, 2 * math.pi)
        self.sub = (self.pos[0] + math.cos(a) * r, self.pos[1] + math.sin(a) * r)
    def execute(self, e, p):
        if e.detect(p): e.change_state(ChaseState()); return
        if (pygame.time.get_ticks() - self.t0) / 1000 >= self.timer:
            e.change_state(PatrolState()); return
        if self.sub:
            dx = self.sub[0] - e.x; dy = self.sub[1] - e.y
            d = math.hypot(dx, dy)
            if d < 10: self._gen(e)
            else: e.move(dx / d, dy / d)
    def exit(self, e): pass

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.x = float(x); self.y = float(y)
        self.width = 32; self.height = 32; self.speed = speed
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = make_enemy_surf(PATROL_PAL)
        self.health = 100
        self.vision_range = 160
        self.vision_angle = 60
        self.alert_level = 0
        self.patrol_points = []
        self.current_state = None
        self._vision = VisionSystem(max_distance=self.vision_range)
        self._alert_pulse = 0
        self.contact_damage = 15
        self._contact_timer = 0
        self._contact_cooldown = 800

    def change_state(self, ns):
        if self.current_state: self.current_state.exit(self)
        self.current_state = ns
        self.current_state.enter(self)
        self._alert_pulse = 0

    def detect(self, player):
        return self._vision.can_see_player(self, player)

    def try_deal_damage(self, player):
        now = pygame.time.get_ticks()
        if now - self._contact_timer < self._contact_cooldown:
            return False
        if self.rect.colliderect(player.rect):
            player.health = max(0, player.health - self.contact_damage)
            player.take_damage_flash()
            self._contact_timer = now
            return True
        return False

    def draw(self, screen):
        shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 55), shadow.get_rect())
        screen.blit(shadow, (self.rect.x + 2, self.rect.bottom - 8))
        screen.blit(self.image, self.rect)
        if self.alert_level > 0:
            self._alert_pulse = (self._alert_pulse + 3) % 360
            pulse = 0.6 + 0.4 * math.sin(math.radians(self._alert_pulse))
            if self.alert_level >= 100:
                label, col = "!", (int(255 * pulse), int(40 * pulse), 40)
            else:
                label, col = "?", (int(220 * pulse), int(160 * pulse), 20)
            f = font(18, True)
            lbl = f.render(label, True, col)
            bg = pygame.Surface((lbl.get_width() + 6, lbl.get_height() + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 100))
            screen.blit(bg, (self.rect.centerx - bg.get_width() // 2, self.rect.top - 20))
            screen.blit(lbl, (self.rect.centerx - lbl.get_width() // 2, self.rect.top - 20))

    def update_enemy(self, player):
        if self.current_state:
            self.current_state.execute(self, player)
        if isinstance(self.current_state, ChaseState):
            self.try_deal_damage(player)
        self.rect.x = int(self.x); self.rect.y = int(self.y)

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