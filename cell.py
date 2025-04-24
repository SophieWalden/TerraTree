
import cell_terrain, random

IMPASSABLE_LIST = {"stump": True, "den": True, "floor": False, "kill_pile": False}

class Cell:
    def __init__(self, terrain, pos):
        self.terrain, self.pos = terrain, pos
        self.displayPos = self.pos[:]

        self.feature = None

    def get_feature_type(self):
        return "" if not self.feature else self.feature.type

    def add_feature(self, type):
        self.feature = Feature(type, IMPASSABLE_LIST[type])

    def is_feature_impassable(self):
        return self.feature and self.feature.impassable

class Feature:
    def __init__(self, type, impassable=False):
        self.type = type
        self.impassable = impassable
        self.storage = []