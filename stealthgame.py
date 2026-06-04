import pygame
import math
import random
import os
from abc import ABC, abstractmethod
from typing import List, Optional

pygame.init()
pygame.mixer.init()

TILE = 32

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

def draw_pixel_art(surface, pixel_grid, palette, scale=2):
    for ri, row in enumerate(pixel_grid):
        for ci, ch in enumerate(row):
            if ch == '.':
                continue
            color = palette.get(ch, (255, 0, 255))
            rect = pygame.Rect(ci * scale, ri * scale, scale, scale)
            pygame.draw.rect(surface, color, rect)

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

def make_enemy_surf(palette):
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    draw_pixel_art(s, ENEMY_PIXELS, palette, 2)
    return s

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

class SoundManager:
    def __init__(self):
        self.lobby_music = None
        self.gameover_sound = None
        self.win_sound = None
        self.blip_sound = None
        self.music_playing = False
        self._load()

    def _load(self):
        base = os.path.dirname(os.path.abspath(__file__))
        lobby_path = os.path.join(base, "assets", "lobby.mp3")
        go_path    = os.path.join(base, "assets", "gameover.mp3")
        win_path   = os.path.join(base, "assets", "win.mp3")
        blip_path  = os.path.join(base, "assets", "Blip.wav")

        if os.path.exists(go_path):
            try:
                self.gameover_sound = pygame.mixer.Sound(go_path)
                self.gameover_sound.set_volume(0.8)
            except Exception:
                pass

        if os.path.exists(blip_path):
            try:
                self.blip_sound = pygame.mixer.Sound(blip_path)
                self.blip_sound.set_volume(0.5)
            except Exception:
                pass

        if os.path.exists(win_path):
            try:
                self.win_sound = pygame.mixer.Sound(win_path)
                self.win_sound.set_volume(0.6)
            except Exception:
                pass

        self._lobby_path = lobby_path if os.path.exists(lobby_path) else None
        self._go_path    = go_path    if os.path.exists(go_path)    else None

    def play_blip(self):
        if self.blip_sound:
            try:
                self.blip_sound.play()
            except Exception:
                pass

    def play_lobby(self):
        if self._lobby_path and not self.music_playing:
            try:
                pygame.mixer.music.load(self._lobby_path)
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception:
                pass

    def stop_lobby(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def play_gameover(self):
        self.stop_lobby()
        if self.gameover_sound:
            try:
                self.gameover_sound.play()
            except Exception:
                pass

    def stop_gameover(self):
        if self.gameover_sound:
            try:
                self.gameover_sound.stop()
            except Exception:
                pass

    def play_win(self):
        if self.win_sound:
            try:
                self.win_sound.play()
            except Exception:
                pass

    def stop_win(self):
        if self.win_sound:
            try:
                self.win_sound.stop()
            except Exception:
                pass

    def fade_out(self, ms=800):
        try:
            pygame.mixer.music.fadeout(ms)
            self.music_playing = False
        except Exception:
            pass

class VisionSystem:
    def __init__(self, max_distance: int = 160):
        self.max_distance: int = max_distance

    def can_see_player(self, enemy, player) -> bool:
        if self.calculate_distance(enemy, player) > self.max_distance:
            return False
        return self.check_line_of_sight(enemy, player)

    def calculate_distance(self, enemy, player) -> float:
        return math.hypot(player.x - enemy.x, player.y - enemy.y)

    def check_line_of_sight(self, enemy, player) -> bool:
        if player.is_hidden:
            return self.calculate_distance(enemy, player) < self.max_distance * 0.25
        return True

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed):
        super().__init__()
        self.x = float(x); self.y = float(y)
        self.width = w; self.height = h; self.speed = speed
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

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

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def check_collision(self, other: "Entity") -> bool:
        return self.rect.colliderect(other.rect)

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

class Player(Entity):
    def __init__(self, x, y, skin_preset=None):
        super().__init__(x, y, 32, 32, 5)
        self.health = 100
        self.inventory = []
        self.is_hidden = False
        self.noise_level = 0
        self.hack_skill = 1
        self.visibility_level = 100
        self.skin_preset = skin_preset if skin_preset else SKIN_PRESETS[0]
        self.image = make_player_surf(self.skin_preset)
        self._dmg_flash = 0
        self._footsteps: List[dict] = []
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

class Enemy(Entity):
    def __init__(self, x, y, speed=2):
        super().__init__(x, y, 32, 32, speed)
        self.image = make_enemy_surf(PATROL_PAL)
        self.health = 100
        self.vision_range = 160
        self.vision_angle = 60
        self.alert_level = 0
        self.patrol_points = []
        self.current_state: Optional[EnemyState] = None
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
        super().update()


class SecurityCamera:
    def __init__(self, x: int, y: int,
                 vision_range: int = 120,
                 rotation_angle: int = 0):
        self.x = x
        self.y = y
        self.vision_range: int = vision_range
        self.rotation_angle: int = rotation_angle
        self.is_active: bool = True
        self._vision = VisionSystem(max_distance=vision_range)
        self._alarm_triggered = False

    def rotate(self):
        self.rotation_angle = (self.rotation_angle + 2) % 360

    def detect(self, player: Player, game_map) -> bool:
        if not self.is_active:
            return False

        class DummyEnemy:
            def __init__(self, x, y, angle):
                self.x = x
                self.y = y
                self.facing_angle = angle

        dummy = DummyEnemy(self.x, self.y, self.rotation_angle)
        detected = self._vision.can_see_player(dummy, player)
        if detected:
            self.trigger_alarm()
        return detected

    def trigger_alarm(self):
        if not self._alarm_triggered:
            self._alarm_triggered = True
            print(f"[ALARM] Kamera ({self.x},{self.y}) mendeteksi player!")

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), 7)
        ex = self.x + math.cos(math.radians(self.rotation_angle)) * self.vision_range
        ey = self.y + math.sin(math.radians(self.rotation_angle)) * self.vision_range
        pygame.draw.line(screen, (255, 200, 0),
                         (self.x, self.y), (int(ex), int(ey)), 1)


