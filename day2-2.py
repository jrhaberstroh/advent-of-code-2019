import sys

target = 19690720

with open("day2.in") as f:
    s_program = f.read().split(",")

program = [int(s) for s in s_program]
print(program)

def eval_program(program):
    i_0 = 0
    while i_0 < len(program):
        # convert to one-based indexing
        command = program[i_0]
        if command == 1 or command == 2:
            i1   = program[i_0 + 1]
            i2   = program[i_0 + 2]
            i_out= program[i_0 + 3]
            
            v1 = program[i1]
            v2 = program[i2]
            v_out = v1 + v2 if command == 1 else v1 * v2

            program[i_out] = v_out
            i_0 += 4
        elif command == 99:
            return(program)
        else:
            raise ValueError("Position {} found invalid data: {}".format(i_0, program[i_0]))
    raise ValueError("Reached end of program without exit".format(i_0, program[i_0]))

def search(program_original, lim=100):
    for noun in range(0, lim):
        for verb in range(0, lim):
            program = program_original.copy()
            program[1] = noun
            program[2] = verb
            try:
                result = eval_program(program)[0]
                if result == target:
                    return(100 * noun + verb)
            except ValueError:
                pass

print(search(program, 100))
