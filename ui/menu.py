import pygame
import math
import random
from constants import font, C_GREEN, C_GREEN_DIM, C_WHITE

class MenuScreen:
    ITEMS = ["NEW GAME", "CONTROLS", "QUIT"]

    def __init__(self, sw, sh):
        self.sw = sw; self.sh = sh
        self.selected = 0
        self._stars = [(random.randint(0, sw), random.randint(0, sh),
                        random.uniform(0.4, 1.6)) for _ in range(80)]
        self._scanlines = self._make_scanlines()
        self.show_controls = False
        self._scroll_chars = []
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