class Terminal:
    def __init__(self, x: int, y: int, hack_difficulty: int = 1):
        self.x = x
        self.y = y
        self.is_hacked: bool = False
        self.hack_difficulty: int = hack_difficulty
        self.rect = pygame.Rect(x, y, 24, 24)

    def hack(self, player: Player) -> bool:
        if self.is_hacked:
            return True
        if player.hack_skill >= self.hack_difficulty:
            self.is_hacked = True
            print(f"[TERMINAL] ({self.x},{self.y}) berhasil diretas!")
            return True
        print(f"[TERMINAL] Gagal — skill {player.hack_skill} < {self.hack_difficulty}")
        return False

    def on_interact(self, player: Player):
        self.hack(player)

    def draw(self, screen: pygame.Surface):
        color = (0, 200, 100) if self.is_hacked else (200, 50, 50)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        lbl = font(9, True).render("TRM", True, (255, 255, 255))
        screen.blit(lbl, (self.x + 2, self.y + 7))


class Item:
    def __init__(self, x: int, y: int,
                 name: str, effect: str, value: str):
        self.x = x
        self.y = y
        self.name: str = name
        self.effect: str = effect
        self.value: str = value

    def use(self, player: Player) -> None:
        if self.effect == "heal":
            player.health = min(100, player.health + int(self.value))
            print(f"[ITEM] {self.name} — health: {player.health}")
        elif self.effect == "hack_boost":
            player.hack_skill += int(self.value)
            print(f"[ITEM] {self.name} — hack_skill: {player.hack_skill}")
        elif self.effect == "stealth":
            player.is_hidden = True
            player.noise_level = 0
            print(f"[ITEM] {self.name} — player tersembunyi")

    def draw(self, screen: pygame.Surface) -> None:
        rect = pygame.Rect(self.x, self.y, 16, 16)
        pygame.draw.rect(screen, (255, 220, 50), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        lbl = font(8).render(self.name[:3], True, (0, 0, 0))
        screen.blit(lbl, (self.x + 1, self.y + 4))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, 16, 16)


class ObjectFactory:
    def __init__(self, difficulty_level: int = 1):
        self.enemy_types: List[str] = ["guard", "patrol"]
        self.item_types: List[str] = ["medkit", "hack_tool", "cloak"]
        self.difficulty_level: int = difficulty_level

    def create_enemy(self, x=0, y=0, patrol_points=None) -> Enemy:
        e = Enemy(x, y, speed=1 + self.difficulty_level)
        e.patrol_points = patrol_points or []
        e.vision_range = 100 + self.difficulty_level * 20
        e.health = 50 + self.difficulty_level * 25
        e._vision = VisionSystem(max_distance=e.vision_range)
        e.change_state(PatrolState())
        return e

    def create_item(self, x=0, y=0) -> Item:
        kind = random.choice(self.item_types)
        if kind == "medkit":
            return Item(x, y, "Medkit", "heal", "30")
        elif kind == "hack_tool":
            return Item(x, y, "HackTool", "hack_boost", "1")
        else:
            return Item(x, y, "Cloak", "stealth", "1")

    def create_terminal(self, x=0, y=0) -> Terminal:
        return Terminal(x, y, hack_difficulty=self.difficulty_level)

    def create_camera(self, x=0, y=0) -> SecurityCamera:
        return SecurityCamera(x, y, vision_range=80 + self.difficulty_level * 15)

class Trap:
    def __init__(self, x, y, damage=20):
        self.x = x; self.y = y; self.damage = damage
        self.rect = pygame.Rect(x, y, 32, 32)
        self.is_triggered = False
        self.trigger_time = 0
        self.cooldown = 2000
        self._pulse = random.uniform(0, 360)

    def check_and_apply(self, player):
        now = pygame.time.get_ticks()
        if self.is_triggered and now - self.trigger_time < self.cooldown:
            return False
        if self.rect.colliderect(player.rect):
            player.health = max(0, player.health - self.damage)
            self.is_triggered = True
            self.trigger_time = now
            return True
        return False

    def draw(self, screen):
        now = pygame.time.get_ticks()
        active = not self.is_triggered or (now - self.trigger_time >= self.cooldown)
        self._pulse = (self._pulse + 2) % 360
        if active:
            p = 0.5 + 0.5 * math.sin(math.radians(self._pulse))
            dark = (int(60 + 30 * p), 8, 8)
            edge = (int(160 + 80 * p), 30, 30)
            pygame.draw.rect(screen, dark, self.rect)
            pygame.draw.rect(screen, edge, self.rect, 1)
            lw = 2
            pygame.draw.line(screen, (int(200 + 55 * p), 60, 60),
                             (self.rect.x + 7, self.rect.y + 7),
                             (self.rect.right - 7, self.rect.bottom - 7), lw)
            pygame.draw.line(screen, (int(200 + 55 * p), 60, 60),
                             (self.rect.right - 7, self.rect.y + 7),
                             (self.rect.x + 7, self.rect.bottom - 7), lw)
            corner_size = 5
            for cx, cy in [(self.rect.x, self.rect.y),
                           (self.rect.right - corner_size, self.rect.y),
                           (self.rect.x, self.rect.bottom - corner_size),
                           (self.rect.right - corner_size, self.rect.bottom - corner_size)]:
                pygame.draw.rect(screen, edge, (cx, cy, corner_size, corner_size))
        else:
            pygame.draw.rect(screen, (30, 10, 10), self.rect)
            pygame.draw.rect(screen, (60, 25, 25), self.rect, 1)

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

class Tile:
    def __init__(self, x, y, is_wall):
        self.x = x; self.y = y; self.is_wall = is_wall

