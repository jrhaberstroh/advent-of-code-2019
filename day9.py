import sys
import logging
import collections

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

def eval_program(program, value_in):
    def check_ix(ix):
        if ix < 0 or ix >= len(program):
            raise IndexError("Found invalid write index: ", ix)

    program_new = collections.defaultdict(int)
    for i,v in enumerate(program):
        program_new[i] = v
    program = program_new



    i_0 = 0
    i_base = 0
    output = []
    n_memory = len(program)
    logging.debug(f"Number of memory addresses: {n_memory}")
    while i_0 < len(program):
        # Parse arguments
        command_full = program[i_0]
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
                program[(i_0+offset)] + (i_base if mode == 2 else 0) if mode in (0, 2)
                else i_0+offset
                for offset, mode in zip(offsets, modes)
        ]
        param     = [program[ix] for ix in param_pos]
        logging.debug(f"{[program[i] for i in range(i_0,i_0+num_params+1)]} @ {i_0}, i_base = {i_base}:\n   command = {command}, params = {param}, pos = {param_pos}")
        logging.debug(f"    Outputs: {output}")

        # Increment for the next loop to allow "overwriting" by the command
        i_0_current = i_0
        i_0 += num_params + 1

        # Parse the command
        if command == 99:
            return({'output':output, 'program':program})
        # Write addition
        elif command == 1:
            program[param_pos[2]] = param[0] + param[1]
        # Write multiplication
        elif command == 2:
            program[param_pos[2]] = param[0] * param[1]
        # Input 
        elif command == 3:
            program[param_pos[0]] = value_in
        # Output
        elif command == 4:
            output.append(param[0])
        # One if True
        elif command == 5:
            if param[0] != 0:
                i_0 = param[1]
        # One if False
        elif command == 6:
            if param[0] == 0:
                i_0 = param[1]
        # Write less than
        elif command == 7:
            program[param_pos[2]] = int(param[0] < param[1])
        # Write equal
        elif command == 8:
            program[param_pos[2]] = int(param[0] == param[1])
        # Adjust relative base
        elif command == 9:
            i_base += param[0]
            # logging.debug(f"Point i_base to {i_base} using {command_modes} (offset by {param[0]})")
        else:
            raise ValueError(f"Position {i_0_current} found invalid command: {command}, (arg = {program[i_0]})")
        
    raise ValueError("Reached end of program without exit".format(i_0, program[i_0]))


with open("day9.in") as f:
    s_program = f.read().split(",")
program = [1102,34915192,34915192,7,4,7,99,0] 
program = [104,1125899906842624,99]
program = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
program = [int(s) for s in s_program]

# logging.basicConfig(level=logging.DEBUG)

result  = eval_program(program.copy(), 2)
print(result['output'])

