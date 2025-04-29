import random
from cat import Cat


class Faction:
    def __init__(self, id=None, z_level=None):

        self.id = id if id else random.randint(0, 100000000)
        self.positions = {"kill_pile": [0, 0]}
        self.prey = 0
        self.camp_z_level = z_level

    def create_cat(self, sprites, unit_dict, game_map):
        pos = self.generate_new_cat_position(game_map)
        while pos in unit_dict.by_pos or not game_map.is_spawnable(pos):
            pos = self.generate_new_cat_position(game_map)

        cat = Cat(sprites, pos)
        cat.faction_id = self.id
        unit_dict.by_pos[pos] = cat
        unit_dict.by_faction[self.id].append(cat)
        unit_dict.units.append(cat)
        unit_dict.by_board[self.camp_z_level].append(cat)

    def generate_new_cat_position(self, game_map):
        pos = [random.randint(0, game_map.width), random.randint(0, game_map.height), self.camp_z_level]
        pos[0] = min(max(pos[0], 0), game_map.width - 1)
        pos[1] = min(max(pos[1], 0), game_map.height - 1)

        return tuple(pos)