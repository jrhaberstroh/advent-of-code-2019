import sys

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

def eval_program(program, value_in):
    def check_ix(ix):
        if ix < 0 or ix >= len(program):
            raise IndexError("Found invalid write index: ", ix)

    i_0 = 0
    output = []
    while i_0 < len(program):
        # Parse arguments
        command_full = program[i_0]
        command = command_full % 100
        command_modes = (command_full - command) // 100
        num_params = 0
        if command in (3, 4):
            num_params = 1
        if command in (5, 6):
            num_params = 2
        if command in (1, 2, 7, 8):
            num_params = 3
        offsets   = range(1, num_params + 1)
        modes     = [get_digit(command_modes, d) for d in offsets]
        param_pos = [program[i_0+offset] if mode == 0 else i_0+offset for offset, mode in zip(offsets, modes)]
        param     = [program[ix] for ix in param_pos]

        # Increment for the next loop to allow "overwriting" by the command
        i_0 += num_params + 1

        # Parse the command
        if command == 99:
            return({'output':output, 'program':program})
        elif command == 1:
            program[param_pos[2]] = param[0] + param[1]
        elif command == 2:
            program[param_pos[2]] = param[0] * param[1]
        elif command == 3:
            program[param_pos[0]] = value_in
        elif command == 4:
            output.append(param[0])
        elif command == 5:
            if param[0] != 0:
                i_0 = param[1]
        elif command == 6:
            if param[0] == 0:
                i_0 = param[1]
        elif command == 7:
            program[param_pos[2]] = int(param[0] < param[1])
        elif command == 8:
            program[param_pos[2]] = int(param[0] == param[1])
        else:
            raise ValueError("Position {} found invalid data: {}".format(i_0, program[i_0]))
        
    raise ValueError("Reached end of program without exit".format(i_0, program[i_0]))


with open("day5.in") as f:
    s_program = f.read().split(",")
program = [int(s) for s in s_program]

result  = eval_program(program.copy(), 1)
print(result['output'])

# print(len(program))
# print(program[238:])
result  = eval_program(program.copy(), 5)
print(result['output'])

