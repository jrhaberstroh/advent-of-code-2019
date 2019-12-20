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
BLOCK = object()
PADDLE = object()
BALL = object()

element_from_output = {
        0: EMPTY,
        1: WALL,
        2: BLOCK,
        3: PADDLE,
        4: BALL 
}

str_from_element = {
        EMPTY  : " ",
        WALL   : "@",
        BLOCK  : "#",
        PADDLE : "=",
        BALL   : "o"
}

PADDLE_CENTER = object()
PADDLE_LEFT = object()
PADDLE_RIGHT = object()

input_from_paddle = {
        PADDLE_CENTER: 0,
        PADDLE_LEFT: -1,
        PADDLE_RIGHT: 1
}

def print_screen(screen):
    max_x, max_y = [max([k[i] for k in screen.keys()]) for i in (0, 1)]

    elem_screen = [[EMPTY for j in range(max_x+1)] for i in range(max_y+1)]
    for pos, elem in screen.items():
        if pos[0] < 0:
            continue
        if not elem in (EMPTY, WALL, BLOCK, PADDLE, BALL):
            raise ValueError(f"Found non-object element {f} at {pos}.")
        elem_screen[pos[1]][pos[0]] = elem
    str_screen = [[str_from_element[e] for e in l] for l in elem_screen]
    print("\n".join(["".join(l) for l in str_screen]))


if __name__ == "__main__":
    with open("day13.in") as f:
        program = [int(x) for x in f.read().strip().split(',')]

    ## PART 1 
    arcade_machine = IntCodeStepper(program)
    output_queue = []
    screen = {}
    n_steps = 0
    while True:
        next_output = arcade_machine.next(input_from_paddle[PADDLE_LEFT])
        if next_output is GAME_OVER:
            break
        elif next_output is NEW_INPUT:
            pass
        else:
            output_queue.append(next_output)
            if len(output_queue) == 3:
                pos = tuple(output_queue[0:2])
                val = output_queue[2]
                output_queue = []
                # Score update
                if pos == (-1, 0):
                    screen[pos] = val 
                else:
                    screen[pos] = element_from_output[val]
        n_steps += 1
        if n_steps >= 1E5:
            break
    print(sum([v == BLOCK for v in screen.values()]))



    ## PART 2
    program[0] = 2
    arcade_machine = IntCodeStepper(program)
    output_queue = []
    screen = {}
    n_steps = 0
    ball_pos_state   = None
    paddle_pos_state = None
    while True:
        ball_pos   = {pos for pos,element in screen.items() if element == BALL}
        paddle_pos = {pos for pos,element in screen.items() if element == PADDLE}
        if len(ball_pos) == 1 and len(paddle_pos) == 1:
            ball_pos   = next(iter(ball_pos))
            paddle_pos = next(iter(paddle_pos))
            if ball_pos != ball_pos_state or paddle_pos != paddle_pos_state:
                print_screen(screen)
                # time.sleep(1/100)
                ball_pos_state = ball_pos
                paddle_pos_state = paddle_pos

            if ball_pos[0]  > paddle_pos[0]:
                paddle_command = PADDLE_RIGHT
            elif ball_pos[0]  < paddle_pos[0]:
                paddle_command = PADDLE_LEFT
            else:
                paddle_command = PADDLE_CENTER
        else:
            paddle_command = PADDLE_CENTER

        next_output = arcade_machine.next(input_from_paddle[paddle_command])
        if next_output is GAME_OVER:
            print(f"Game over in {n_steps}")
            print(f"Count of inputs     : {arcade_machine.count_inputs}")
            print(f"Count of outputs    : {arcade_machine.count_outputs}")
            print(f"Num blocks remaining: {sum([v == BLOCK for v in screen.values()])}")
            print(f"Score               : {screen[(-1,0)]}")
            break
        elif next_output is NEW_INPUT:
            pass
        else:
            output_queue.append(next_output)
            if len(output_queue) == 3:
                pos = tuple(output_queue[0:2])
                val = output_queue[2]
                output_queue = []
                # Score update
                if pos == (-1, 0):
                    screen[pos] = val 
                else:
                    screen[pos] = element_from_output[val]
        n_steps += 1







