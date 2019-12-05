import sys

with open(sys.argv[1]) as f:
    s_program = f.read().split(",")

program = [int(s) for s in s_program]
print(program)

def eval_program(program):
    i_0 = 0
    print(len(program))
    while i_0 < len(program):
        # convert to one-based indexing
        command = program[i_0]
        if command in (1, 2):
            i1   = program[i_0 + 1]
            i2   = program[i_0 + 2]
            i_out= program[i_0 + 3]
            
            v1 = program[i1]
            v2 = program[i2]
            v_out = v1 + v2 if command == 1 else v1 * v2
            print(i_out, v_out)

            program[i_out] = v_out
            i_0 += 4
        elif command == 99:
            print(i_0)
            print(program[i_0-5 : i_0+5])
            return(program)
        else:
            ValueError("Position {} found invalid data: {}".format(i_0, program[i_0]))
    ValueError("Reached end of program without exit".format(i_0, program[i_0]))

print(eval_program(program))
