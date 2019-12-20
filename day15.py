import sys
import logging
import collections
import numpy as np
from dataclasses import dataclass
from typing import Any
from itertools import cycle
import time

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

GAME_OVER = object()
NEW_INPUT = object()

class IntCodeStepper:
    def __init__(self, program):
        self.i_0 = 0
        self.i_base = 0
        self.n_memory = len(program)
        program_new = collections.defaultdict(int)
        for i,v in enumerate(program):
            program_new[i] = v
        self.program = program_new
        self.count_inputs = 0
        self.count_outputs = 0

    def next(self, program_input):
        while self.i_0 < self.n_memory:
            # Parse arguments
            command_full = self.program[self.i_0]
            command = command_full % 100
            command_modes = (command_full - command) // 100
            num_params = 0
            if command in (3, 4, 9):
                num_params = 1
            if command in (5, 6):
                num_params = 2
            if command in (1, 2, 7, 8):
                num_params = 3
            offsets   = range(1, num_params + 1)
            modes     = [get_digit(command_modes, d) for d in offsets]
            param_pos = [
                    self.program[(self.i_0+offset)] + (self.i_base if mode == 2 else 0) if mode in (0, 2)
                    else self.i_0+offset
                    for offset, mode in zip(offsets, modes)
            ]
            param     = [self.program[ix] for ix in param_pos]
            logging.debug(f"{[self.program[i] for i in range(self.i_0,self.i_0+num_params+1)]} @ {self.i_0}, self.i_base = {self.i_base}:\n   command = {command}, params = {param}, pos = {param_pos}")

            # Increment for the next loop to allow "overwriting" by the command
            i_0_current = self.i_0
            self.i_0 += num_params + 1

            # Parse the command
            if command == 99:
                return GAME_OVER
            # Write addition
            elif command == 1:
                self.program[param_pos[2]] = param[0] + param[1]
            # Write multiplication
            elif command == 2:
                self.program[param_pos[2]] = param[0] * param[1]
            # Input 
            elif command == 3:
                self.count_inputs += 1
                self.program[param_pos[0]] = program_input
                return NEW_INPUT
            # Output
            elif command == 4:
                self.count_outputs += 1
                return param[0]
            # One if True
            elif command == 5:
                if param[0] != 0:
                    self.i_0 = param[1]
            # One if False
            elif command == 6:
                if param[0] == 0:
                    self.i_0 = param[1]
            # Write less than
            elif command == 7:
                self.program[param_pos[2]] = int(param[0] < param[1])
            # Write equal
            elif command == 8:
                self.program[param_pos[2]] = int(param[0] == param[1])
            # Adjust relative base
            elif command == 9:
                self.i_base += param[0]
                # logging.debug(f"Point self.i_base to {self.i_base} using {command_modes} (offset by {param[0]})")
            else:
                raise ValueError(f"Position {i_0_current} found invalid command: {command}, (arg = {self.program[self.i_0]})")
            
        raise ValueError("Reached end of program without exit".format(self.i_0, self.program[self.i_0]))



EMPTY = object()
WALL = object()
ROBOT = object()
OXYGEN = object()
GOOD_PATH = object()

str_from_element = {
        EMPTY     : "  ",
        WALL      : "##",
        ROBOT     : "oo",
        OXYGEN    : "xx",
        GOOD_PATH : ".."
}


def print_screen(screen):
    min_x, min_y = [min([k[i] for k in screen.keys()]) for i in (0, 1)]
    max_x, max_y = [max([k[i] for k in screen.keys()]) for i in (0, 1)]
    
    elem_screen = [[
            EMPTY 
            for j in range(max_x-min_x+1)
        ] 
        for i in range(max_y-min_y+1)
    ]
    for pos, elem in screen.items():
        x = pos[0]-min_x
        y = pos[1]-min_y
        if not elem in str_from_element.keys():
            raise ValueError(f"Found non-object element {f} at {pos}.")
        elem_screen[y][x] = elem
    str_screen = [[str_from_element[e] for e in l] for l in elem_screen]
    print("==========================================")
    print("\n".join(["".join(l) for l in str_screen]))


## Directional inputs
NORTH=object()
SOUTH=object()
WEST=object()
EAST=object()
direction_from_input = {
        1:NORTH,
        2:SOUTH,
        3:EAST,
        4:WEST
}
input_from_direction = {v:k for k,v in direction_from_input.items()}
tuple_from_direction = {
        NORTH:(0,1),
        SOUTH:(0,-1),
        EAST:(1,0),
        WEST:(-1,0)
}

## Status outputs
STATUS_BLOCKED=object()
STATUS_WALK=object()
STATUS_OXYGEN=object()
status_from_output = {
        0:STATUS_BLOCKED,
        1:STATUS_WALK,
        2:STATUS_OXYGEN
}
output_from_status = {v:k for k,v in status_from_output.items()}

