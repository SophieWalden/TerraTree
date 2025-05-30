import pygame, random
from commands import MoveCommand
import cell_terrain
import math
import heapq
from collections import defaultdict

cat_colors = [
    (210, 161, 92),
    (180, 140, 110),
    (140, 110, 90),
    (230, 230, 230),
    (180, 180, 180),
    (100, 100, 100),
    (250, 250, 250),
    (20, 20, 20),
    (140, 70, 40),
    (190, 170, 140),
    (255, 240, 200),
    (200, 180, 160),
    (150, 130, 100),
    (220, 220, 220),
    (60, 60, 60),
    (160, 120, 90),
    (120, 100, 80),
    (200, 200, 210),
    (240, 230, 220),
    (170, 150, 120),
    (110, 90, 70),
    (130, 130, 130),
    (90, 70, 60),
    (255, 220, 180),
    (100, 80, 120),
    (180, 160, 130),
    (240, 200, 160),
    (210, 190, 150),
    (80, 60, 40),
    (190, 170, 180)
]


name_prefixes = [
    "Ash", "Birch", "Cloud", "Dark", "Dawn", "Eagle", "Frost", "Gorse", "Hawk", "Ice",
    "Jagged", "Leaf", "Mist", "Night", "Otter", "Pine", "Quick", "Rain", "Snow", "Thistle",
    "Vine", "Willow", "Yew", "Red", "Brindle", "Silent", "Larch", "Stone", "Swift", "Golden"
]

name_suffixes = [
    "tail", "foot", "pelt", "claw", "fur", "stripe", "eye", "fang", "storm", "shade",
    "breeze", "heart", "nose", "whisker", "thorn", "light", "fall", "shine", "leaf", "strike"
]

personality = [
    "Calm",
    "Energetic",
    "Reserved",
    "Outgoing",
    "Bold",
    "Timid",
    "Loyal",
    "Rebellious",
    "Confident",
    "Anxious",
    "Gentle",
    "Clever",
    "Naive",
    "Honest",
    "Secretive"
]

social_traits = [
    "Friendly",
    "Aloof",
    "Charismatic",
    "Awkward",
    "Empathetic",
    "Jealous",
    "Competitive",
    "Supportive",
    "Independent",
    "Clingy",
    "Leaderly",
    "Follower",
    "Distrustful",
    "Trusting"
]

quirks = [
    "Talks to self",
    "Collects things",
    "Stares often",
    "Vivid dreams",
    "Fidgets often",
    "Loves symmetry",
    "Sleeps oddly",
    "Hums while working",
    "Argues with air",
    "Fears insects",
    "Loves storms",
    "Follows others",
    "Eats fast",
    "Never blinks"
]

combat_style = [
    "Aggressive",
    "Defensive",
    "Strategic",
    "Reckless",
    "Cautious",
    "Chaotic",
    "Calculated",
    "Showy",
    "Stealthy",
    "Protective"
]

role_attitude = [
    "Role-devoted",
    "Questions orders",
    "Aspires to lead",
    "Lazy worker",
    "Proud of role",
    "Wants role change",
    "Feels unneeded",
    "Seeks more power"
]

bonding_style = [
    "Bonds quickly",
    "Slow to trust",
    "Easily hurt",
    "Loyal forever",
    "Shallow bonds",
    "Avoids connection",
    "Trusts only kin",
    "Needs approval"
]