class GameMap:
    def __init__(self, w, h):
        self.width = w; self.height = h
        self.tiles: List[List[Tile]] = []
        self.rooms: List[dict] = []
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

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_room_at(self, x: int, y: int) -> Optional[dict]:
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

def _new_particle(sw, sh):
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

def draw_hud(screen, player, sw, sh):
    bar_w, bar_h = 170, 12
    bx, by = 14, 14
    pygame.draw.rect(screen, (0, 0, 0, 0), (bx - 2, by - 2, bar_w + 4, bar_h + 4))
    pygame.draw.rect(screen, (8, 20, 8), (bx, by, bar_w, bar_h))
    hp = player.health / 100
    if hp > 0:
        if hp > 0.6:
            hpc = (20, 200, 60)
        elif hp > 0.3:
            hpc = (200, 160, 20)
        else:
            hpc = (220, 30, 30)
        pygame.draw.rect(screen, hpc, (bx, by, int(bar_w * hp), bar_h))
    pygame.draw.rect(screen, C_GREEN_DIM, (bx, by, bar_w, bar_h), 1)
    hp_lbl = font(12, True).render(f"HP  {player.health:03d}", True, C_GREEN)
    screen.blit(hp_lbl, (bx + bar_w + 8, by - 1))
    screen.blit(font(11).render(f"HACK {player.hack_skill}", True, C_CYAN), (bx, by + 16))
    if player.is_hidden:
        pulse = 0.6 + 0.4 * math.sin(pygame.time.get_ticks() / 300)
        col = (int(0), int(200 * pulse), int(90 * pulse))
        hs = font(12, True).render("[ HIDDEN ]", True, col)
        screen.blit(hs, (sw - hs.get_width() - 14, 14))

