import sys, time
import params

import pygame
from pygame.locals import *
import game_map
import display
import cell_terrain
import random 
import units
from commands import MoveCommand
pygame.init()


class Game:
    def __init__(self, display=None):
        self.display = display
        self.fpsClock = pygame.time.Clock()
        
        self.units = units.unit_dict()
        self.board = game_map.GameMap()
        self.reset = False

        self.speed = 512
        self.ticks = 0

        cat_sprites = {key: self.display.images[f"cat_sprite_{key}"] for key in ["left", "right", "down", "up"]}
        for _ in range(int(self.board.width * self.board.height * 0.1)):
            self.units.add_cat(cat_sprites, self.board)

    def event_handling(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self.display.width, self.display.height = event.w, event.h
                self.display.screen = pygame.display.set_mode((event.w, event.h),
                                            pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_val = min(max(event.y, -3), 3)/6 + 1
                self.display.desired_zoom = max(min(scroll_val * self.display.desired_zoom, 10), 0.5)
                self.display.desired_zoom = round(self.display.desired_zoom * 50) / 50

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset = True
                elif event.key == pygame.K_LEFT:
                    self.speed = max(self.speed // 2, 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.speed = min(self.speed * 2, 1024)
                elif event.key == pygame.K_DOWN:
                    self.display.agent_tracking = random.choice(self.units.units)

                # elif event.key == pygame.K_u:
                #     self.display.TILE_X_OFFSET -= 1
                # elif event.key == pygame.K_i:
                #     self.display.TILE_X_OFFSET += 1
                # elif event.key == pygame.K_o:
                #     self.display.TILE_Y_OFFSET -= 1
                # elif event.key == pygame.K_p:
                #     self.display.TILE_Y_OFFSET += 1

        if not self.display.agent_tracking_cooldown and time.perf_counter() - self.display.drag_time < 0.1:
            pos, pressed = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
            for unit in self.units.units:
                x, y, visible = self.display.get_unit_pos(unit)

                if visible and x < pos[0] < x + 50 * self.display.zoom and y < pos[1] < y + 50 * self.display.zoom and pressed[0]:
                    self.display.agent_tracking = unit
                    self.display.agent_tracking_cooldown = True
                    print(unit.name)


    def draw(self):
        self.display.fill("#121212")
        self.display.draw_map(self.board)
        self.display.tick(self.board, self.units.units)
        
        self.display.draw_units(self.units)
        self.display.handle_unit_animation(self.units)

        pygame.display.flip()

    def cat_logic(self, dt):
        """Handles all of the calling, movement, and functions of the cats"""

        self.ticks += dt

        while self.ticks > self.speed:
            commands = []
            for cat in self.units.units:
                commands.append(cat.getMove(self.board))

            random.shuffle(commands)

            for command in commands:
                if type(command) == MoveCommand:
                    unit, position = command.unit, command.pos
                    if position in self.units.by_pos: continue

                    self.units.move_unit(unit, position)
                    unit.direction = command.direction

            self.ticks -= self.speed

    def main_loop(self):
        dt = 1/100000
        while not self.reset:
            self.event_handling()
            self.draw()
            self.cat_logic(dt)
            dt = self.fpsClock.tick(params.FPS)
      

import cProfile, pstats

if __name__ == "__main__":
    display = display.Display()

    while True:
        # profiler = cProfile.Profile()
        # profiler.enable()

        Game(display).main_loop()

        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats("tottime")
        # stats.print_stats(30)