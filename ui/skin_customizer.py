import pygame
import math
from constants import font, SKIN_PRESETS
from entities.player import make_player_surf

class SkinCustomizer:
    def __init__(self, sw, sh, sounds=None):
        self.sw = sw; self.sh = sh
        self.selected = 0
        self.sounds = sounds
        self._preview_surfs = [make_player_surf(p) for p in SKIN_PRESETS]
        self._bg_pulse = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(SKIN_PRESETS)
                if self.sounds:
                    self.sounds.play_blip()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(SKIN_PRESETS)
                if self.sounds:
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