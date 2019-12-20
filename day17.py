import sys
import logging
import collections
import numpy as np
import operator
from dataclasses import dataclass
from typing import Any, Sequence
from itertools import cycle, combinations
import time

PART = 2

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


with open('day17.in') as f:
    s_program = f.read().strip()

program = [int(x) for x in s_program.split(',')]
this_prog = IntCodeStepper(program)
keep_running = True
full_camera = []
while keep_running:
    line = []
    while True:
        this_value = this_prog.next(None)
        if this_value == 10:
            break
        elif this_value == GAME_OVER:
            print("Encountered GAME OVER")
            keep_running = False
            break
        elif this_value == NEW_INPUT:
            continue
        line.append(chr(this_value))
    if line:
        full_camera.append(line)
    
## Print the lattice decoratively
print("\n".join([" ".join(line) for line in full_camera]))


np_camera = np.array(full_camera)
    
if PART == 1:
    
    lattice_intersect = (
            lattice[1:-1, 1:-1] * 
            lattice[0:-2, 1:-1] *
            lattice[2:  , 1:-1] *
            lattice[1:-1, 0:-2] *
            lattice[1:-1, 2:  ]
    )
    lattice = (np_camera == '#').astype(int)
    
    ## Print map with intersections
    ## [print(" ".join([str(x) for x in line])) for line in lattice[1:-1, 1:-1] + lattice_intersect]
    
    intersection_points = np.where(lattice_intersect)
    
    alignment = 0
    for x,y in zip(*intersection_points):
        this_alignment = (x+1) * (y+1)
        print(x+1, y+1, this_alignment)
        alignment += this_alignment
    print(alignment)
    
LEFT  = lambda a: (-a[1], a[0])
RIGHT = lambda a: ( a[1],-a[0])


class AddTuple(tuple):
    def __add__(self, other):
        return self.__class__(map(operator.add, self, other))
    
