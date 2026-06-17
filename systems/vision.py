import math

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