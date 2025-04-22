import pygame, os
import params
import cell_terrain
from collections import OrderedDict
import time

class LRUCache:
    def __init__(self, max_size=250):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key) 
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False) 
        self.cache[key] = value
        return value
    
TILE_IMAGES = {cell_terrain.Terrain.Grass: "grass_tile", cell_terrain.Terrain.Forest: "forest_tile"}
IMAGE_SIZE = 50

class Display:
    def __init__(self):
        self.camera_pos = [-600, -150]
        self.zoom, self.desired_zoom = round(1 * 32) / 32, round(1 * 32) / 32
        self.width, self.height = 1400, 800

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.images = self.load_images()
        self.font = pygame.freetype.Font('JetBrainsMono-Regular.ttf', 18)

        # Caches
        self.image_cache = LRUCache()
        self.text_cache = {}

        self.TILE_X_OFFSET = 24
        self.TILE_Y_OFFSET = 12

    def load_images(self):
        images = {}
        for filename in os.listdir("images"):
            full_path = f"images/{filename}"
            key = filename[:filename.index(".")]

            images[key] = pygame.image.load(full_path).convert_alpha()

        return images
    

    def fill(self, color):
        self.screen.fill(color)

    def blit(self, image, x, y, size, name=None):
        adjusted_x = x - self.camera_pos[0]
        adjusted_y = y - self.camera_pos[1]

        adjusted_x *= self.zoom
        adjusted_y *= self.zoom       
        
        if self.is_onscreen(adjusted_x, adjusted_y, size):
            if name:
                adjusted_image = self.image_cache.get((name, self.zoom))

                if adjusted_image == None:
                    adjusted_image = self.image_cache.put((name, self.zoom), pygame.transform.scale(image, (size * self.zoom, size * self.zoom)))
            else:
                adjusted_image = pygame.transform.scale(image, (size * self.zoom, size * self.zoom))

            self.screen.blit(adjusted_image, (adjusted_x, adjusted_y))

    def get_world_coordinates(self, x, y, size=IMAGE_SIZE):
        x, y = x * size, y * size

        x -= self.camera_pos[0]
        y -= self.camera_pos[1]

        x *= self.zoom
        y *= self.zoom

        return x, y
    
    def world_to_cord(self, pos):
        """Translates 2D array cords into cords for isometric rendering"""
        x = pos[0] * self.TILE_X_OFFSET - pos[1] * self.TILE_X_OFFSET
        y = pos[0] * self.TILE_Y_OFFSET + pos[1] * self.TILE_Y_OFFSET

        return (x, y)
    
    def is_onscreen(self, x, y, size):
        return x > -size * self.zoom and x < self.width and y > -size * self.zoom and y < self.height
            

    def draw_map(self, board):
        for cell in board.tiles_render_queue:
            image = self.images[TILE_IMAGES[cell.terrain]]
            x, y = self.world_to_cord((cell.pos[0], cell.pos[1]))
            self.blit(image, x, y, IMAGE_SIZE, TILE_IMAGES[cell.terrain])

    def draw_units(self, units):
        for unit in units.units:
            position = unit.display_pos
            image = unit.sprite
            size = unit.size
            
            x, y = self.world_to_cord(position)
            y -= self.TILE_Y_OFFSET
            x += self.TILE_X_OFFSET // 2
            self.blit(image, x, y, size, unit.name)

    def draw_text(self, given_surface, msg, x, y, color):
        if msg.isdigit():
            surfaces = []
            width, height = 0, 0

            for number in msg:
                surface, rect = self.text_cache[number]
                surfaces.append((surface, rect))
                width += rect[2]
                height = max(height, rect[3])

            width += 2 * len(surfaces)
            text_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            rect_x = 0
            for (surface, rect) in surfaces:
                text_surface.blit(surface, (rect_x, 0))
                rect_x += rect[2] + 2
        else:
            if msg not in self.text_cache:
                surface, rect = self.font.render(msg, color)
                self.text_cache[msg] = (surface, None)

            text_surface = self.text_cache[msg][0]


        given_surface.blit(text_surface, (x, y))

    def draw_ui(self):
        pass

    def tick(self, board):
        # Dragging
        rel, pressed, pos = pygame.mouse.get_rel(), pygame.mouse.get_pressed(), pygame.mouse.get_pos()
   
        if pressed[0]:
            self.camera_pos[0] += -rel[0] * (1 / self.zoom)
            self.camera_pos[1] += -rel[1] * (1 / self.zoom)

        # Zooming
        if abs(self.zoom - self.desired_zoom) > 0.005:
            mx, my = pos
            world_x_before = (mx / self.zoom) + self.camera_pos[0]
            world_y_before = (my / self.zoom) + self.camera_pos[1]

            self.zoom += (self.desired_zoom - self.zoom) * 1

            world_x_after = (mx / self.zoom) + self.camera_pos[0]
            world_y_after = (my / self.zoom) + self.camera_pos[1]

            self.camera_pos[0] += world_x_before - world_x_after
            self.camera_pos[1] += world_y_before - world_y_after
        else:
            self.zoom = self.desired_zoom


