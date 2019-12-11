import functools

width = 25
height = 6

with open("day8.img") as f:
    s_image = f.read().strip()

rows = tuple(tuple(int(x) for x in s_image[width*i:width*(i+1)]) for i in range(len(s_image)//width) )
layers = tuple(rows[height*i:height*(i+1)] for i in range(len(rows)//height))

num_each = [[sum(sum(int(p == num) for p in r) for r in l)  for l in layers]  for num in (0,1,2)]
min_zero_ind = tuple(i for i,x in enumerate(num_each[0]) if x == min(num_each[0]))
if (len(min_zero_ind)) > 1:
    raise RuntimeException()
min_zero_ind = next(iter(min_zero_ind))
print(num_each[1][min_zero_ind] * num_each[2][min_zero_ind])


# Now flatten the image -- use a "reduce" paradigm
def reduce_image(a, b):
    return tuple(tuple(pa if pb == 2 else pb for pa, pb in zip(ra, rb) ) for  ra, rb in zip(a,b)) 

image = functools.reduce(reduce_image, layers[::-1])
[print("".join(tuple(" " if p == 0 else "*" for p in  r))) for r in image]



import numpy as np
a_layers = np.reshape([int(x) for x in s_image], newshape = (-1, 25, 6), order = 'C')
flatten = functools.reduce(lambda a, b: np.where(b == 2, a, b), a_layers[::-1])
[print("".join(l)) for l in np.where(flatten, '*', ' ')]
