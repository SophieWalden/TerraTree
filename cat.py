import pygame, random

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
    (60, 60, 60)
]

class Cat:
    def __init__(self, sprite=None, pos=[0,0]):
        self.pos = pos
        self.display_pos = pos[:]

        self.colors = self.generate_color_palette()
        self.sprite = self.color_sprite(sprite, self.colors)
        self.name = "".join([random.choice("ABCDEFGHJIJKLMNOPQRSTUV") for _ in range(10)])
        self.size = 30
        
    def generate_color_palette(self):
        main_color = random.choice(cat_colors)
        eye_color = self.generate_color()
        highlights = self.darken(main_color, 0.7)
        shadows = self.darken(main_color, 2)

        colors = {(174, 168, 46, 255): main_color, (106, 190, 48, 255): shadows, (91, 110, 225, 255): highlights, (172, 50, 50, 255): eye_color}
        return colors


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