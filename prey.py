from commands import MoveCommand
import random

class Prey:
    def __init__(self, type, pos):
        self.type = type
        self.pos = pos
        self.display_pos = list(pos)
        self.size = 30
        self.dead = False
        self.id = random.randint(0, 9999999999)
        self.faction_id = "prey"
        self.health = 5
        self.damage = 1

    def getMove(self, game_map):
        possible_moves = []
        
        directions = ["left", "right", "down", "up"]
        for i, move in enumerate([(-1, 0), (1, 0), (0, 1), (0, -1)]):
            new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
            
            if not game_map.in_bounds(new_pos[0], new_pos[1]): continue
            if game_map.tiles[new_pos[1]][new_pos[0]].is_feature_impassable(): continue

            possible_moves.append((new_pos, directions[i]))

        if random.random() < 0.5 or not possible_moves: return None

        move, direction = random.choice(possible_moves)
        return MoveCommand(self, move, direction)