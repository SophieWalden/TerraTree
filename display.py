import pygame, os
import params
import cell_terrain
from collections import OrderedDict
import time
from cat import Cat

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
FEATURE_IMAGES = {"stump": "tree_tile", "den": "den_wall_tile", "floor": "den_floor", "kill_pile": "kill_pile"}
PREY_SPRITES = {"rat": "rat_sprite"}
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

        self.agent_tracking = None
        self.tracking_wanted_pos = [0, 0]
        self.agent_tracking_cooldown = False
        self.drag_time = time.perf_counter()
        self.drag_cooldown = False
        self.speed = 512

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
        
    def get_unit_pos(self, unit):
        display_pos = unit.display_pos
        display_pos = self.world_to_cord(display_pos)
        x, y = display_pos
        y -= self.TILE_Y_OFFSET
        x += self.TILE_X_OFFSET // 2
        
        x, y = x - self.camera_pos[0], y - self.camera_pos[1]
        x *= self.zoom
        y *= self.zoom

        visible = self.is_onscreen(x, y, unit.size)

        return x, y, visible
    
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


        for cell in board.tiles_render_queue:
            feature_type = cell.get_feature_type()
            if feature_type:
                image = self.images[FEATURE_IMAGES[feature_type]]
                x, y = self.world_to_cord((cell.pos[0] - 1, cell.pos[1] - 1))
                self.blit(image, x, y, 50, feature_type)

    def draw_units(self, units):
        for unit in units.units:
            position = unit.display_pos

            if type(unit) == Cat:
                sprite_name = f"{unit.id}_{unit.direction}"
                image = unit.sprites[unit.direction]
            else:
                sprite_name = unit.type
                image = self.images[PREY_SPRITES[unit.type]]

            size = unit.size
            
            x, y = self.world_to_cord(position)
            y -= self.TILE_Y_OFFSET
            x += self.TILE_X_OFFSET // 2
            self.blit(image, x, y, size, sprite_name)


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
        if self.agent_tracking:
            unit = self.agent_tracking
            x, y, visible = self.get_unit_pos(unit)

            start_x, start_y = x - 150 + (self.agent_tracking.size*self.zoom)/2, y - 180 + (self.agent_tracking.size*self.zoom)/4
            self.draw_rect_advanced((210, 180, 140), 240, start_x, start_y, 300, 170, ((180, 140, 120), 10))
            pygame.draw.polygon(self.screen, (180, 140, 120), [(start_x + 100, start_y + 170), (start_x +200, start_y + 170), (start_x + 150, start_y + 185)])
            self.draw_text(self.screen, unit.name, start_x + 10, start_y + 10, (0, 0, 0))
            pygame.draw.line(self.screen, (20, 20, 20), (start_x + 10, start_y + 30), (start_x + 290, start_y + 30))

            for i, trait in enumerate(unit.traits):
                self.draw_text(self.screen, trait, start_x + 10, start_y + 40 + 20 * i, (0, 0, 0))

    def draw_rect_advanced(self, color, opacity, x, y, width, height, outline=None):
        surface = pygame.Surface((width, height))
        surface.set_alpha(opacity)
        if not outline: surface.fill((color))
        else:
            outline_color, width = outline
            surface.fill(outline_color)
            surface.fill(color, surface.get_rect().inflate(-width, -width))

        self.screen.blit(surface, (x, y))

    def handle_unit_animation(self, unit_dict):        
        for unit in unit_dict.units:
            dx, dy = unit.pos[0] - unit.display_pos[0], unit.pos[1] - unit.display_pos[1]

            if abs(dx) + abs(dy) < 0.01:
                unit.display_pos = list(unit.pos)
                continue
                
            unit.display_pos[0] += dx * 0.1
            unit.display_pos[1] += dy * 0.1


    def tick(self, board, units):
        # Dragging
        rel, pressed, pos = pygame.mouse.get_rel(), pygame.mouse.get_pressed(), pygame.mouse.get_pos()

        if pressed[0] and self.agent_tracking == None:
            self.camera_pos[0] += -rel[0] * (1 / self.zoom)
            self.camera_pos[1] += -rel[1] * (1 / self.zoom)
        elif self.agent_tracking != None:
            self.tracking_wanted_pos = self.agent_tracking.display_pos[:]
            x, y = self.world_to_cord(self.tracking_wanted_pos)
            y -= self.TILE_Y_OFFSET
            x += self.TILE_X_OFFSET // 2
            self.tracking_wanted_pos = [x, y]
            self.tracking_wanted_pos[0] -= (self.width /self.zoom) // 2
            self.tracking_wanted_pos[1] -= (self.height /self.zoom) // 2

            if pressed[0] and not self.agent_tracking_cooldown: self.agent_tracking = None
        if not pressed[0]: self.agent_tracking_cooldown = False

        if self.agent_tracking != None:
            if abs(self.camera_pos[0] - self.tracking_wanted_pos[0]) + abs(self.camera_pos[1] - self.tracking_wanted_pos[1]) > 0.1:
                dx, dy = self.camera_pos[0] - self.tracking_wanted_pos[0], self.camera_pos[1] - self.tracking_wanted_pos[1]

                self.camera_pos[0] -= dx * 0.05
                self.camera_pos[1] -= dy * 0.05

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


        if pressed[0] and not self.drag_cooldown: 
            self.drag_time = time.perf_counter()
            self.drag_cooldown = True
        
        if not pressed[0]: self.drag_cooldown = False