hug_the_wall = [NORTH, EAST, SOUTH, WEST]
hug_the_wall = [NORTH, EAST, SOUTH, WEST]
walk_strategy = hug_the_wall



if __name__ == "__main__":
    with open("day15.in") as f:
        program = [int(x) for x in f.read().strip().split(',')]



    ## PART 1
    screen = {(0,0):ROBOT}
    path_length = 0
    # Verify that this is a proper maze
    walk_strategy = hug_the_wall[::-1]
    last_walk_ix = 0
    search_robot = IntCodeStepper(program)
    pos = (0, 0)
    n_steps = 0
    found_wall = False
    while True:
        walk_obj = walk_strategy[last_walk_ix]
        walk_input = input_from_direction[walk_obj]
        walk_dir   = tuple_from_direction[walk_obj]
        next_output = search_robot.next(walk_input)
        if next_output is GAME_OVER:
            print("GAME OVER")
            break
        elif next_output is NEW_INPUT:
            pass
        else:
            walk_pos = tuple(a+b for a,b in zip(pos, walk_dir))
            status = status_from_output[next_output]
            if status == STATUS_BLOCKED:
                screen[walk_pos] = WALL
                last_walk_ix = (last_walk_ix + 1) % len(hug_the_wall)
                found_wall = True
            elif status == STATUS_WALK:
                if not walk_pos in screen:
                    path_length += 1
                    screen[pos]  = GOOD_PATH
                else:
                    path_length -= 1
                    screen[pos]  = EMPTY 
                screen[walk_pos] = ROBOT
                pos = walk_pos
                if found_wall:
                    last_walk_ix = (last_walk_ix - 1) % len(hug_the_wall)
            elif status == STATUS_OXYGEN:
                print(f"FOUND OXYGEN AT {walk_pos}! GAME OVER")
                screen[pos] = GOOD_PATH
                screen[walk_pos] = OXYGEN
                path_length += 1
                break
        n_steps += 1
        if n_steps >= 1E6:
            print("TOO MANY STEPS: GAME OVER")
            break
    screen[(0,0)] = ROBOT
    print_screen(screen)
    print(path_length)


    ## PART 2
    full_map = {(0,0):ROBOT}
    path_length = 0
    # Verify that this is a proper maze
    for walk_strategy in (hug_the_wall, hug_the_wall[::-1]):
        last_walk_ix = 0
        search_robot = IntCodeStepper(program)
        pos = (0, 0)
        n_steps = 0
        found_wall = False
        while True:
            walk_obj = walk_strategy[last_walk_ix]
            walk_input = input_from_direction[walk_obj]
            walk_dir   = tuple_from_direction[walk_obj]
            next_output = search_robot.next(walk_input)
            if next_output is GAME_OVER:
                print("GAME OVER")
                break
            elif next_output is NEW_INPUT:
                pass
            else:
                walk_pos = tuple(a+b for a,b in zip(pos, walk_dir))
                status = status_from_output[next_output]
                if status == STATUS_BLOCKED:
                    full_map[walk_pos] = WALL
                    last_walk_ix = (last_walk_ix + 1) % len(hug_the_wall)
                    found_wall = True
                elif status == STATUS_WALK:
                    full_map[pos]  = EMPTY 
                    full_map[walk_pos] = ROBOT
                    pos = walk_pos
                    if found_wall:
                        last_walk_ix = (last_walk_ix - 1) % len(hug_the_wall)
                elif status == STATUS_OXYGEN:
                    print(f"FOUND OXYGEN AT {walk_pos}! GAME OVER")
                    full_map[pos] = EMPTY
                    full_map[walk_pos] = OXYGEN
                    break

            n_steps += 1
            if n_steps >= 1E6:
                print("TOO MANY STEPS: GAME OVER")
                break
    full_map[(0,0)] = ROBOT
    print_screen(full_map)

    oxygen_pos = {k for k,v in full_map.items() if v == OXYGEN}
    oxygen_pos = next(iter(oxygen_pos))
    print(oxygen_pos)
    print(len({k for k,v in full_map.items() if v == EMPTY}))

    def map_recurse(map_now, pos, depth):
        map_now = map_now.copy()
        map_now[pos] = OXYGEN
        
        add_tuple = lambda a,b: tuple(x+y for x,y in zip(a,b))

        search_pos_list = [
                add_tuple(pos, vec) 
                for vec in tuple_from_direction.values()
                if map_now[add_tuple(pos, vec)] == EMPTY
        ]
        if len(search_pos_list) == 0:
            return(depth)

        search = [
            map_recurse(map_now, new_pos, depth + 1)
            for new_pos in search_pos_list
        ]

        return(max(search))
    print(f"Time for oxygen {map_recurse(full_map, oxygen_pos, 0)}")






