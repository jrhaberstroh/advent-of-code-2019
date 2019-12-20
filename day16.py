import numpy as np
import itertools

with open('day16.in') as f:
    s_seq = f.read().strip()

# s_seq = "12345678"
# s_seq = "80871224585914546619083218645595"
# s_seq = "03036732577212944063491565474664"
# s_seq = "03081770884921959731165446850517"
seq = [int(s) for s in s_seq]

BASE_SEQ = [0, 1, 0, -1]

def apply_fft(seq, k):
    k += 1
    mult_seq = [BASE_SEQ[((i+1) // k) % len(BASE_SEQ)] for i,x in enumerate(seq)]
    apply_sum = sum([s * f for s,f in zip(seq, mult_seq)])
    return(abs(apply_sum) % 10)



if __name__ == "__main__":
    PART = 2

    if PART == 1:
        seq_update = seq
        for i in range(100):
            seq_update = [apply_fft(seq_update, k) for k in range(len(seq_update))]
        print(seq_update)

    num_iterations = 100

    print(len(seq))
    l_extended_seq = len(seq) * 10000
    i_target_offset = int("".join([str(x) for x in seq[0:7]])) + 1
    i_first_value = i_target_offset - num_iterations
    l_result = l_extended_seq - i_first_value
    print(f"Target offset: {i_target_offset}")
    print(f"Extended seq:  {l_extended_seq}")
    print(f"Length result: {l_result}")
    assert(i_target_offset * 2 > l_extended_seq)

    print(f"First Value:   {i_first_value}")
    i_appendix = i_first_value % len(seq)

    arr_appendix = seq[i_appendix:]
    n_copies = l_result // len(seq)
    
    my_arr = [arr_appendix] + [seq for i in range(n_copies)]
    my_arr = np.array(list(itertools.chain.from_iterable(my_arr)))
    # print(n_copies)
    # print(len(my_arr))

    for i in range(num_iterations):
        my_arr = (np.cumsum(my_arr[::-1])[::-1]) % 10
    print(len(my_arr))

    print("".join([str(x) for x in my_arr[num_iterations-1:num_iterations-1+8]]))