if PART == 2:
    def check_pos(pos):
        np_camera[pos] == '#'

    def valid_trial_pos(camera, trial_pos):
        if all([x < l and x >= 0 for x,l in zip(trial_pos, camera.shape)]):
            if camera[trial_pos] in ('#', '^'):
                return True
        return False

    def determine_turn(camera, pos, facing):
        dir_try = {'L':LEFT, 'R':RIGHT}
        for dir_name, dir_func in dir_try.items():
            new_facing = dir_func(facing)
            trial_pos = pos + new_facing 
            if valid_trial_pos(camera, trial_pos):
                return (dir_name, new_facing)
        raise StopIteration(f"No valid turning direction, {pos}:{new_facing}")

    def count_forward(camera, pos, facing):
        result = 0
        while valid_trial_pos(camera, pos + facing):
            pos = pos + facing
            result += 1
        if result == 0:
            raise StopIteration(f"No forward to move, {pos}:{new_facing}")
        return (result, pos)

    pos    = AddTuple(arr[0] for arr in np.where(np_camera == '^'))
    continue_search = True
    path_sequence = []
    facing = AddTuple([-1, 0])
    print(f"CAMERA INSPECTION: {np_camera[49:51, 36:39]}")

    while continue_search:
        try: 
            turn, facing = determine_turn(np_camera, pos, facing)
            path_sequence.append(turn)
            fwd, pos     = count_forward(np_camera, pos, facing)
            path_sequence.append(fwd)
        except StopIteration:
            print("Reached end of path!")
            break

    path_sequence = [str(x) for x in  path_sequence]


    MIN_WORD_LEN = 2
    MAX_WORD_LEN = 20
    EMPTY_CHR = " "

    solution_strings = [
            "A,B,A,C,C,A,B,C,B,B",
            "L,8,R,10,L,8,R,8",
            "L,12,R,8,R,8",
            "L,8,R,6,R,6,R,10,L,8"
    ]
    solution_inputs = [
            ord(letter) 
            for sol in solution_strings 
            for letter in (sol + "\n")
    ]
    solution_inputs += [ord(letter) for letter in "no\n"]

    with open('day17.in') as f:
        s_program = f.read().strip()
    program = [int(x) for x in s_program.split(',')]
    program[0] = 2
    this_prog = IntCodeStepper(program)

    output_line = []
    print(solution_inputs)
    next_input = solution_inputs.pop(0)
    while True:
        this_value = this_prog.next(next_input)
        if this_value == NEW_INPUT:
            try:
                next_input = solution_inputs.pop(0)
            except IndexError:
                next_input = None
        elif this_value == GAME_OVER:
            break
        elif this_value == 10:
            print(" ".join([chr(letter) for letter in output_line]))
            output_line = []
        else:
            output_line.append(this_value)
    print(output_line)


    ## def replace_positions(path_sequence: Sequence[str], replace_pos: Sequence[int], word_len, letter):
    ##     new_path_sequence = list(path_sequence)
    ##     replaced_string = [EMPTY_CHR for _ in range(len(new_path_sequence))]
    ##     for count_letter, pos_start in enumerate(replace_pos):
    ##         this_letter = letter + str(count_letter)
    ##         for i in range(pos_start, pos_start + word_len):
    ##             if new_path_sequence[i] == EMPTY_CHR:
    ##                 return False, None, None
    ##             new_path_sequence[i] = EMPTY_CHR 
    ##             replaced_string[i] = this_letter
    ##     return True, new_path_sequence, replaced_string


    ## def helper_compress(path_sequence: Sequence[str], new_word_len: int, depth: int, maxdepth):
    ##     path_sequence = list(path_sequence)
    ##     depth_names = ['A', 'B', 'C']
    ##     full_compressed = [EMPTY_CHR for _ in range(len(path_sequence))]

    ##     # Assign the new word to the first segment
    ##     first_segment = []
    ##     first_ix = None
    ##     for i, letter in enumerate(path_sequence):
    ##         if len(first_segment) > 0 and letter == EMPTY_CHR:
    ##             break
    ##         if letter != EMPTY_CHR:
    ##             if first_ix is None:
    ##                 first_ix = i
    ##             first_segment.append(letter)

    ##     if len(first_segment) < new_word_len:
    ##         # BASE-CASE: Failure if first segment is not of sufficient length
    ##         return (False, EMPTY_CHR)
    ##     else:
    ##         new_word = first_segment[:new_word_len]
    ##         for i in range(first_ix, first_ix + new_word_len):
    ##             path_sequence[i] = EMPTY_CHR 
    ##             full_compressed[i]    = depth_names[depth]


    ##     # First get all *versions* of the sequence with our new word replaced

    ##     position_matches = []
    ##     for i in range(len(path_sequence) - new_word_len):
    ##         if path_sequence[i:i+new_word_len] == new_word:
    ##             position_matches.append(i)

    ##     # print("Position matches:", position_matches)
    ##     all_combinations = [
    ##             x 
    ##             for r in range(1, len(position_matches) + 1) 
    ##             for x in combinations(position_matches, r) 
    ##     ]

    ##     # Recursive aggregation
    ##     all_good_recursions = []
    ##     for replace_pos in all_combinations:
    ##         success, this_path_sequence, trial_compressed = replace_positions(
    ##                 tuple(path_sequence), 
    ##                 replace_pos, 
    ##                 new_word_len, 
    ##                 depth_names[depth]
    ##         )
    ##         
    ##         if not success:
    ##             continue 
    ##         
    ##         trial_compressed = [a if a != EMPTY_CHR else b for a,b in zip(full_compressed, trial_compressed)]


    ##         # BASE-CASE: Success if all letters have been replaced at maxdepth
    ##         if depth == maxdepth:
    ##             if all([s == EMPTY_CHR for s in path_sequence]):
    ##                 all_good_recursions.append(trial_compressed)
    ##         else:
    ##             for next_word_len in range(MIN_WORD_LEN, MAX_WORD_LEN + 1):
    ##                 recursion_success, result = helper_compress(tuple(this_path_sequence), next_word_len, depth + 1, maxdepth)
    ##                 if recursion_success:
    ##                     recursion_compressed = [a if a != EMPTY_CHR else b for a,b in zip(full_compressed, result)]
    ##                     print("Recursion compressed: ", recursion_compressed)
    ##                     all_good_recursions.append(recursion_compressed)
    ##         if depth == 0:
    ##             print(f"Depth {depth} good recursions found for word len {new_word_len}:", all_good_recursions)
    ##             print("trial_compressed", "".join([s.rjust(2) for s in trial_compressed]))
    ##             print("path_sequence   ", "".join([s.rjust(2) for s in this_path_sequence]))

    ##     # BASE CASE: Success if received any successful recursions, Failure if received none
    ##     # print(all_good_recursions)
    ##     return len(all_good_recursions) > 0, all_good_recursions


    ## def compress(path_sequence, maxdepth = 2):
    ##     for word_len in range(MIN_WORD_LEN, MAX_WORD_LEN + 1):
    ##         recursion_success, result = helper_compress(tuple(path_sequence), word_len, 0, maxdepth)
    ##         print(result)



    # compress(path_sequence, maxdepth = 2)


    ## with open('day17.in') as f:
    ##     s_program = f.read().strip()
    ## program = [int(x) for x in s_program.split(',')]
    ## program[0] = 2
    ## this_prog = IntCodeStepper(program)




    
