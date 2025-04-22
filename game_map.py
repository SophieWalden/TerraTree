import cell_terrain
import random
from cell import Cell
import params

TERRAIN_TRANSLATION = {0: cell_terrain.Terrain.Grass, 1: cell_terrain.Terrain.Forest}

class GameMap:
    def __init__(self):
        self.width, self.height = params.BOARD_WIDTH, params.BOARD_HEIGHT
        self.tiles = self.generate_board(self.width, self.height)
        self.tiles_render_queue = self.generate_render_queue(self.tiles)
    
    def generate_render_queue(self, tiles):
        flat_tiles = []

        for j, row in enumerate(tiles):
            for i, tile in enumerate(row):
                flat_tiles.append(((i, j), tile))
            
        flat_tiles.sort(key = lambda x: x[0][0] + x[0][1])
        return [tile[1] for tile in flat_tiles]

    def in_bounds(self, x, y):
        return x >= 0 and x < len(self.tiles[0]) and y >= 0 and y < len(self.tiles) 
    

    def generate_board(self, width, height):
        board = [[0] * width for _ in range(height)]
        
        for j in range(len(board)):
            for i in range(len(board[0])):
                board[j][i] = Cell(TERRAIN_TRANSLATION[random.randint(0, 1)], (i, j))

        return board
    

class Chunk:
    def __init__(self, size=16):
        self.tiles, self.size = [], size
        self.background_tiles = []
        self.rendered = None
        self.render_update = False

    def add_tile(self, cell):
        self.tiles.append(cell)
        cell.chunk = self
    
    def add_background_tile(self, cell):
        self.background_tiles.append(cell)