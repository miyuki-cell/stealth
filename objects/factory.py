import random
from entities.enemy import Enemy, PatrolState
from entities.item import Item
from objects.terminal import Terminal
from objects.camera import SecurityCamera
from systems.vision import VisionSystem

class ObjectFactory:
    def __init__(self, difficulty_level: int = 1):
        self.enemy_types = ["guard", "patrol"]
        self.item_types = ["medkit", "hack_tool", "cloak"]
        self.difficulty_level = difficulty_level

    def create_enemy(self, x=0, y=0, patrol_points=None) -> Enemy:
        e = Enemy(x, y, speed=1 + self.difficulty_level)
        e.patrol_points = patrol_points or []
        e.vision_range = 100 + self.difficulty_level * 20
        e.health = 50 + self.difficulty_level * 25
        e._vision = VisionSystem(max_distance=e.vision_range)
        e.change_state(PatrolState())
        return e

    def create_item(self, x=0, y=0) -> Item:
        kind = random.choice(self.item_types)
        if kind == "medkit":
            return Item(x, y, "Medkit", "heal", "30")
        elif kind == "hack_tool":
            return Item(x, y, "HackTool", "hack_boost", "1")
        else:
            return Item(x, y, "Cloak", "stealth", "1")

    def create_terminal(self, x=0, y=0) -> Terminal:
        return Terminal(x, y, hack_difficulty=self.difficulty_level)

    def create_camera(self, x=0, y=0) -> SecurityCamera:
        return SecurityCamera(x, y, vision_range=80 + self.difficulty_level * 15)