import pygame
from constants import font

class Item:
    def __init__(self, x: int, y: int,
                 name: str, effect: str, value: str):
        self.x = x
        self.y = y
        self.name: str = name
        self.effect: str = effect
        self.value: str = value

    def use(self, player) -> None:
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