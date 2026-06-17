import pygame
import math
from constants import font, C_GREEN, C_GREEN_DIM, C_CYAN

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