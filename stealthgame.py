import pygame
import math
import random
from abc import ABC, abstractmethod
from typing import List, Optional

pygame.init()

def draw_pixel_art(surface: pygame.Surface, pixel_grid: list, palette: dict, scale: int = 2):
    """Menggambar pixel art dari grid huruf ke Surface."""
    for row_idx, row in enumerate(pixel_grid):
        for col_idx, char in enumerate(row):
            if char == '.':
                continue
            color = palette.get(char, (255, 0, 255, 255))
            rect = pygame.Rect(col_idx * scale, row_idx * scale, scale, scale)
            if len(color) == 4:
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (*color, 255), rect)

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
PLAYER_PALETTE = {
    'B': (30, 30, 30, 255),  
    'S': (210, 170, 120, 255), 
    'G': (20, 80, 20, 255),  
}

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
ENEMY_PATROL_PALETTE = {
    'R': (180, 30, 30, 255),   
    'W': (255, 220, 220, 255),
    'D': (80, 80, 100, 255),   
}
ENEMY_CHASE_PALETTE = {
    'R': (255, 50, 50, 255),  
    'W': (255, 255, 100, 255), 
    'D': (120, 40, 40, 255),   
}
ENEMY_SEARCH_PALETTE = {
    'R': (200, 100, 30, 255), 
    'W': (255, 220, 100, 255),
    'D': (90, 60, 30, 255),
}

def make_player_surface() -> pygame.Surface:
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_pixel_art(surf, PLAYER_PIXELS, PLAYER_PALETTE, scale=2)
    return surf

def make_enemy_surface(palette: dict) -> pygame.Surface:
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_pixel_art(surf, ENEMY_PIXELS, palette, scale=2)
    return surf

