
import cell_terrain, random
class Cell:
    def __init__(self, terrain, pos):
        self.terrain, self.pos = terrain, pos
        self.displayPos = self.pos[:]

        self.has_stump = False
        if terrain == cell_terrain.Terrain.Forest:
            self.has_stump = random.random() < 0.1