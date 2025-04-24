from cat import Cat
import random
from collections import defaultdict
from prey import Prey

class unit_dict:
    def __init__(self):
        self.units = []
        self.by_pos = {}
        self.by_faction = defaultdict(lambda: [])

    def spawn_prey(self, game_map):
        pos = (random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))
        while pos in self.by_pos or not game_map.is_spawnable(pos):
            pos = (random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))

        self.units.append(Prey("rat", pos))
        self.by_pos[pos] = self.units[-1]
        self.by_faction["prey"].append(self.units[-1])

    def move_unit(self, unit, new_pos):
        old_pos = unit.pos
        del self.by_pos[old_pos]

        self.by_pos[new_pos] = unit
        unit.pos = new_pos
        
    def swap_positions(self, pos, pos2):
        if pos not in self.by_pos or pos2 not in self.by_pos: return

        unit, unit2 = self.by_pos[pos], self.by_pos[pos2]
        self.by_pos[pos], self.by_pos[pos2] = self.by_pos[pos2], self.by_pos[pos]
        unit.pos, unit2.pos = unit2.pos, unit.pos