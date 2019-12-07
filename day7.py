import sys

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

def eval_program(program, input_seq):
    def check_ix(ix):
        if ix < 0 or ix >= len(program):
            raise IndexError("Found invalid write index: ", ix)
    num_inputs = 0

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
            return({'output':output, 'program':program, 'num_inputs': num_inputs})
        elif command == 1:
            program[param_pos[2]] = param[0] + param[1]
        elif command == 2:
            program[param_pos[2]] = param[0] * param[1]
        elif command == 3:
            if num_inputs >= len(input_seq):
                raise ValueError()
            use_value = input_seq[num_inputs]
            num_inputs += 1
            program[param_pos[0]] = use_value
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


with open("day7.in") as f:
    s_program = f.read().split(",")
program = [int(s) for s in s_program]

def check_single_value(x):
    if len(x) != 1:
        raise ValueError("Length not == 1")
amp_values = set(range(0,5))
max_signal = 0
for a1 in amp_values:
    for a2 in amp_values - {a1}:
        for a3 in amp_values - {a1, a2}:
            for a4 in amp_values - {a1, a2, a3}:
                for a5 in amp_values - {a1, a2, a3, a4}:
                    o1 = eval_program(program.copy(), [a1, 0])['output'][0]
                    o2 = eval_program(program.copy(), [a2, o1])['output'][0]
                    o3 = eval_program(program.copy(), [a3, o2])['output'][0]
                    o4 = eval_program(program.copy(), [a4, o3])['output'][0]
                    o5 = eval_program(program.copy(), [a5, o4])['output'][0]
                    if o5 > max_signal:
                        max_signal = o5
                        max_setting = "".join([str(a) for a in [a1, a2, a3, a4, a5]])
print(max_signal)
print(max_setting)

