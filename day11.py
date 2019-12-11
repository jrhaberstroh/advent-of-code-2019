import sys
import logging
import collections
import numpy as np

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

class PainterRobot:
    def __init__(self, program):
        self.i_0 = 0
        self.i_base = 0
        self.n_memory = len(program)
        program_new = collections.defaultdict(int)
        for i,v in enumerate(program):
            program_new[i] = v
        self.program = program_new

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
                return None
            # Write addition
            elif command == 1:
                self.program[param_pos[2]] = param[0] + param[1]
            # Write multiplication
            elif command == 2:
                self.program[param_pos[2]] = param[0] * param[1]
            # Input 
            elif command == 3:
                self.program[param_pos[0]] = program_input.pop(0)
            # Output
            elif command == 4:
                return(param[0])
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

with open("day11.in") as f:
    program = [int(x) for x in f.read().strip().split(',')]
print(program)


# logging.basicConfig(level=logging.DEBUG)


LEFT = object()
RIGHT = object()

def add_tuple(x, y):
    return tuple(a+b for a,b in zip(x,y))

def rotate(x, way):
    if way == LEFT:
        return (-x[1],  x[0])
    elif way == RIGHT:
        return  (x[1], -x[0])
    else:
        raise ValueError("No direction passed to rotate")


##  ## PART 1
##  ship_hull        = collections.defaultdict(int)
##  has_been_painted = set()
##  paint_robot = PainterRobot(program)
##  in_queue = []
##  pos = (0,0)
##  facing = (0,1)
##  num_steps = 0
##  while True:
##      # Read the paint color
##      in_queue.append(ship_hull[pos])
##  
##      # Then paint
##      paint_color    = paint_robot.next(in_queue)
##      if paint_color is None:
##          break
##      else:
##          ship_hull[pos] = paint_color
##          has_been_painted = has_been_painted.union({pos})
##          # print(f"Painting {pos} {paint_color}")
##  
##      # Then turn and move
##      turn_command   = paint_robot.next(in_queue)
##      if turn_command is None:
##          break
##      else:
##          turn_direction = RIGHT if turn_command else LEFT
##          facing = rotate(facing, turn_direction)
##          pos = add_tuple(pos, facing)
##  
##      num_steps += 1
##      if num_steps >= 1000000:
##          break
##  
##  print(len(ship_hull.keys()))
##  print(len(has_been_painted))


## PART 2
paint_robot = PainterRobot(program)

ship_hull        = collections.defaultdict(int)
has_been_painted = set()
in_queue = []
pos    = (0,0)
facing = (0,1)
num_steps = 0
# Set first spot to white
ship_hull[pos] = 1
while True:
    # Read the paint color
    in_queue.append(ship_hull[pos])

    # Then paint
    paint_color    = paint_robot.next(in_queue)
    if paint_color is None:
        break
    else:
        ship_hull[pos] = paint_color
        has_been_painted = has_been_painted.union({pos})
        # print(f"Painting {pos} {paint_color}")

    # Then turn and move
    turn_command   = paint_robot.next(in_queue)
    if turn_command is None:
        break
    else:
        turn_direction = RIGHT if turn_command else LEFT
        facing = rotate(facing, turn_direction)
        pos = add_tuple(pos, facing)

    num_steps += 1
    if num_steps >= 1000000:
        break

white_spaces = {pos for pos, color in ship_hull.items() if color == 1}
min_x = min([x[0] for x in white_spaces])
min_y = min([x[1] for x in white_spaces])
max_x = max([x[0] for x in white_spaces])
max_y = max([x[1] for x in white_spaces])

w_x = max_x - min_x + 1
w_y = max_y - min_y + 1
white_spaces_ix = {
        (pos[0] - min_x, pos[1] - min_y) 
        for pos, color in ship_hull.items() 
        if color == 1
}

ship = np.zeros([w_x, w_y])
for pos in white_spaces_ix:
    ship[pos] = 1
for col in ship.T[::-1, :]:
    print("".join([' ' if x == 0 else '#' for x in col]))


