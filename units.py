from cat import Cat
import random

class unit_dict:
    def __init__(self):
        self.units = []
        self.by_pos = {}

    def add_cat(self, sprite, game_map):
        pos = (random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))
        while pos in self.by_pos:
            pos = (random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))

        self.units.append(Cat(sprite, pos))
        self.by_pos[pos] = self.units[-1]