import sys

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

def eval_program(program, value_in):
    i_0 = 0
    output = []
    while i_0 < len(program):
        # convert to one-based indexing
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
        query_ix  = (lambda delta, mode: p)
        offsets  = range(1, num_params + 1)
        modes    = [get_digit(command_modes, d) for d in offsets]

        param_ix = [program[i_0+offset] if mode == 0 else i_0+offset for offset, mode in zip(offsets, modes)]

        if command == 99:
            return({'output':output, 'program':program})
        elif command == 1 or command == 2:
            v1, v2 = [program[ix] for ix in [param_ix[0], param_ix[1]]]
            ixo = param_ix[2]
            v_out = v1 + v2 if command == 1 else v1 * v2
            print(program[i_0:i_0+4], ":", modes, [v1, v2, ixo])
            print("Write {} to {}".format(v_out, ixo))
            if ixo < 0 or ixo >= len(program):
                raise ValueError("Found invalid write index: ", ixo)
            program[ixo] = v_out
            i_0 += 4
        elif command == 3 or command == 4:
            i_target = param_ix[0]
            if i_target < 0 or i_target >= len(program):
                raise ValueError("Found invalid write index: ", ix[2])
            if command == 3:
                print("Write {} to {}".format(value_in, i_target))
                program[i_target] = value_in
            if command == 4:
                print("    Output {} from {}".format(program[i_target], i_target))
                output.append(program[i_target])
            i_0 += 2
        else:
            raise ValueError("Position {} found invalid data: {}".format(i_0, program[i_0]))
    raise ValueError("Reached end of program without exit".format(i_0, program[i_0]))


with open("day5.in") as f:
    s_program = f.read().split(",")
program = [int(s) for s in s_program]
result  = eval_program(program, 1)
print(result['output'])
# print(eval_program(program, 1))

# print(search(program, 100))