class SkinCustomizer:
    def __init__(self, sw, sh, sounds=None):   # <-- NEW: accepts sounds ref
        self.sw = sw; self.sh = sh
        self.selected = 0
        self.sounds = sounds                   # <-- NEW
        self._preview_surfs = [make_player_surf(p) for p in SKIN_PRESETS]
        self._bg_pulse = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(SKIN_PRESETS)
                if self.sounds:                # <-- NEW: play blip on navigate
                    self.sounds.play_blip()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(SKIN_PRESETS)
                if self.sounds:                # <-- NEW: play blip on navigate
                    self.sounds.play_blip()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "confirm"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def draw(self, screen):
        screen.fill((4, 6, 10))
        self._bg_pulse = (self._bg_pulse + 0.8) % 360

        for i in range(0, self.sw, 40):
            a = int(12 + 8 * math.sin(math.radians(self._bg_pulse + i * 3)))
            pygame.draw.line(screen, (0, a, a // 2), (i, 0), (i, self.sh))
        for j in range(0, self.sh, 40):
            a = int(10 + 6 * math.sin(math.radians(self._bg_pulse + j * 2)))
            pygame.draw.line(screen, (0, a // 2, a), (0, j), (self.sw, j))

        pygame.draw.rect(screen, (0, 160, 80), (0, 0, self.sw, 3))
        pygame.draw.rect(screen, (0, 160, 80), (0, self.sh - 3, self.sw, 3))

        title = font(32, True).render("[ OPERATOR PROFILE ]", True, (0, 240, 120))
        screen.blit(title, title.get_rect(center=(self.sw // 2, 50)))

        sub = font(13).render("← → navigate     ENTER confirm     ESC back", True, (0, 120, 60))
        screen.blit(sub, sub.get_rect(center=(self.sw // 2, 85)))

        card_w, card_h = 76, 120
        total = len(SKIN_PRESETS)
        spacing = 90
        start_x = self.sw // 2 - (total // 2) * spacing + spacing // 2

        for i, preset in enumerate(SKIN_PRESETS):
            cx = start_x + i * spacing
            cy = self.sh // 2

            is_sel = (i == self.selected)
            card_x = cx - card_w // 2
            card_y = cy - card_h // 2
            if is_sel:
                card_y -= 12

            bg_col = (0, 50, 25) if is_sel else (6, 14, 8)
            border_col = (0, 255, 120) if is_sel else (0, 60, 30)
            pygame.draw.rect(screen, bg_col, (card_x, card_y, card_w, card_h), border_radius=8)
            pygame.draw.rect(screen, border_col, (card_x, card_y, card_w, card_h), 2, border_radius=8)

            if is_sel:
                glow = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
                p = 0.5 + 0.5 * math.sin(math.radians(self._bg_pulse * 2))
                ga = int(30 * p)
                pygame.draw.rect(glow, (0, 255, 120, ga), (0, 0, card_w + 20, card_h + 20), border_radius=10)
                screen.blit(glow, (card_x - 10, card_y - 10))

            preview = self._preview_surfs[i]
            scale_factor = 2
            big = pygame.transform.scale(preview, (32 * scale_factor, 32 * scale_factor))
            screen.blit(big, (cx - 32, card_y + 16))

            sw_col = preset["suit"]
            sk_col = preset["skin"]
            dot_y = card_y + 80
            pygame.draw.rect(screen, sk_col, (cx - 20, dot_y, 12, 12), border_radius=3)
            pygame.draw.rect(screen, (200, 200, 200), (cx - 20, dot_y, 12, 12), 1, border_radius=3)
            pygame.draw.rect(screen, sw_col, (cx + 8,  dot_y, 12, 12), border_radius=3)
            pygame.draw.rect(screen, (200, 200, 200), (cx + 8,  dot_y, 12, 12), 1, border_radius=3)

            name_col = (0, 255, 120) if is_sel else (0, 140, 60)
            name_lbl = font(11, is_sel).render(preset["name"], True, name_col)
            screen.blit(name_lbl, name_lbl.get_rect(center=(cx, card_y + card_h - 16)))

        sel_name = font(20, True).render(f"> {SKIN_PRESETS[self.selected]['name'].upper()}", True, (0, 255, 120))
        screen.blit(sel_name, sel_name.get_rect(center=(self.sw // 2, self.sh - 60)))

        dot_total = len(SKIN_PRESETS)
        dot_start = self.sw // 2 - (dot_total * 14) // 2
        for di in range(dot_total):
            col = (0, 220, 100) if di == self.selected else (0, 70, 35)
            pygame.draw.circle(screen, col, (dot_start + di * 14, self.sh - 30), 4)

class MenuScreen:
    ITEMS = ["NEW GAME", "CONTROLS", "QUIT"]

    def __init__(self, sw, sh):
        self.sw = sw; self.sh = sh
        self.selected = 0
        self._stars = [(random.randint(0, sw), random.randint(0, sh),
                        random.uniform(0.4, 1.6)) for _ in range(80)]
        self._scanlines = self._make_scanlines()
        self.show_controls = False
        self._scroll_chars: List[dict] = []
        self._next_col = 0

    def _make_scanlines(self):
        s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        for y in range(0, self.sh, 2):
            pygame.draw.line(s, (0, 0, 0, 30), (0, y), (self.sw, y))
        return s

    def _tick_rain(self):
        now = pygame.time.get_ticks()
        if now - self._next_col > 60:
            self._next_col = now
            col = random.randrange(0, self.sw, 14)
            self._scroll_chars.append({
                "x": col,
                "y": random.randint(-20, 0),
                "speed": random.uniform(1.5, 4.0),
                "len": random.randint(4, 14),
                "chars": [chr(random.randint(33, 126)) for _ in range(20)],
                "offset": 0,
            })
        for c in self._scroll_chars:
            c["y"] += c["speed"]
            c["offset"] = (c["offset"] + 0.15) % len(c["chars"])
        self._scroll_chars = [c for c in self._scroll_chars if c["y"] < self.sh + 20 * 14]

    def handle_event(self, event):
        if self.show_controls:
            if event.type == pygame.KEYDOWN:
                self.show_controls = False
            return None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                ch = self.ITEMS[self.selected]
                if ch == "NEW GAME": return "start"
                if ch == "QUIT":     return "quit"
                if ch == "CONTROLS": self.show_controls = True
        return None

    def update(self):
        self._tick_rain()

    def draw(self, screen):
        screen.fill((4, 8, 4))
        now = pygame.time.get_ticks()

        RAIN_COLORS = [
            (0, 200, 80), (0, 160, 200), (160, 0, 200),
            (0, 200, 180), (200, 160, 0),
        ]
        f_sm = font(13)
        for idx, c in enumerate(self._scroll_chars):
            rain_col = RAIN_COLORS[idx % len(RAIN_COLORS)]
            for i in range(c["len"]):
                cy = int(c["y"]) - i * 14
                if cy < 0 or cy > self.sh: continue
                char_idx = (int(c["offset"]) + i) % len(c["chars"])
                ch = c["chars"][char_idx]
                bright = max(20, 180 - i * 20)
                col = (
                    int(rain_col[0] * bright / 180),
                    int(rain_col[1] * bright / 180),
                    int(rain_col[2] * bright / 180),
                )
                screen.blit(f_sm.render(ch, True, col), (c["x"], cy))

        screen.blit(self._scanlines, (0, 0))

        pygame.draw.rect(screen, (0, 180, 80), (0, 0, self.sw, 3))
        pygame.draw.rect(screen, (0, 80, 200), (0, 3, self.sw, 2))
        pygame.draw.rect(screen, (0, 180, 80), (0, self.sh - 3, self.sw, 3))
        pygame.draw.rect(screen, (0, 80, 200), (0, self.sh - 5, self.sw, 2))

        if self.show_controls:
            self._draw_controls(screen)
            return

        ty = self.sh // 5

        pulse_t = now / 1000
        glow_a = int(80 + 40 * math.sin(pulse_t * 1.5))
        glow_surf = font(52, True).render("> STEALTH ROGUELITE", True, (0, glow_a, int(glow_a * 0.3)))
        title1    = font(52, True).render("> STEALTH ROGUELITE", True, (0, 255, 100))
        title2    = font(52, True).render("  GAME", True, (0, 200, 70))
        tx1 = self.sw // 2 - title1.get_width() // 2
        tx2 = self.sw // 2 - title2.get_width() // 2
        for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
            screen.blit(glow_surf, (tx1 + ox, ty + oy))
        screen.blit(title1, (tx1, ty))
        screen.blit(title2, (tx2, ty + 56))

        ACCENT_COLS = [(0, 255, 100), (0, 180, 255), (180, 0, 255), (0, 255, 200)]
        sub_col = ACCENT_COLS[(now // 1200) % len(ACCENT_COLS)]
        if (now // 600) % 2 == 0:
            sub = font(13).render("[ INFILTRATE  ·  EVADE  ·  SURVIVE ]", True, sub_col)
            screen.blit(sub, sub.get_rect(center=(self.sw // 2, ty + 120)))

        sep_y = ty + 148
        for off in range(3):
            fade = 60 - off * 20
            pygame.draw.line(screen, (0, fade, fade // 3),
                             (self.sw // 4, sep_y + off), (3 * self.sw // 4, sep_y + off))

        for i, item in enumerate(self.ITEMS):
            sel = (i == self.selected)
            if sel:
                t = now / 400
                r = int(128 + 127 * math.sin(t))
                g = 255
                b = int(128 + 127 * math.cos(t))
                col = (r // 4, g, b // 4)
            else:
                col = (0, 100, 50)
            prefix = "> " if sel else "  "
            lbl = font(26, True).render(f"{prefix}{item}", True, col)
            iy = sep_y + 44 + i * 52
            ix = self.sw // 2 - lbl.get_width() // 2
            if sel:
                bg = pygame.Surface((lbl.get_width() + 28, lbl.get_height() + 8), pygame.SRCALPHA)
                bg.fill((*col, 18))
                screen.blit(bg, (ix - 14, iy - 4))
                pygame.draw.rect(screen, (*col[:2], col[2] // 2),
                                 (ix - 14, iy - 4, lbl.get_width() + 28, lbl.get_height() + 8), 1)
            screen.blit(lbl, (ix, iy))

        foot = font(12).render("UP/DOWN  navigate     ENTER  select", True, (0, 70, 35))
        screen.blit(foot, foot.get_rect(center=(self.sw // 2, self.sh - 16)))

        ver = font(12).render("v5.0", True, (0, 50, 25))
        screen.blit(ver, (self.sw - 40, self.sh - 16))

    def _draw_controls(self, screen):
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))

        panel_w, panel_h = 460, 400
        px = (self.sw - panel_w) // 2; py = (self.sh - panel_h) // 2
        pygame.draw.rect(screen, (4, 10, 6), (px, py, panel_w, panel_h))
        pygame.draw.rect(screen, C_GREEN_DIM, (px, py, panel_w, panel_h), 1)
        pygame.draw.rect(screen, (0, 40, 80), (px + 1, py + 1, panel_w - 2, panel_h - 2), 1)

        lines = [
            ("─── CONTROLS ───",           (0, 240, 120)),
            ("",                             C_GREEN_DIM),
            ("WASD / Arrows      Move",      C_WHITE),
            ("H                  Hide / Unhide", C_WHITE),
            ("R (Game Over)      Restart",   C_WHITE),
            ("Esc                Pause", C_WHITE),
            ("",                             C_GREEN_DIM),
            ("─── ENEMIES ───",             (0, 180, 255)),
            ("",                             C_GREEN_DIM),
            ("Blue    Patrol mode",          (100, 140, 255)),
            ("Red     Chase mode — watch out!", (255, 80, 80)),
            ("Orange  Search mode",          (220, 150, 40)),
            ("",                             C_GREEN_DIM),
            ("─── HAZARDS ───",             (255, 80, 80)),
            ("",                             C_GREEN_DIM),
            ("Red X   Deals 15 damage, 2s cooldown", (200, 80, 80)),
            ("Enemy contact deals 15 dmg",  (200, 80, 80)),
            ("",                             C_GREEN_DIM),
            ("[ Any key to close ]",         C_GREEN_DIM),
        ]
        f = font(14)
        start_y = py + 22
        for i, (line, col) in enumerate(lines):
            s = f.render(line, True, col)
            screen.blit(s, s.get_rect(center=(self.sw // 2, start_y + i * 20)))

class Game:
    def __init__(self, sw=800, sh=576):
        self.sw = sw; self.sh = sh
        self.state = "MENU"
        self.game_map = GameMap(25, 18)
        self.player = Player(64, 64)

        self.enemies: List[Enemy] = []
        self.traps: List[Trap] = []
        self.obstacles: List[Obstacle] = []
        self.cameras: List[SecurityCamera] = []
        self.terminals: List[Terminal] = []
        self.items: List[Item] = []

        self._factory = ObjectFactory()
        self.menu = MenuScreen(sw, sh)
        self.sounds = SoundManager()
        self.skin_screen = SkinCustomizer(sw, sh, sounds=self.sounds)  # <-- pass sounds
        self._particles: List[dict] = []
        self._loading_start = 0
        self._loading_dur = 2800
        self._step_timer = 0
        self._vignette = self._make_vignette()
        self._scan = self._make_scanlines()
        self._selected_skin = SKIN_PRESETS[0]
        self._gameover_sound_played = False
        self._win_sound_played = False
        self.pause_menu_items = ["RESUME", "MAIN MENU", "QUIT GAME"]
        self.pause_selected = 0
        self.win_menu_items = ["RESTART", "MAIN MENU", "QUIT GAME"]
        self.win_selected = 0
        self.gameover_menu_items = ["RESTART", "MAIN MENU", "QUIT GAME"]
        self.gameover_selected = 0
        self.sounds.play_lobby()

    def _make_vignette(self):
        s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        cx, cy = self.sw // 2, self.sh // 2
        max_r = math.hypot(cx, cy)
        for y in range(0, self.sh, 2):
            for x in range(0, self.sw, 2):
                d = math.hypot(x - cx, y - cy)
                a = int(100 * (d / max_r) ** 2.2)
                a = min(a, 180)
                if a > 10:
                    pygame.draw.rect(s, (0, 0, 0, a), (x, y, 2, 2))
        return s

    def _make_scanlines(self):
        s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        for y in range(0, self.sh, 3):
            pygame.draw.line(s, (0, 0, 0, 18), (0, y), (self.sw, y))
        return s

    def _setup_level(self):
        self.enemies.clear(); self.traps.clear(); self.obstacles.clear(); self.cameras.clear()
        self.terminals.clear(); self.items.clear()

        e1 = Enemy(400, 300, 2)
        e1.patrol_points = [(400, 300), (600, 300), (600, 450), (400, 450)]
        e1.change_state(PatrolState())
        self.enemies.append(e1)

        e2 = Enemy(200, 400, 2)
        e2.patrol_points = [(200, 400), (350, 400)]
        e2.change_state(PatrolState())
        self.enemies.append(e2)

        e3 = Enemy(580, 160, 2)
        e3.patrol_points = [(580, 160), (700, 160), (700, 260), (580, 260)]
        e3.change_state(PatrolState())
        self.enemies.append(e3)

        for tx, ty in [(160, 160), (192, 160), (224, 160), (320, 256),
                       (480, 352), (512, 352), (288, 448), (448, 192)]:
            self.traps.append(Trap(tx, ty, 15))

        obs_data = [
            (256, 128,  32,  96, "wall"),
            (384, 192,  96,  32, "wall"),
            (160, 320,  32,  64, "wall"),
            (480, 256,  32, 128, "wall"),
            (320, 384, 128,  32, "wall"),
            (96,  448,  64,  32, "wall"),
            (560, 128,  32,  32, "crate"),
            (592, 128,  32,  32, "crate"),
            (624, 128,  32,  32, "crate"),
            (140, 192,  32,  32, "crate"),
            (440,  96,  32,  32, "tree"),
            (472,  96,  32,  32, "tree"),
            (504,  96,  32,  32, "tree"),
            (200, 250,  32,  32, "tree"),
            (232, 250,  32,  32, "tree"),
            (680, 300,  32,  32, "tree"),
            (680, 332,  32,  32, "tree"),
            (340, 160,  32,  32, "barrel"),
            (520, 448,  32,  32, "barrel"),
            (600, 450,  32,  32, "barrel"),
        ]
        for (ox, oy, ow, oh, kind) in obs_data:
            self.obstacles.append(Obstacle(ox, oy, ow, oh, kind))

        self.cameras.append(self._factory.create_camera(300, 200))
        self.cameras.append(self._factory.create_camera(550, 400))

        self.terminals.append(self._factory.create_terminal(300, 100))
        self.terminals.append(self._factory.create_terminal(650, 400))

        self.items.append(self._factory.create_item(350, 300))
        self.items.append(self._factory.create_item(600, 200))

        self._particles = [_new_particle(self.sw, self.sh) for _ in range(50)]
        for p in self._particles:
            p["max_life"] = p["life"]

    def start_loading(self):
        self.state = "LOADING"
        self._loading_start = pygame.time.get_ticks()
        self.sounds.fade_out(600)
        self.game_map.load_map()
        self._setup_level()

    def restart(self):
        self.player = Player(64, 64, self._selected_skin)
        self._setup_level()
        self._gameover_sound_played = False
        self._win_sound_played = False
        self.sounds.stop_win()
        self.sounds.stop_gameover()
        self.state = "PLAYING"

    def handle_event(self, event):
        if self.state == "MENU":
            r = self.menu.handle_event(event)
            if r == "start":
                self.state = "SKIN_SELECT"
            elif r == "quit":
                return False

        elif self.state == "SKIN_SELECT":
            r = self.skin_screen.handle_event(event)
            if r == "confirm":
                self._selected_skin = SKIN_PRESETS[self.skin_screen.selected]
                self.start_loading()
            elif r == "back":
                self.state = "MENU"

        elif self.state == "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "PAUSED"
                self.pause_selected = 0

        elif self.state == "PAUSED":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.pause_selected = (self.pause_selected - 1) % len(self.pause_menu_items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_selected = (self.pause_selected + 1) % len(self.pause_menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = self.pause_menu_items[self.pause_selected]
                    if action == "RESUME":
                        self.state = "PLAYING"
                    elif action == "MAIN MENU":
                        self.state = "MENU"
                        self.sounds.play_lobby()
                    elif action == "QUIT GAME":
                        return False
                elif event.key == pygame.K_ESCAPE:
                    self.state = "PLAYING"


        elif self.state == "WIN":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.win_selected = (self.win_selected - 1) % len(self.win_menu_items)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.win_selected = (self.win_selected + 1) % len(self.win_menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = self.win_menu_items[self.win_selected]
                    if action == "RESTART":
                        self.sounds.stop_win()
                        self.restart()
                    elif action == "MAIN MENU":
                        self.sounds.stop_win()
                        self.state = "MENU"
                        self.sounds.play_lobby()
                    elif action == "QUIT GAME":
                        return False


        elif self.state == "GAMEOVER":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.gameover_selected = (self.gameover_selected - 1) % len(self.gameover_menu_items)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.gameover_selected = (self.gameover_selected + 1) % len(self.gameover_menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = self.gameover_menu_items[self.gameover_selected]
                    if action == "RESTART":
                        self.sounds.stop_gameover()
                        self.restart()
                    elif action == "MAIN MENU":
                        self.sounds.stop_gameover()
                        self.state = "MENU"
                        self.sounds.play_lobby()
                    elif action == "QUIT GAME":
                        return False

        return True

    def _obs_blocks(self, nx, ny):
        r = pygame.Rect(int(nx), int(ny), self.player.width, self.player.height)
        if any(o.blocks(r) for o in self.obstacles):
            return True

        MAX_OVERLAP = 20

        for trap in self.traps:
            if r.colliderect(trap.rect):
                overlap_x = max(0, min(r.right, trap.rect.right) - max(r.left, trap.rect.left))
                overlap_y = max(0, min(r.bottom, trap.rect.bottom) - max(r.top, trap.rect.top))
                overlap = min(overlap_x, overlap_y)

                if overlap > MAX_OVERLAP:
                    return True

        for corner in [(r.left, r.top), (r.right - 1, r.top),
                       (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1)]:
            tx = corner[0] // TILE
            ty = corner[1] // TILE
            if not self.game_map.is_walkable(tx, ty):
                return True
        return False

    def handle_input(self):
        if self.state != "PLAYING": return
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1

        if dx or dy:
            if dx and dy: dx *= 0.7071; dy *= 0.7071
            nx = self.player.x + dx * self.player.speed
            ny = self.player.y + dy * self.player.speed
            if not self._obs_blocks(nx, ny):
                self.player.move(dx, dy, self.game_map)
                now = pygame.time.get_ticks()
                if now - self._step_timer > 200:
                    self.player.add_footstep()
                    self._step_timer = now

        self.player.is_hidden = bool(keys[pygame.K_h])
        if not self.player.is_hidden:
            self.player.update_visibility()
        else:
            self.player.visibility_level = 0

    def update(self):
        if self.state == "MENU":
            self.menu.update()
            return

        if self.state == "SKIN_SELECT":
            return

        if self.state == "PAUSED":
            return

        if self.state == "WIN":
            return

        if self.state == "LOADING":
            if pygame.time.get_ticks() - self._loading_start >= self._loading_dur:
                self.player = Player(64, 64, self._selected_skin)
                self.state = "PLAYING"
            return

        if self.state == "GAMEOVER":
            if not self._gameover_sound_played:
                self.sounds.play_gameover()
                self._gameover_sound_played = True
            return

        if self.state != "PLAYING": return

        self.player.update()
        if self.player._dmg_flash > 0:
            self.player._dmg_flash = max(0, self.player._dmg_flash - 16)

        self.player._footsteps = [fp for fp in self.player._footsteps if fp["life"] > 0]
        for fp in self.player._footsteps:
            fp["life"] -= 1

        for e in self.enemies:
            e.update_enemy(self.player)
        for t in self.traps:
            if t.check_and_apply(self.player):
                self.player.take_damage_flash()

        for cam in self.cameras:
            cam.rotate()
            cam.detect(self.player, self.game_map)

        for term in self.terminals:
            if self.player.rect.colliderect(term.rect):
                if not term.is_hacked:
                    term.hack(self.player)

        for item in self.items[:]:
            if self.player.rect.colliderect(item.get_rect()):
                item.use(self.player)
                self.items.remove(item)


        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                p.clear()
                p.update(_new_particle(self.sw, self.sh))
                p["max_life"] = p["life"]

        if self.player.health <= 0:
            self.state = "GAMEOVER"
            return

        if self.terminals and all(t.is_hacked for t in self.terminals):
            if self.state != "WIN":
               self.state = "WIN"
               self.win_selected = 0
               if not self._win_sound_played:
                   self.sounds.play_win()
                   self._win_sound_played = True
            print("[WIN] Semua terminal berhasil diretas! Mission Complete!")

    def draw(self, screen):
        screen.fill(C_BG)
        if   self.state == "MENU":        self.menu.draw(screen)
        elif self.state == "SKIN_SELECT": self.skin_screen.draw(screen)
        elif self.state == "LOADING":     self._draw_loading(screen)
        elif self.state == "PLAYING":     self._draw_playing(screen)
        elif self.state == "PAUSED":
            self._draw_playing(screen)
            self._draw_pause_menu(screen)
        elif self.state == "WIN":
            self._draw_playing(screen)
            self._draw_win_menu(screen)
        elif self.state == "GAMEOVER":    self._draw_gameover(screen)

    def _draw_pause_menu(self, screen):
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        title = font(36, True).render("[ PAUSED ]", True, C_AMBER)
        screen.blit(title, title.get_rect(center=(self.sw // 2, self.sh // 2 - 80)))

        now = pygame.time.get_ticks()
        for i, item in enumerate(self.pause_menu_items):
            sel = (i == self.pause_selected)
            col = C_GREEN if sel else C_GREEN_DIM
            if sel:
                pulse = 0.7 + 0.3 * math.sin(now / 200)
                col = (int(255 * pulse), int(255 * pulse), int(100 * pulse))

            lbl = font(24, True).render(item, True, col)
            iy = self.sh // 2 - 20 + i * 40
            screen.blit(lbl, lbl.get_rect(center=(self.sw // 2, iy)))

        hint = font(12).render("UP/DOWN navigate   ENTER select   ESC resume", True, C_GREEN_DIM)
        screen.blit(hint, hint.get_rect(center=(self.sw // 2, self.sh - 40)))

    def _draw_win_menu(self, screen):
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        screen.blit(ov, (0, 0))

        now = pygame.time.get_ticks()

        for i in range(20):
            angle = now / 500 + i * (360 / 20)
            rx = self.sw // 2 + int(math.cos(math.radians(angle)) * 250)
            ry = self.sh // 2 + int(math.sin(math.radians(angle)) * 100)
            a = int(120 + 80 * math.sin(math.radians(angle + now / 3)))
            if a > 0:
                ps = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(ps, (255, 215, 0, a), (4, 4), 4)
                screen.blit(ps, (rx - 4, ry - 4))

        pulse = 0.7 + 0.3 * math.sin(now / 300)
        glow_col = (int(255 * pulse), int(215 * pulse), 0)

        title = font(44, True).render("[ MISSION COMPLETE ]", True, glow_col)
        screen.blit(title, title.get_rect(center=(self.sw // 2, self.sh // 2 - 80)))

        subtitle = font(16).render("All terminals hacked — system compromised!", True, C_GOLD)
        screen.blit(subtitle, subtitle.get_rect(center=(self.sw // 2, self.sh // 2 - 30)))

        num_items = len(self.win_menu_items)
        spacing = 220
        start_x = (self.sw - (num_items - 1) * spacing) // 2

        for i, item in enumerate(self.win_menu_items):
            sel = (i == self.win_selected)
            col = (int(255 * pulse), int(255 * pulse), int(100 * pulse)) if sel else C_GREEN_DIM

            lbl = font(26, True).render(item, True, col)
            ix = start_x + i * spacing
            iy = self.sh // 2 + 40
            screen.blit(lbl, lbl.get_rect(center=(ix, iy)))

            if sel:
                pygame.draw.rect(screen, col, (ix - 70, iy + 18, 140, 2), border_radius=1)

        hint = font(12).render("← → navigate     ENTER select", True, C_GREEN_DIM)
        screen.blit(hint, hint.get_rect(center=(self.sw // 2, self.sh - 40)))

    def _draw_playing(self, screen):
        self.game_map.draw(screen)

        for p in self._particles:
            ml = p.get("max_life", 120)
            if ml <= 0: continue
            a = int(140 * (p["life"] / ml))
            if a <= 0: continue
            r = max(1, p["size"])
            ps = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            hue = p.get("hue", (0, 200, 80))
            pygame.draw.circle(ps, (*hue, a), (r + 1, r + 1), r)
            screen.blit(ps, (int(p["x"]) - r, int(p["y"]) - r))

        for o in self.obstacles: o.draw(screen)
        for t in self.traps:     t.draw(screen)
        for cam in self.cameras:   cam.draw(screen)
        for term in self.terminals: term.draw(screen)
        for item in self.items:     item.draw(screen)
        for e in self.enemies:   e.draw(screen)
        self.player.draw(screen)

        screen.blit(self._vignette, (0, 0))
        screen.blit(self._scan, (0, 0))

        draw_hud(screen, self.player, self.sw, self.sh)

        hacked_count = sum(1 for t in self.terminals if t.is_hacked)
        total_count = len(self.terminals)
        term_text = font(12, True).render(f"TERMINALS: {hacked_count}/{total_count}", True, C_CYAN)
        screen.blit(term_text, (self.sw - term_text.get_width() - 14, 34))

        bar_h = 24
        pygame.draw.rect(screen, (3, 8, 3), (0, self.sh - bar_h, self.sw, bar_h))
        pygame.draw.line(screen, C_GREEN_DARK, (0, self.sh - bar_h), (self.sw, self.sh - bar_h))
        hint = font(12).render(
            "WASD/↑↓←→  move      H  hide/unhide      ESC  pause",
            True, (0, 100, 45))
        screen.blit(hint, (10, self.sh - bar_h + 5))

    def _draw_gameover(self, screen):
        self.game_map.draw(screen)
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 185))
        screen.blit(ov, (0, 0))
        screen.blit(self._vignette, (0, 0))

        now = pygame.time.get_ticks()
        pulse = 0.7 + 0.3 * math.sin(now / 400)
        col_r = (int(220 * pulse), int(30 * pulse), int(30 * pulse))

        t1 = font(40, True).render("[ MISSION FAILED ]", True, col_r)
        t2 = font(14).render("you were compromised", True, (160, 70, 70))

        screen.blit(t1, t1.get_rect(center=(self.sw // 2, self.sh // 2 - 80)))
        screen.blit(t2, t2.get_rect(center=(self.sw // 2, self.sh // 2 - 30)))

        num_items = len(self.gameover_menu_items)
        spacing = 220
        start_x = (self.sw - (num_items - 1) * spacing) // 2

        for i, item in enumerate(self.gameover_menu_items):
            sel = (i == self.gameover_selected)
            col = (int(255 * pulse), int(255 * pulse), int(100 * pulse)) if sel else C_GREEN_DIM

            lbl = font(26, True).render(item, True, col)
            ix = start_x + i * spacing
            iy = self.sh // 2 + 40
            screen.blit(lbl, lbl.get_rect(center=(ix, iy)))

            if sel:
                pygame.draw.rect(screen, col, (ix - 70, iy + 18, 140, 2), border_radius=1)

        hint = font(12).render("← → navigate     ENTER select", True, C_GREEN_DIM)
        screen.blit(hint, hint.get_rect(center=(self.sw // 2, self.sh - 40)))

    def _draw_loading(self, screen):
        now = pygame.time.get_ticks()
        elapsed = now - self._loading_start
        prog = min(1.0, elapsed / self._loading_dur)

        screen.fill((2, 4, 8))

        for col in range(0, self.sw, 16):
            if random.random() < 0.05:
                cy = random.randint(0, self.sh - 14)
                ch = chr(random.randint(33, 126))
                bright = random.randint(60, 180)
                LOAD_COLS = [(0, bright, int(bright * 0.35)), (0, int(bright * 0.35), bright),
                             (int(bright * 0.35), 0, bright), (0, bright, bright)]
                cc = LOAD_COLS[col % len(LOAD_COLS)]
                screen.blit(font(13).render(ch, True, cc), (col, cy))

        lbl_str = "> ACCESSING SYSTEM_MAIN..." if (now // 500) % 2 == 0 else "> ACCESSING SYSTEM_MAIN_"
        lbl = font(22, True).render(lbl_str, True, C_GREEN)
        screen.blit(lbl, lbl.get_rect(center=(self.sw // 2, self.sh // 2 - 50)))

        sub = font(12).render("BYPASSING_SECURITY_ALGORITHMS...", True, C_GREEN_DIM)
        screen.blit(sub, sub.get_rect(center=(self.sw // 2, self.sh // 2 - 20)))

        bw, bh = 420, 28
        bx = (self.sw - bw) // 2; by = self.sh // 2 + 10
        pygame.draw.rect(screen, (0, 30, 55), (bx - 4, by - 4, bw + 8, bh + 8), 1)
        pygame.draw.rect(screen, (2, 12, 22), (bx, by, bw, bh))

        n_blocks = 22; blk_w = (bw - 8) // n_blocks
        for i in range(int(prog * n_blocks)):
            t_frac = i / n_blocks
            r = int(0 + 60 * t_frac)
            g = int(80 + 120 * t_frac)
            b = int(180 - 60 * t_frac)
            bbx = bx + 4 + i * blk_w
            pygame.draw.rect(screen, (r, g, b), (bbx, by + 4, blk_w - 2, bh - 8), border_radius=2)
            pygame.draw.rect(screen, (min(255, r + 80), min(255, g + 80), 255),
                             (bbx, by + 4, blk_w - 2, 3), border_radius=1)

        pct = font(14, True).render(f"{int(prog * 100)}%", True, C_CYAN)
        screen.blit(pct, pct.get_rect(center=(self.sw // 2, by + bh + 18)))

        screen.blit(self._scan, (0, 0))
        screen.blit(self._vignette, (0, 0))

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 576))
    pygame.display.set_caption("Top-Down Stealth Roguelite Game")
    clock = pygame.time.Clock()
    game = Game(800, 576)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if game.handle_event(event) is False:
                    running = False
        game.handle_input()
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
