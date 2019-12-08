import sys
from itertools import permutations

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)

def next_output(program, i_0, input_queue):
    program = list(program)
    input_queue = list(input_queue)
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
        param_pos = [
                program[i_0+offset] if mode == 0 else i_0+offset 
                for offset, mode in zip(offsets, modes)
        ]
        param     = [program[ix] for ix in param_pos]

        # Increment for the next loop to allow "overwriting" by the command
        i_0 += num_params + 1

        state = {'memory':tuple(program), 'addr': i_0, 'input': tuple(input_queue)}

        # Parse the command
        if command == 99:
            return (None, state)
        elif command == 1:
            program[param_pos[2]] = param[0] + param[1]
        elif command == 2:
            program[param_pos[2]] = param[0] * param[1]
        elif command == 3:
            if len(input_queue) == 0:
                raise ValueError("Looking for input but none found: i = {}".format(i_0))
            use_value = input_queue.pop(0)
            program[param_pos[0]] = use_value
        elif command == 4:
            return (param[0], state)
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





def feedback_recursion_helper(program_executors, i_amp, target_value):
    num_entities = len(program_executors)

    this_program = program_executors[i_amp]
    i_amp %= num_entities

    output, state = next_output(this_program['memory'], this_program['addr'], this_program['input'])

    if output is None:
        if i_amp == num_entities - 1:
            return target_value
    else:
        target_value = output

    # Construct the next recursion
    i_amp_next = (i_amp + 1) % num_entities
    program_executors = tuple(
            state if i == i_amp else 
            ({'memory':pe['memory'], 'addr':pe['addr'], 'input':pe['input'] + (output,)} if i == i_amp_next else pe)
            for i, pe in enumerate(program_executors)
    )
    return(feedback_recursion_helper(program_executors, i_amp_next, target_value))


# Define a main recursion call with simplified inputs to initiate recursion
def feedback_recursion(program, amp_values, first_input):
    num_entities      = len(amp_values)
    program_executors = tuple(
            {'memory':tuple(program), 'addr':0, 'input': (a,)} if i != 0 else
            {'memory':tuple(program), 'addr':0, 'input': (a, first_input)} 
            for i,a in enumerate(amp_values)
    )
    return feedback_recursion_helper(tuple(program_executors), 0, None)
    



with open("day7.in") as f:
    s_program = f.read().split(",")
program = tuple(int(s) for s in s_program)
amp_values = list(range(5,10))
print(max([feedback_recursion(program, amp_setting, 0) for amp_setting in permutations(amp_values)]))
