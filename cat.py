import pygame, random
from commands import MoveCommand
import cell_terrain

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
    def __init__(self, sprites={}, pos=[0,0]):
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

        self.traits = [random.choice(personality), random.choice(social_traits), random.choice(quirks), random.choice(combat_style), random.choice(role_attitude), random.choice(bonding_style)]
        
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
    

    def getMove(self, game_map):
        possible_moves = []
        
        directions = ["left", "right", "down", "up"]
        for i, move in enumerate([(-1, 0), (1, 0), (0, 1), (0, -1)]):
            new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
            
            if not game_map.in_bounds(new_pos[0], new_pos[1]): continue
            if game_map.tiles[new_pos[1]][new_pos[0]].has_stump: continue

            possible_moves.append((new_pos, directions[i]))

        if random.random() < self.agility_stat or not possible_moves: return None

        move, direction = random.choice(possible_moves)
        return MoveCommand(self, move, direction)