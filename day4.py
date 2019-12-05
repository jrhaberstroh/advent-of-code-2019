valid_range = [248345, 746315]

def is_sequential_and_pair(x):
    x = str(x)
    true_pair = False
    found_pair = False
    invalid_pair = False
    for x_prev, x_next in zip(x[:-1], x[1:]):
        #----- Sequential logic -----
        if int(x_next) < int(x_prev):
            return False

        #----- Pair logic ------
        if x_next == x_prev:
            # First activate found_pair,
            # then activate invalid_pair
            if not found_pair:
                found_pair = True
            else:
                invalid_pair = True
        else:
            # Only makr a true pair if it is found
            # but not invalid, and we have exited
            # a current pair
            if found_pair and invalid_pair == False:
                true_pair = True
            found_pair = False
            invalid_pair = False
    # Mark true pair for the final set
    if found_pair and invalid_pair == False:
        true_pair = True
    return true_pair

count_valid = 0
for x_test in range(valid_range[0], valid_range[1]+1):
    if is_sequential_and_pair(x_test):
        count_valid += 1

print(is_sequential_and_pair(125578))
print(is_sequential_and_pair(126578))
print(is_sequential_and_pair(125678))
print(is_sequential_and_pair(125699))

print(count_valid)

