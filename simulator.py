import random
from commands import MoveCommand
from cat import Cat
from prey import Prey
from collections import defaultdict

DIRECTION_KEY = {(-1, 0): "left", (1, 0): "right", (0, -1): "up", (0, 1): "down"}

class Simulator:
    def __init__(self, units, board, display, factions):
        self.units, self.board, self.display, self.factions = units, board, display, factions
        self.ticks = 0
        self.prey_cooldown = 1

    def simulate_one_turn(self, dt):
        """Handles all of the calling, movement, and functions of the cats"""

        self.ticks += dt

        while self.ticks > self.display.speed:

            self.handle_spawning()
            self.pre_turn()
            commands = self.get_commands()
            self.execute_commands(commands)

            self.ticks -= self.display.speed

    def execute_commands(self, commands):
        faction_movements = defaultdict(lambda: set([]))
        for command in commands:
            if type(command) == MoveCommand:
                unit, position = command.unit, command.pos
                if unit.dead: continue

                key = sorted([unit.pos, position], key=lambda x: x[0]+x[1])
                key = tuple([key[0][0], key[0][1], key[0][2], key[1][0], key[1][1], key[1][2]])
                if key in faction_movements[unit.faction_id]: # Units want to pass by:
                    self.units.swap_positions(unit.pos, position)
                else:
                    faction_movements[unit.faction_id].add(key)
                    if position in self.units.by_pos: 
                        can_move = self.run_combat(unit, position)
                        if not can_move: continue

                faction_movements[unit.faction_id].add(key)

                if hasattr(unit, "direction"):
                    direction = (position[0] - unit.pos[0], position[1] - unit.pos[1])

                    if direction in DIRECTION_KEY:
                        unit.direction = DIRECTION_KEY[direction]
                
                self.units.move_unit(unit, position)

                
                

                if unit.faction_id != "prey" and self.factions[unit.faction_id].positions["kill_pile"] == list(position):
                    if self.factions[unit.faction_id].prey > 0:
                        self.factions[unit.faction_id].prey -= 1
                        unit.hunger += 1000

                    self.factions[unit.faction_id].prey += unit.prey
                    unit.prey = 0

                    


    def run_combat(self, unit, position):
        enemy_unit = self.units.by_pos[position]
        if enemy_unit.faction_id == unit.faction_id: 
            return False
        enemy_unit.health -= unit.damage
        
        if enemy_unit.health <= 0: 
            del self.units.by_pos[position]
            self.units.by_faction[enemy_unit.faction_id].remove(enemy_unit)
            enemy_unit.dead = True
            self.units.units.remove(enemy_unit)

            if type(enemy_unit) == Prey and type(unit) == Cat:
                unit.prey += 1
        else:
            return False
        
        return True


    def get_commands(self):
        commands = []
        for unit in self.units.units:
            if type(unit) == Prey: commands.append(unit.getMove(self.board[unit.pos[2]]))
            elif type(unit) == Cat: commands.append(unit.getMove(self.board[unit.pos[2]], self.factions, self.units))

        random.shuffle(  commands)

        return commands

    def pre_turn(self):
        for unit in self.units.units:
            if type(unit) != Cat: continue
            
            # unit.hunger -= 1
            # if unit.hunger <= 0:
            #     unit.health -= 1

            # if unit.prey > 0 and unit.hunger < 300:
            #     unit.hunger += 1000
            #     unit.prey -= 1
            
            
            if unit.health <= 0:
                self.kill(unit)

    def handle_spawning(self):
        pass

    def kill(self, unit):
        unit.dead = True
        del self.units.by_pos[unit.pos]
        self.units.by_faction[unit.faction_id].remove(unit)
        self.units.units.remove(unit)

