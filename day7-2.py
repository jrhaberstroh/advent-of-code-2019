import sys

def get_digit(x, digit):
    x = x  - x % pow(10, digit-1)
    x = x // pow(10, digit-1)
    return(x % 10)


class Program:
    def __init__(self, program):
        self.program = program
        self.num_inputs = 0
        self.i_0 = 0
        self.output = []

    def next(self, input_queue):
        while self.i_0 < len(self.program):
            # Parse arguments
            command_full = self.program[self.i_0]
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
                    self.program[self.i_0+offset] if mode == 0 else self.i_0+offset 
                    for offset, mode in zip(offsets, modes)
            ]
            param     = [self.program[ix] for ix in param_pos]

            # Increment for the next loop to allow "overwriting" by the command
            self.i_0 += num_params + 1

            # Parse the command
            if command == 99:
                return(None)
            elif command == 1:
                self.program[param_pos[2]] = param[0] + param[1]
            elif command == 2:
                self.program[param_pos[2]] = param[0] * param[1]
            elif command == 3:
                if len(input_queue) == 0:
                    raise ValueError()
                use_value = input_queue.pop(0)
                self.num_inputs += 1
                self.program[param_pos[0]] = use_value
            elif command == 4:
                self.output.append(param[0])
                return(param[0])
            elif command == 5:
                if param[0] != 0:
                    self.i_0 = param[1]
            elif command == 6:
                if param[0] == 0:
                    self.i_0 = param[1]
            elif command == 7:
                self.program[param_pos[2]] = int(param[0] < param[1])
            elif command == 8:
                self.program[param_pos[2]] = int(param[0] == param[1])
            else:
                raise ValueError("Position {} found invalid data: {}".format(self.i_0, self.program[self.i_0]))
        raise ValueError("Reached end of program without exit".format(self.i_0, self.program[self.i_0]))


with open("day7.in") as f:
    s_program = f.read().split(",")
program = [int(s) for s in s_program]

amp_values = set(range(5,10))
max_signal = 0
for a1 in amp_values:
    for a2 in amp_values - {a1}:
        for a3 in amp_values - {a1, a2}:
            for a4 in amp_values - {a1, a2, a3}:
                for a5 in amp_values - {a1, a2, a3, a4}:
                    i1 = [a1, 0]
                    i2 = [a2]
                    i3 = [a3]
                    i4 = [a4]
                    i5 = [a5]
                    p1 = Program(program.copy())
                    p2 = Program(program.copy())
                    p3 = Program(program.copy())
                    p4 = Program(program.copy())
                    p5 = Program(program.copy())
                    prev_o5 = None
                    while True:
                        o1 = p1.next(i1) 
                        i2.append(o1)
                        o2 = p2.next(i2)
                        i3.append(o2)
                        o3 = p3.next(i3)
                        i4.append(o3)
                        o4 = p4.next(i4)
                        i5.append(o4)
                        o5 = p5.next(i5)
                        i1.append(o5) 
                        if o5 is None:
                            break
                        else:
                            prev_o5 = o5
                    if prev_o5 > max_signal:
                        max_signal = prev_o5
                        max_setting = "".join([str(a) for a in [a1, a2, a3, a4, a5]])

print(max_signal)
print(max_setting)

# print(eval_program(program.copy(), [0, 0])['num_inputs'])
# print(eval_program(program.copy(), [1, 0])['num_inputs'])
# print(eval_program(program.copy(), [2, 0])['num_inputs'])
# print(eval_program(program.copy(), [3, 0])['num_inputs'])
# print(eval_program(program.copy(), [4, 0])['num_inputs'])
# 
# print(eval_program(program.copy(), [9, 0])['output'])
# print(eval_program(program.copy(), [8, 0])['output'])
# print(eval_program(program.copy(), [7, 0])['output'])
# print(eval_program(program.copy(), [6, 0])['output'])
# print(eval_program(program.copy(), [5, 0])['output'])
# print(eval_program(program.copy(), [9, 0])['num_inputs'])
# print(eval_program(program.copy(), [8, 0])['num_inputs'])
# print(eval_program(program.copy(), [7, 0])['num_inputs'])
# print(eval_program(program.copy(), [6, 0])['num_inputs'])
# print(eval_program(program.copy(), [5, 0])['num_inputs'])
# print(eval_program(program.copy(), [7, 4])['output'])
