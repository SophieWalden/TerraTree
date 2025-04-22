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

    def move_unit(self, unit, new_pos):
        old_pos = unit.pos
        del self.by_pos[old_pos]

        self.by_pos[new_pos] = unit
        unit.pos = new_pos
        