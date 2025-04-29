import cell_terrain
import random
from cell import Cell
import params
import faction

TERRAIN_TRANSLATION = {0: cell_terrain.Terrain.Grass, 1: cell_terrain.Terrain.Forest}

class GameMap:
    def __init__(self, width, height, z):
        self.width, self.height = width, height
        self.tiles = self.generate_board(self.width, self.height)
        self.tiles_render_queue = self.generate_render_queue(self.tiles)
        self.z_level = z
    
    def generate_render_queue(self, tiles):
        flat_tiles = []

        for j, row in enumerate(tiles):
            for i, tile in enumerate(row):
                flat_tiles.append(((i, j), tile))
            
        flat_tiles.sort(key = lambda x: x[0][0] + x[0][1])
        return [tile[1] for tile in flat_tiles]

    def in_bounds(self, x, y):
        return x >= 0 and x < len(self.tiles[0]) and y >= 0 and y < len(self.tiles) 
    
    def gen_faction(self, type):
        def dist(p1, p2):
            return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5
        
        def get_free_spot(den):
            position = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            while den[position[1]][position[0]] != 0:
                position = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))

            return position


        createdFaction = faction.Faction(z_level=self.z_level)
        if type == "camp":
            

            dens = self.generate_dens(self.width)
            for j, row in enumerate(dens):
                for i, tile in enumerate(row):
                    if tile == "wall": self.tiles[j][i].add_feature("den")
                    elif tile == "floor": self.tiles[j][i].add_feature("floor")

            createdFaction.positions["kill_pile"] = get_free_spot(dens) 
            self.tiles[createdFaction.positions["kill_pile"][1]][createdFaction.positions["kill_pile"][0]].add_feature("kill_pile")

        return createdFaction

    def gen_factions(self):

        def dist(p1, p2):
            return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5

        factions = {}
        camp_positions = set([])
        for _ in range(params.FACTION_COUNT):
            createdFaction = faction.Faction()

            faction_size = 20
            camp_position = (random.randint(faction_size/2, self.width-faction_size/2), random.randint(faction_size, self.height - faction_size/2))
            while any(dist(camp_position, pos) < self.width // 3 for pos in camp_positions):
                camp_position = (random.randint(faction_size/2, self.width-faction_size/2), random.randint(faction_size, self.height - faction_size/2))

            dens = self.generate_dens(faction_size)
            

            kill_pile_unplaced = True
            for j, row in enumerate(dens):
                for i, tile in enumerate(row):
                    position = (camp_position[0] + i - 10, camp_position[1] + j - 10)
                    if tile == "wall": self.tiles[position[1]][position[0]].add_feature("den")
                    elif tile == "floor": self.tiles[position[1]][position[0]].add_feature("floor")
                    elif kill_pile_unplaced:
                        kill_pile_unplaced = False
                        self.tiles[position[1]][position[0]].add_feature("kill_pile")
                        createdFaction.positions["kill_pile"] = [position[0], position[1]]

            

            createdFaction.camp_pos = camp_position
            camp_positions.add(camp_position)
            factions[createdFaction.id] = createdFaction

        return factions
    
    def is_spawnable(self, position):
        return self.tiles[position[1]][position[0]].get_feature_type() == "" or not self.tiles[position[1]][position[0]].feature.impassable
    
    def generate_dens(self, size):
        board = [[0] * size for _ in range(size)]

        def den_not_free(pos, size):
            for j in range(pos[1], pos[1] + size):
                for i in range(pos[0], pos[0] + size):
                    if i >= len(board[0]) or j >= len(board): return True
                    if board[j][i] != 0: return True
            
            return False

        dens = [["leader", 3], ["medicine", 4], ["warrior", 4], ["apprentice", 3], ["elder", 3], ["nursery", 5]]
        for name, den_size in dens:
            position = (random.randint(0, size - 1), random.randint(0, size - 1))
            while den_not_free(position, den_size):
                position = (random.randint(0, size - 1), random.randint(0, size - 1))

            for j in range(position[1], position[1] + den_size):
                for i in range(position[0], position[0] + den_size):
                    quadrant = [position[0] // (size / 2), position[1] // (size / 2)]

                    if ((i == position[0] and not quadrant[0]) 
                       or (j == position[1] and not quadrant[1]) or 
                       (i == position[0] + den_size - 1 and quadrant[0]) or 
                       (j == position[1] + den_size - 1 and quadrant[1])):
                        board[j][i] = "wall"
                    else:
                        board[j][i] = "floor"
        
        return board
            

    def generate_board(self, width, height):
        board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        noise = [[random.random() for _ in range(self.width)] for _ in range(self.height)]
        
        noise = self.smooth(noise, 4)

        for j, row in enumerate(noise):
            for i, tile in enumerate(row):
                if noise[j][i] > 0.5:
                    board[j][i] = 1
                else: 
                    board[j][i] = 0
            
        # Get rid of isolated water tiles
        board = self.remove_isolated(board, 2, 5)
        
        for j, row in enumerate(board):
            for i, tile in enumerate(row):
                board[j][i] = Cell(TERRAIN_TRANSLATION[tile], (i, j))


        return board
    
    def smooth(self, board, depth):
        new_board = [[0] * len(board[0]) for _ in range(len(board))]

        for y, row in enumerate(board):
            for x, tile in enumerate(row):
                count = 0

                for j in range(-depth, depth + 1):
                    for i in range(-depth, depth + 1):

                        new_x, new_y = i + x, j + y
                        new_x %= len(row)
                        new_y %= len(board)
                        new_board[y][x] += board[new_y][new_x]
                        count += 1

                new_board[y][x] /= count

        return new_board

    def remove_isolated(self, board, terrain, minimum_amount):
        """
            Performs floodfill and removes terrain if there isn't atleast minimum_amount connected
        """

        seen_nodes = set([])

        for j, row in enumerate(board):
            for i, tile in enumerate(row):

                if (i, j) not in seen_nodes and board[j][i] == terrain:
                    seen_nodes.add((i, j))
                    current_fill = [(i, j)]
                    queue = [(i, j)]

                    while queue:
                        x, y = queue.pop(0)

                        for dir_x, dir_y in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
                            new_x, new_y = dir_x + x, dir_y + y
                

                            if new_x in range(len(board[0])) and new_y in range(len(board)) and board[new_y][new_x] == terrain and (new_x, new_y) not in seen_nodes:
                                seen_nodes.add((new_x, new_y))
                                queue.append((new_x, new_y))
                                current_fill.append((new_x, new_y))

                    if len(current_fill) < minimum_amount:
                        for (x, y) in current_fill:
                            board[y][x] = 0
                        

        return board
    