class Entity(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, speed: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def move(self, dx: float, dy: float, game_map=None):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if game_map:
            tile_x = int(new_x // 32)
            tile_y = int(new_y // 32)
            if game_map.is_walkable(tile_x, tile_y):
                self.x = new_x
                self.y = new_y
        else:
            self.x = new_x
            self.y = new_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def update(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def check_collision(self, other_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(other_rect)

class EnemyState(ABC):
    def __init__(self, state_name: str):
        self.state_name = state_name

    @abstractmethod
    def enter(self, enemy):
        pass

    @abstractmethod
    def execute(self, enemy, player):
        pass

    @abstractmethod
    def exit(self, enemy):
        pass

class PatrolState(EnemyState):
    def __init__(self):
        super().__init__("Patrol")
        self.current_point_index = 0
        self.stay_timer = 0

    def enter(self, enemy):
        enemy.alert_level = 0
        enemy.image = make_enemy_surface(ENEMY_PATROL_PALETTE)
        if enemy.patrol_points:
            self.current_point_index = 0

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            enemy.change_state(ChaseState())
            return

        if not enemy.patrol_points:
            return

        target_point = enemy.patrol_points[self.current_point_index]
        dx = target_point[0] - enemy.x
        dy = target_point[1] - enemy.y
        distance = math.hypot(dx, dy)

        if distance < 5:
            if self.stay_timer == 0:
                self.stay_timer = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.stay_timer > 1000:
                self.current_point_index = (self.current_point_index + 1) % len(enemy.patrol_points)
                self.stay_timer = 0
        else:
            enemy.move(dx / distance, dy / distance)

    def exit(self, enemy):
        pass

class ChaseState(EnemyState):
    def __init__(self):
        super().__init__("Chase")
        self.chase_speed_multiplier = 1.5
        self.last_seen_position = (0, 0)
        self.original_speed = 0

    def enter(self, enemy):
        enemy.alert_level = 100
        self.original_speed = enemy.speed
        enemy.speed = int(enemy.speed * self.chase_speed_multiplier)
        enemy.image = make_enemy_surface(ENEMY_CHASE_PALETTE)

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            self.last_seen_position = (player.x, player.y)
            self.follow_target(enemy, player.x, player.y)
        else:
            dx = self.last_seen_position[0] - enemy.x
            dy = self.last_seen_position[1] - enemy.y
            dist = math.hypot(dx, dy)

            if dist > 10:
                self.follow_target(enemy, self.last_seen_position[0], self.last_seen_position[1])
            else:
                enemy.change_state(SearchState(self.last_seen_position))

    def follow_target(self, enemy, target_x, target_y):
        dx = target_x - enemy.x
        dy = target_y - enemy.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            enemy.move(dx / distance, dy / distance)

    def exit(self, enemy):
        enemy.speed = self.original_speed

class SearchState(EnemyState):
    def __init__(self, search_position: tuple):
        super().__init__("Search")
        self.search_position = search_position
        self.search_timer = 5.0
        self.start_ticks = 0
        self.sub_target = None

    def enter(self, enemy):
        enemy.alert_level = 50
        self.start_ticks = pygame.time.get_ticks()
        self.generate_random_sub_target(enemy)
        enemy.image = make_enemy_surface(ENEMY_SEARCH_PALETTE)

    def generate_random_sub_target(self, enemy):
        radius = 80
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(20, radius)
        self.sub_target = (
            self.search_position[0] + math.cos(angle) * r,
            self.search_position[1] + math.sin(angle) * r,
        )

    def execute(self, enemy, player):
        if enemy.detect_player(player):
            enemy.change_state(ChaseState())
            return

        if (pygame.time.get_ticks() - self.start_ticks) / 1000.0 >= self.search_timer:
            enemy.change_state(PatrolState())
            return

        if self.sub_target:
            dx = self.sub_target[0] - enemy.x
            dy = self.sub_target[1] - enemy.y
            dist = math.hypot(dx, dy)
            if dist < 10:
                self.generate_random_sub_target(enemy)
            else:
                enemy.move(dx / dist, dy / dist)

    def exit(self, enemy):
        pass

class GameObject(ABC):
    def __init__(self, obj_id: int, x: int, y: int, is_interactable: bool):
        self.id = obj_id
        self.x = x
        self.y = y
        self.is_interactable = is_interactable

    @abstractmethod
    def on_interact(self):
        pass

class Trap:
    def __init__(self, x: int, y: int, damage: int = 20):
        self.x = x
        self.y = y
        self.damage = damage
        self.rect = pygame.Rect(x, y, 32, 32)
        self.is_triggered = False
        self.trigger_time = 0
        self.cooldown = 2000 

    def check_and_apply(self, player) -> bool:
        now = pygame.time.get_ticks()
        if self.is_triggered and now - self.trigger_time < self.cooldown:
            return False
        if self.rect.colliderect(player.rect):
            player.health = max(0, player.health - self.damage)
            self.is_triggered = True
            self.trigger_time = now
            return True
        return False

    def draw(self, screen: pygame.Surface):
        now = pygame.time.get_ticks()
        active = not self.is_triggered or (now - self.trigger_time >= self.cooldown)
        if active:
            pulse = abs(math.sin(now / 300))
            r = int(180 + 75 * pulse)
            pygame.draw.rect(screen, (r, 30, 30), self.rect)
            pygame.draw.line(screen, (255, 200, 200), (self.rect.x + 6, self.rect.y + 6), (self.rect.right - 6, self.rect.bottom - 6), 3)
            pygame.draw.line(screen, (255, 200, 200), (self.rect.right - 6, self.rect.y + 6), (self.rect.x + 6, self.rect.bottom - 6), 3)
        else:
            pygame.draw.rect(screen, (60, 20, 20), self.rect)
            pygame.draw.rect(screen, (100, 50, 50), self.rect, 2)

class Obstacle:
    def __init__(self, x: int, y: int, width: int = 32, height: int = 32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def blocks(self, entity_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(entity_rect)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (50, 70, 50), self.rect)
        pygame.draw.rect(screen, (80, 120, 80), self.rect, 2)
        for College in range(self.y, self.y + self.height, 10):
            pygame.draw.line(screen, (40, 60, 40), (self.x, College), (self.x + self.width, College))
        for gx in range(self.x, self.x + self.width, 16):
            pygame.draw.line(screen, (40, 60, 40), (gx, self.y), (gx, self.y + self.height))

class Player(Entity):
    def __init__(self, x: int, y: int, width: int, height: int, speed: int):
        super().__init__(x, y, width, height, speed)
        self.visibility_level: int = 100
        self.is_hidden: bool = False
        self.has_objective: bool = False
        self.health: int = 100
        self.hack_skill: int = 1
        self.image = make_player_surface()
        self._damage_flash = 0 

    def hide(self):
        self.is_hidden = True
        self.visibility_level = 0

    def interact(self, obj: GameObject):
        if obj.is_interactable:
            obj.on_interact()

    def take_damage_flash(self):
        self._damage_flash = 400 

    def update_visibility(self):
        if not self.is_hidden:
            self.visibility_level = 100

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        if self._damage_flash > 0:
            flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = int(180 * (self._damage_flash / 400))
            flash_surf.fill((255, 0, 0, alpha))
            screen.blit(flash_surf, self.rect)

class Enemy(Entity):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height, speed)
        self.image = make_enemy_surface(ENEMY_PATROL_PALETTE)
        self.alert_level = 0
        self.patrol_points = []
        self.current_state: Optional[EnemyState] = None

    def change_state(self, new_state: EnemyState):
        if self.current_state:
            self.current_state.exit(self)
        self.current_state = new_state
        self.current_state.enter(self)

    def detect_player(self, player: Player) -> bool:
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        detection_range = 150
        if player.is_hidden:
            return distance < detection_range * 0.3
        return distance < detection_range

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        if self.alert_level > 0:
            label = "!" if self.alert_level >= 100 else "?"
            color = (255, 60, 60) if self.alert_level >= 100 else (255, 200, 60)
            font = pygame.font.SysFont("Courier", 16, bold=True)
            text = font.render(label, True, color)
            screen.blit(text, (self.rect.centerx - 4, self.rect.top - 16))

    def update_enemy(self, player: Player):
        if self.current_state:
            self.current_state.execute(self, player)
        super().update()

class Tile:
    def __init__(self, x: int, y: int, is_wall: bool, texture: str):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.texture = texture

class Room:
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.objects: List[GameObject] = []

    def generate_objects(self):
        pass

class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = []
        self.rooms: List[Room] = []
        self.tile_size = 32

    def load_map(self, file_path: str):
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                is_wall = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)
                row.append(Tile(x, y, is_wall, "wall" if is_wall else "floor"))
            self.tiles.append(row)

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return not self.tiles[y][x].is_wall
        return False

    def draw(self, screen: pygame.Surface):
        WALL_COLOR = (20, 60, 20)
        FLOOR_COLOR = (8, 25, 8)
        GRID_COLOR = (12, 35, 12)
        ts = self.tile_size
        for row in self.tiles:
            for tile in row:
                rx, ry = tile.x * ts, tile.y * ts
                if tile.is_wall:
                    pygame.draw.rect(screen, WALL_COLOR, (rx, ry, ts, ts))
                    pygame.draw.rect(screen, (30, 90, 30), (rx, ry, ts, ts), 1)
                else:
                    pygame.draw.rect(screen, FLOOR_COLOR, (rx, ry, ts, ts))
                    pygame.draw.line(screen, GRID_COLOR, (rx, ry), (rx + ts, ry))
                    pygame.draw.line(screen, GRID_COLOR, (rx, ry), (rx, ry + ts))

class Item:
    def __init__(self, name: str, effect: str, value: str):
        self.name = name
        self.effect = effect
        self.value = value

    def use(self, player: Player):
        if "heal" in self.effect.lower():
            player.health = min(100, player.health + int(self.value))
        elif "hack" in self.effect.lower():
            player.hack_skill += int(self.value)

class SecurityCamera:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.vision_range = 120
        self.rotation_angle = 0
        self.is_active = True

    def rotate(self):
        if self.is_active:
            self.rotation_angle = (self.rotation_angle + 1) % 360

    def draw(self, screen):
        color = (255, 50, 50) if self.is_active else (80, 80, 80)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 10)

class Terminal:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_hacked = False
        self.hack_difficulty = random.randint(1, 5)

    def hack(self, player: Player) -> bool:
        if self.is_hacked:
            return True
        if player.hack_skill >= self.hack_difficulty:
            self.is_hacked = True
            return True
        return False

    def draw(self, screen: pygame.Surface):
        color = (0, 255, 0) if self.is_hacked else (0, 100, 255)
        pygame.draw.rect(screen, color, (self.x - 12, self.y - 12, 24, 24))

def draw_hud(screen: pygame.Surface, player: Player, font: pygame.font.Font):
    sw = screen.get_width()
    bar_w, bar_h = 160, 14
    bx, by = 12, 12
    pygame.draw.rect(screen, (40, 10, 10), (bx, by, bar_w, bar_h), border_radius=3)
    hp_ratio = player.health / 100
    hp_color = (int(200 * (1 - hp_ratio)), int(200 * hp_ratio), 30)
    pygame.draw.rect(screen, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h), border_radius=3)
    pygame.draw.rect(screen, (0, 200, 80), (bx, by, bar_w, bar_h), 1, border_radius=3)
    hp_text = font.render(f"HP {player.health}", True, (0, 220, 80))
    screen.blit(hp_text, (bx + bar_w + 8, by - 1))

    if player.is_hidden:
        hide_text = font.render("[ HIDDEN ]", True, (0, 255, 150))
        screen.blit(hide_text, (sw - 130, 12))

class Game:
    def __init__(self):
        self.state: str = "INIT"
        self.map: GameMap = GameMap(25, 18)
        self.player: Player = Player(64, 64, 32, 32, 5)
        self.enemies: List[Enemy] = []
        self.traps: List[Trap] = []
        self.obstacles: List[Obstacle] = []
        self.loading_start_time = 0
        self.loading_duration = 3000
        self.font = pygame.font.SysFont("Courier", 22, bold=True)
        self.font_small = pygame.font.SysFont("Courier", 13, bold=True)

    def start(self):
        self.state = "LOADING"
        self.loading_start_time = pygame.time.get_ticks()
        self.map.load_map("dummy_path")
        self._setup_level()

    def _setup_level(self):
        enemy1 = Enemy(400, 300, 32, 32, 2)
        enemy1.patrol_points = [(400, 300), (600, 300), (600, 450), (400, 450)]
        enemy1.change_state(PatrolState())
        self.enemies.append(enemy1)

        enemy2 = Enemy(200, 400, 32, 32, 2)
        enemy2.patrol_points = [(200, 400), (350, 400)]
        enemy2.change_state(PatrolState())
        self.enemies.append(enemy2)

        # Setup Traps
        trap_positions = [
            (160, 160), (192, 160), (224, 160),
            (320, 256), (480, 352), (512, 352), (288, 448),
        ]
        for tx, ty in trap_positions:
            self.traps.append(Trap(tx, ty, damage=15))

        obstacle_positions = [
            (256, 128, 32, 96), (384, 192, 96, 32),
            (160, 320, 32, 64), (480, 256, 32, 128),
            (320, 384, 128, 32), (96, 448, 64, 32),
        ]
        for (ox, oy, ow, oh) in obstacle_positions:
            self.obstacles.append(Obstacle(ox, oy, ow, oh))

    def _obstacle_blocks_move(self, new_x: float, new_y: float) -> bool:
        test_rect = pygame.Rect(int(new_x), int(new_y), self.player.width, self.player.height)
        for obs in self.obstacles:
            if obs.blocks(test_rect):
                return True
        return False

    def handle_input(self):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1

        if dx != 0 or dy != 0:
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
            
            new_x = self.player.x + dx * self.player.speed
            new_y = self.player.y + dy * self.player.speed
            if not self._obstacle_blocks_move(new_x, new_y):
                self.player.move(dx, dy, self.map)

        if keys[pygame.K_h]:
            self.player.is_hidden = True
            self.player.visibility_level = 0
        else:
            self.player.is_hidden = False
            self.player.update_visibility()

    def update(self):
        if self.state == "LOADING":
            if pygame.time.get_ticks() - self.loading_start_time >= self.loading_duration:
                self.state = "PLAYING"
            return

        if self.state != "PLAYING":
            return

        self.player.update()
        if self.player._damage_flash > 0:
            self.player._damage_flash -= 16

        for enemy in self.enemies:
            enemy.update_enemy(self.player)

        for trap in self.traps:
            if trap.check_and_apply(self.player):
                self.player.take_damage_flash()

        if self.player.health <= 0:
            self.state = "GAMEOVER"

    def draw(self, screen: pygame.Surface):
        screen.fill((5, 15, 5))

        if self.state == "LOADING":
            self._draw_loading(screen)
        elif self.state == "PLAYING":
            self.map.draw(screen)
            for obs in self.obstacles:
                obs.draw(screen)
            for trap in self.traps:
                trap.draw(screen)
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player.draw(screen)
            
            draw_hud(screen, self.player, self.font_small)
            hint = self.font_small.render("WASD/Arrow: gerak | H: sembunyi", True, (0, 100, 50))
            screen.blit(hint, (10, screen.get_height() - 22))
        elif self.state == "GAMEOVER":
            msg = self.font.render("[ MISSION FAILED ]", True, (255, 50, 50))
            sub = self.font_small.render("Tekan R untuk restart", True, (180, 80, 80))
            screen.blit(msg, msg.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 20)))
            screen.blit(sub, sub.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 20)))

    def _draw_loading(self, screen: pygame.Surface):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.loading_start_time
        progress = min(1.0, elapsed / self.loading_duration)

        label = "> ACCESSING SYSTEM_MAIN..." if (current_time // 500) % 2 == 0 else "> ACCESSING SYSTEM_MAIN"
        text_surface = self.font.render(label, True, (0, 255, 100))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
        screen.blit(text_surface, text_rect)

        bar_width, bar_height = 400, 30
        bar_x = (screen.get_width() - bar_width) // 2
        bar_y = screen.get_height() // 2 + 10

        pygame.draw.rect(screen, (0, 100, 50), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
        pygame.draw.rect(screen, (0, 60, 30), (bar_x - 6, bar_y - 6, bar_width + 12, bar_height + 12), 1, border_radius=8)

        num_blocks = 20
        block_width = (bar_width - 10) // num_blocks
        for i in range(int(progress * num_blocks)):
            green_shade = int(150 + (i / num_blocks) * 105)
            bx = bar_x + 5 + i * block_width
            by = bar_y + 5
            pygame.draw.rect(screen, (0, green_shade, 50), (bx, by, block_width - 2, bar_height - 10), border_radius=2)
            pygame.draw.rect(screen, (100, 255, 150), (bx, by, block_width - 2, 3))

        pct = self.font.render(f"{int(progress * 100)}%", True, (0, 255, 100))
        screen.blit(pct, pct.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 25)))
        sub = self.font_small.render("BYPASSING_SECURITY_ALGORITHMS...", True, (0, 120, 60))
        screen.blit(sub, (bar_x, bar_y - 20))

    def restart(self):
        self.player = Player(64, 64, 32, 32, 5)
        self.enemies = []
        self.traps = []
        self.obstacles = []
        self._setup_level()
        self.state = "PLAYING"
        
if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 576))
    pygame.display.set_caption("Stealth Game v2 - Integrated")
    fps_clock = pygame.time.Clock()
    
    game = Game()
    game.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.state == "GAMEOVER":
                    game.restart()

        game.handle_input()
        game.update()
        game.draw(screen)
        
        pygame.display.flip()
        fps_clock.tick(60)

    pygame.quit()