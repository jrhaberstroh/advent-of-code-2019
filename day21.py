from IntcodeStepper import IntcodeStepper, REQUEST_INPUT, GAME_OVER

FAILURE = object()
SUCCESS = object()

with open('day21.in') as f:
    spring_prog = [int(v) for v in f.read().strip().split(',')]

## print(spring_prog)

def ascii_stepper(program, statement):
    for char in line:
        program.next(ord(char))
    program.next(ord('\n'))


def run_springscript_program(springscript, display = False, mode = 'WALK'):
    if not mode in ('WALK', 'RUN'):
        raise ValueError("Must use mode = 'WALK' or 'RUN'")
    this_prog = IntcodeStepper(spring_prog)
    springscript_iter = iter(springscript)
    springscript.append(mode)
    output_line = ''
    exit_status = SUCCESS
    while True:
        next_result = this_prog.next()
        while next_result == REQUEST_INPUT:
            next_springscript_instruction = next(springscript_iter)
            if display:
                print(next_springscript_instruction)
            for char in next_springscript_instruction:
                next_result = this_prog.next(ord(char))
                if next_result != REQUEST_INPUT:
                    raise RuntimeError("Program returned output before reaching end of input")
            next_result = this_prog.next(ord('\n'))

        if next_result == GAME_OVER:
            return exit_status
        else:
            try: 
                next_result_char = chr(next_result)
            except ValueError:
                return(next_result)

            if next_result_char == '\n':
                if output_line == "Didn't make it across:":
                    exit_status = FAILURE
                if display:
                    print(output_line)
                output_line = ''
            else:
                output_line = output_line + next_result_char


first_words = ['NOT', 'AND', 'OR']
second_words = ['A', 'B', 'C', 'D', 'T', 'J']
third_words = ['T', 'J']

all_terms = [' '.join([w1, w2, w3])
        for w1 in first_words
        for w2 in second_words
        for w3 in third_words
        if w2 != w1
]

def script_generator(terms, depth, array = []):
    if depth == 1:
        for t in terms:
            yield array + [t]
    else:
        for t in terms:
            for script in script_generator(terms, depth - 1, array + [t]):
                yield script

def part1():
    springscript = ['NOT A J', 'NOT B T', 'OR T J', 'NOT C T', 'OR T J', 'AND D J']
    result = run_springscript_program(springscript, display = True, mode = 'WALK')
    print(result)


def part2():
    # springscript = ['NOT A J', 'NOT B T', 'OR T J', 'NOT C T', 'OR T J', 'AND D J']
    springscript = [
            ## (UNLESS) There is a hole at both F and I 
            ##  i.e. (IF) there is ground at either I or J
            'OR I T' , 'OR F T' , 'AND T J',
            ## (AND) there are any holes in the next three spaces...
            'NOT A T', 'OR T J' , 'NOT B T', 'OR T J' , 'NOT C T', 'OR T J' , 
            ## (AND) there are TWO landing spots at 4 & 5
            'AND D J', 'AND E J',
            ]
    
    springscript = [
            ## (Initialize J to TRUE)
            'NOT J J',

            ## (IF) there is a landing spot at 4 
            'AND D J',

            ## (UNLESS) There is a hole at both E and H 
            ##  i.e. (IF) there is ground at either E or H
            'OR H T' , 'OR E T' , 'AND T J',

            ## If we have not already failed, T = True
            ## If we have already failed, T = False
            ## Therefore, assume T = True

            ## (AND) there are any holes in the next three spaces...
            ##  i.e. (IF) there is not ground all all of A, B, and C
            'AND A T', 'AND B T', 'AND C T', 'NOT T T', 'AND T J' 

            ]


    result = run_springscript_program(springscript, display = True, mode = 'RUN')
    print(result)


if __name__ == "__main__":
    # part1()
    part2()
