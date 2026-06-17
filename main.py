import pygame
import math
import random
from constants import (
    TILE, C_BG, C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
    C_AMBER, C_CYAN, C_GOLD, SKIN_PRESETS, font
)
from utils import _new_particle
from entities import Player, Enemy, Trap, Item
from entities.enemy import PatrolState, ChaseState
from objects import Obstacle, Terminal, SecurityCamera, ObjectFactory
from maps import GameMap
from systems import SoundManager
from ui import MenuScreen, SkinCustomizer, draw_hud

class Game:
    def __init__(self, sw=800, sh=576):
        self.sw = sw; self.sh = sh
        self.state = "MENU"
        self.game_map = GameMap(25, 18)
        self.player = Player(64, 64)

        self.enemies = []
        self.traps = []
        self.obstacles = []
        self.cameras = []
        self.terminals = []
        self.items = []

        self._factory = ObjectFactory()
        self.menu = MenuScreen(sw, sh)
        self.sounds = SoundManager()
        self.skin_screen = SkinCustomizer(sw, sh, sounds=self.sounds)
        self._particles = []
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