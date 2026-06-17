import pygame
import math
from systems.vision import VisionSystem

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

    def detect(self, player, game_map) -> bool:
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