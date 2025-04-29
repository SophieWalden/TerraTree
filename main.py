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
from simulator import Simulator
from cat import Cat
from faction import Faction


class Game:
    def __init__(self, display=None):
        self.display = display
        self.fpsClock = pygame.time.Clock()
        
        self.units = units.unit_dict()
        self.boards = {}

        for i in range(params.FACTION_COUNT):
            self.boards[i] = game_map.GameMap(20, 20, i)

        self.reset = False

        cat_sprites = {key: self.display.images[f"cat_sprite_{key}"] for key in ["left", "right", "down", "up"]}
        self.factions = {}
        for key, board in self.boards.items():
            faction = board.gen_faction("camp")

            self.factions[faction.id] = faction
             

            for _ in range(25):
                faction.create_cat(cat_sprites, self.units, board)

            self.display.board_viewing = board.z_level
        

        self.factions["prey"] = Faction("prey")
        

        self.simulator = Simulator(self.units, self.boards, self.display, self.factions)
        

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
                self.display.desired_zoom = round(self.display.desired_zoom * 12) / 12

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset = True
                elif event.key == pygame.K_LEFT:
                    self.display.speed = max(self.display.speed // 2, 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.display.speed = min(self.display.speed * 2, 1024)
                elif event.key == pygame.K_DOWN:
                    keys = list(self.boards.keys())
                    board_index = keys.index(self.display.board_viewing)
                    board_index -= 1
                    board_index %= len(keys)
                    self.display.board_viewing = keys[board_index]
                elif event.key == pygame.K_UP:
                    keys = list(self.boards.keys())
                    board_index = keys.index(self.display.board_viewing)
                    board_index += 1
                    board_index %= len(keys)
                    self.display.board_viewing = keys[board_index]

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
            for unit in self.units.by_board[self.display.board_viewing]:
                if type(unit) != Cat: continue
                x, y, visible = self.display.get_unit_pos(unit)

                if visible and x < pos[0] < x + unit.size * self.display.zoom and y < pos[1] < y + unit.size * self.display.zoom and pressed[0]:
                    self.display.agent_tracking = unit
                    self.display.agent_tracking_cooldown = True


    def draw(self):
        self.display.tick(self.boards, self.units.units)
        self.display.fill("#121212")
        self.display.draw_map(self.boards)
        
        
        self.display.draw_units(self.units)
        self.display.handle_unit_animation(self.units)
        self.display.draw_ui()

        pygame.display.flip()

    def main_loop(self):
        dt = 1/100000
        while not self.reset:
            self.event_handling()
            self.draw()
            self.simulator.simulate_one_turn(dt)
            dt = self.fpsClock.tick(params.FPS)
      

import cProfile, pstats

if __name__ == "__main__":
    display = display.Display()

    while True:
        Game(display).main_loop()