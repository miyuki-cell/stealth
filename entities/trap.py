import pygame
import math
import random

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