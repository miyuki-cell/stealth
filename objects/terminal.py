import pygame
from constants import font

class Terminal:
    def __init__(self, x: int, y: int, hack_difficulty: int = 1):
        self.x = x
        self.y = y
        self.is_hacked: bool = False
        self.hack_difficulty: int = hack_difficulty
        self.rect = pygame.Rect(x, y, 24, 24)

    def hack(self, player) -> bool:
        if self.is_hacked:
            return True
        if player.hack_skill >= self.hack_difficulty:
            self.is_hacked = True
            print(f"[TERMINAL] ({self.x},{self.y}) berhasil diretas!")
            return True
        print(f"[TERMINAL] Gagal — skill {player.hack_skill} < {self.hack_difficulty}")
        return False

    def on_interact(self, player):
        self.hack(player)

    def draw(self, screen: pygame.Surface):
        color = (0, 200, 100) if self.is_hacked else (200, 50, 50)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        lbl = font(9, True).render("TRM", True, (255, 255, 255))
        screen.blit(lbl, (self.x + 2, self.y + 7))