import re

## ---------
## exploration
## ---------


inputs = """
deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1
""".strip()


def compute_mapper(inputs, n_modulo):
    mapper = {'a':1, 'b':0}
    for l in inputs.split('\n'):
        splitter = re.findall(r"([a-z ]+) ([-0-9]*)", l.strip() + " ")[0]
        if splitter[0] == 'deal into new stack':
            mapper['a'] = (mapper['a'] * -1)
            mapper['b'] = (mapper['b'] * -1) - 1
        if splitter[0] == 'deal with increment':
            mapper['a'] = (mapper['a'] * int(splitter[1]))
            mapper['b'] = (mapper['b'] * int(splitter[1]))
        if splitter[0] == 'cut':
            mapper['b'] = (mapper['b'] - int(splitter[1]))
        mapper['a'] %= n_modulo
        mapper['b'] %= n_modulo
    return(mapper)

i = list(range(10))
mapper = compute_mapper(inputs, 10)
j = [(mapper['a']*i0 + mapper['b']) % 10 for i0 in i]
print(i)
print(j)
print([x[0] for x in sorted(zip(i,j), key = lambda x: x[1])])




## ----------------------------------------------------------------------
## PART 1
## ----------------------------------------------------------------------
def cut(deck, n):
    return [*deck[n:], *deck[:n]]
def deal_increment(deck, n):
    ix_target = [(n*i) % N_CARDS for i in range(len(deck))]
    return [x[0] for x in sorted(zip(deck, ix_target), key = lambda x: x[1])]
def deal_stack(deck):
    return deck[::-1]
function_dict = {
        "cut": cut,
        "deal into new stack":deal_stack,
        "deal with increment":deal_increment
}

N_CARDS = 10007
deck = list(range(N_CARDS))
with open('day22.in') as f:
    for l in f:
        splitter = re.findall(r"([a-z ]+) ([-0-9]*)", l.strip() + " ")[0]
        this_func = function_dict[splitter[0]]
        args = [deck, int(splitter[1])] if splitter[1] else [deck]
        deck = this_func(*args)

print("PART 1")
print([i for i,v in enumerate(deck) if v == 2019][0])

with open('day22.in') as f:
    inputs = f.read().strip()
mapper = compute_mapper(inputs, N_CARDS)

j = [(mapper['a'] * i0 + mapper['b']) % N_CARDS for i0 in range(N_CARDS)]
result_deck = [x for _, x in sorted(zip(j, range(N_CARDS)))]
print("Using mapper...")
print([i for i,v in enumerate(result_deck) if v == 2019][0])



## ----------------------------------------------------------------------
## PART 2
## ----------------------------------------------------------------------
N_CARDS   = 119315717514047
N_SHUFFLE = 101741582076661

N_SHUF_BIN = format(N_SHUFFLE, 'b')

with open('day22.in') as f:
    inputs = f.read().strip()

mapper = compute_mapper(inputs, N_CARDS)
print(mapper)


def invert_mapper(mapper, m):
    moddiv = lambda x, m: pow(x, m-2, m)
    a_inv = moddiv(mapper['a'], m)
    return {'a' : a_inv, 
            'b' : (-mapper['b'] % m * a_inv) % m}

def square_mapper(mapper, m):
    return {'a' :(mapper['a'] * mapper['a']) % m, 
            'b' : ((mapper['a'] * mapper['b']) + mapper['b']) % m}

def apply_mapper(pos, mapper, m):
    return (pos * mapper['a'] + mapper['b']) % m


## Apply the full function sequence a number of times that corresponds to the binary sequence
func_apply_bindigit = [mapper]
for n in range(len(N_SHUF_BIN)-1):
    func_apply_bindigit.append(square_mapper(func_apply_bindigit[-1], N_CARDS))

func_inv_bindigit_1 = [invert_mapper(mapper, N_CARDS)]
for n in range(len(N_SHUF_BIN)-1):
    func_inv_bindigit_1.append(square_mapper(func_inv_bindigit_1[-1], N_CARDS))

func_inv_bindigit_2 = [invert_mapper(m, N_CARDS) for m in func_apply_bindigit]

assert(func_inv_bindigit_1 == func_inv_bindigit_2)

pos = 2020
for ix, d in enumerate(reversed(N_SHUF_BIN)):
    if int(d) == 1:
        print(ix)
        pos = apply_mapper(pos, func_inv_bindigit_1[ix], N_CARDS)

print(pos)



#### ## Exploratory solution
#### def pos_cut(position, n):
####     return (position - n) % N_CARDS
#### 
#### def pos_deal_increment(position, n):
####     return (n*position) % N_CARDS
#### 
#### def pos_deal_stack(position):
####     return N_CARDS - position
#### 
#### function_dict = {
####         "cut": pos_cut,
####         "deal into new stack":pos_deal_stack,
####         "deal with increment":pos_deal_increment
#### }
#### 
#### actions = []
#### product_of_expands = 1
#### sum_of_shifts = 0
#### sign = 1
#### with open('day22.in') as f:
####     for l in f:
####         splitter = re.findall(r"([a-z ]+) ([-0-9]*)", l.strip() + " ")[0]
####         this_func = function_dict[splitter[0]]
####         args = [int(splitter[1])] if splitter[1] else []
####         pos_func = lambda pos: this_func(*([pos] + args))
####         actions.append(pos_func)
####         if splitter[0] == 'cut':
####             sum_of_shifts += sign + int(splitter[1])
####         if splitter[0] == 'deal into new stack':
####             sign *= -1
####         if splitter[0] == 'deal with increment':
####             product_of_expands *= int(splitter[1])
#### 
#### print(product_of_expands // N_CARDS)
#### print(product_of_expands  % N_CARDS)
#### print(sum_of_shifts)
#### 
#### assert(pos_deal_increment(1, 62) == 62)
#### assert(pos_cut(101, 100) == 1)
#### assert(pos_cut(101, -100) == 201)
#### assert(pos_deal_stack(0) == N_CARDS)
#### 
#### print("PART 2")
#### pos = 2020
#### pos_prev = pos
#### 
#### def apply_all_shuffle(pos):
####     for f in actions:
####         pos = f(pos)
####     return pos
#### 
#### 
#### import numpy as np
#### 
#### np.random.seed(90210)
#### random_pos = [np.random.randint(N_CARDS) for i in range(10000)]
#### all_deltas = {(pos - apply_all_shuffle(pos)) % N_CARDS for pos in random_pos}
#### if (len(all_deltas) != 1):
####     raise NotImplementedError("Assuming every random delta is identical, other solution not implemented")
#### 
#### delta_size = next(iter(all_deltas))
#### print(f"Found delta size of {delta_size}")
#### 
#### 
#### lands_in_2020 = (2020 - delta_size * N_SHUFFLE) % N_CARDS
#### print(f"Lands in 2020: {lands_in_2020}")



