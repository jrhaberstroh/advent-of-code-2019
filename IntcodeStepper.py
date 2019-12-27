import collections
import logging

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

GAME_OVER = object()
REQUEST_INPUT = object()
RECEIVED_INPUT = object()

class IntcodeStepper:
    def __init__(self, program, patient = False):
        self.i_0 = 0
        self.i_base = 0
        self.n_memory = len(program)
        program_new = collections.defaultdict(int)
        for i,v in enumerate(program):
            program_new[i] = v
        self.program = program_new
        self.count_inputs = 0
        self.count_outputs = 0
        self.patient = patient
    def next(self, program_input = None):
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
                if program_input is None:
                    self.i_0 = i_0_current
                    return REQUEST_INPUT
                self.count_inputs += 1
                self.program[param_pos[0]] = program_input
                if self.patient:
                    return RECEIVED_INPUT
                program_input = None
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