class Cat:
    def __init__(self, sprites={}, pos=[0,0,0]):
        self.pos = pos
        self.display_pos = list(pos)

        self.colors = self.generate_color_palette()

        self.sprites = {}
        for key, val in sprites.items():
            self.sprites[key] = self.color_sprite(val, self.colors)
     
        self.id = random.randint(0, 999999999999)
        self.name = self.generate_name()
        self.size = 30
        self.faction_id = None

        self.direction = "left"

        self.agility_stat = random.random()
        self.health, self.damage = random.randint(8, 20), random.randint(3, 8)
        self.dead = False
        self.hunger = 1000
        self.prey = 0

        self.traits = [random.choice(personality), random.choice(social_traits), random.choice(quirks), random.choice(combat_style), random.choice(role_attitude), random.choice(bonding_style)]
        self.goal = "hunt"
        self.hunt_target = None

        self.path = {}
        
    def generate_color_palette(self):
        main_color = random.choice(cat_colors)
        eye_color = self.generate_color()
        highlights = self.darken(main_color, random.uniform(0.3, 1.5))
        shadows = self.darken(main_color, random.uniform(1, 3))

        colors = {(174, 168, 46, 255): main_color, (106, 190, 48, 255): shadows, (91, 110, 225, 255): highlights, (172, 50, 50, 255): eye_color}
        return colors

    def generate_name(self):
        return random.choice(name_prefixes) + random.choice(name_suffixes)

    def generate_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def darken(self, color, amount):
        new_color = list(color)
        for i in range(len(new_color)):
            new_color[i] = min(max(new_color[i] * amount, 0), 255)
        
        return new_color

    def color_sprite(self, surface, color_map):
        surface = surface.copy()

        pixel_array = pygame.PixelArray(surface)
        for src_rgb, dst_rgb in color_map.items():
            src_color = surface.map_rgb(src_rgb)
            dst_color = surface.map_rgb(dst_rgb)
            pixel_array.replace(src_color, dst_color)

        del pixel_array 
        return surface

    # def getMove(self, game_map, factions, unit_dict):
    #     if "target" in self.path and self.pos == self.path["target"]:
    #         self.path = None
        
    #     if self.path:
    #         return MoveCommand(self, self.path[self.pos])

    #     start, goal = self.pos, self.get_target(game_map, factions, unit_dict)
    #     directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    #     open_set = []
    #     heapq.heappush(open_set, (self.dist(start, goal), 0, start))
    #     came_from = {}
    #     g_score = defaultdict(lambda: float("inf"))
    #     g_score[start] = 0

    #     while open_set:
    #         _, cost, current = heapq.heappop(open_set)

    #         if current == goal:
    #             path = {"target": goal}
    #             while current in came_from:
    #                 path[came_from[current]] = current
    #                 current = came_from[current]
                
    #             self.path = path
    #             return None if len(self.path) <= 1 else MoveCommand(self, self.path[self.pos])
        
    #         for dx, dy in directions:
    #             neighbor = (current[0] + dx, current[1] + dy)
    #             if not game_map.in_bounds(neighbor[0], neighbor[1]): continue
    #             if game_map.tiles[neighbor[1]][neighbor[0]].is_feature_impassable(): continue

    #             tentative_g_score = g_score[current] + 1
    #             if tentative_g_score < g_score[neighbor]:
    #                 came_from[neighbor] = current
    #                 g_score[neighbor] = tentative_g_score
    #                 f_score = tentative_g_score + self.dist(neighbor, goal)
    #                 heapq.heappush(open_set, (f_score, tentative_g_score, neighbor))

    #     self.path = {}
    
    # def dist(self, p1, p2):
    #         return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) **.5

    # def get_target(self, game_map, factions, unit_dict):
    #     if self.hunt_target and self.hunt_target.dead: self.hunt_target = None

    #     if self.hunt_target == None:
    #         for unit in unit_dict.by_faction["prey"]:
    #             if self.dist(self.pos, unit.pos) < 40:
    #                 self.hunt_target = unit
    #                 break
        
    #     target_position = self.pos
    #     if self.hunt_target:
    #         target_position = self.hunt_target.pos
    #     if self.prey > 0 or (self.hunger < 200 and factions[self.faction_id].prey > 0):
    #         target_position = factions[self.faction_id].positions["kill_pile"]

    #     return target_position


    def getMove(self, game_map, factions, unit_dict):

        def dist(p1, p2):
            return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) **.5

        if self.hunt_target and self.hunt_target.dead: self.hunt_target = None

        if self.hunt_target == None:
            for unit in unit_dict.by_faction["prey"]:
                if dist(self.pos, unit.pos) < 40:
                    self.hunt_target = unit
                    break
        
        target_position = self.pos
        if self.hunt_target:
            target_position = self.hunt_target.pos
        if self.prey > 0 or (self.hunger < 200 and factions[self.faction_id].prey > 0):
            target_position = factions[self.faction_id].positions["kill_pile"]
    

        best_move = None
        distance = math.inf
        
        directions = ["left", "right", "down", "up"]
        for i, move in enumerate([(-1, 0), (1, 0), (0, 1), (0, -1)]):
            new_pos = (self.pos[0] + move[0], self.pos[1] + move[1], self.pos[2])
            
            if not game_map.in_bounds(new_pos[0], new_pos[1]): continue
            if game_map.tiles[new_pos[1]][new_pos[0]].is_feature_impassable(): continue

            computed_dist = dist(new_pos, target_position)
            if computed_dist < distance and random.random() < 0.5:
                best_move = (new_pos, directions[i])
                distance = computed_dist


        if random.random() < self.agility_stat or not best_move: return None

        move, direction = best_move
        return MoveCommand(self, move)