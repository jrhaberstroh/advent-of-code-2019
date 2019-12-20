import numpy as np
import math

X = [[-14, -4, -11],
      [-9, 6, -7],
      [4, 1, 4],
      [2, -14, -9]]

# X = [[ -1,   0,  2],
#      [  2, -10, -7],
#      [  4,  -8,  8],
#      [  3,   5, -1]]

# X = [[-8, -10,  0],
#      [ 5,   5, 10],
#      [ 2,  -7,  3],
#      [ 9,  -8, -3]]

X = np.array(X, dtype = int)
V = np.zeros(X.shape, dtype = int)

X0 = X.copy()
V0 = V.copy()


get_energy = lambda X, V: int(np.array([np.abs(R).sum(axis = 1) for R in (X, V)]).prod(axis = 0).sum())


E = get_energy(X, V)

flattenize = lambda X, V: tuple([*X.flatten(), *V.flatten()])
print(flattenize(X, V))

state_set_ax = {0:set(), 1:set(), 2:set()}
state_set = set()

t = 0
period = []
while t < 400000:
    if t % 10000 == 0:
        print(f"{t}")

    axis_to_remove = []
    for axis in state_set_ax.keys():
        # this_state = flattenize(X[:,axis], V[:,axis])
        # this_set   = state_set_ax[axis]
        # if this_state in this_set:
        if t != 0 and all(X[:,axis] == X0[:, axis]) and all(V[:, axis] == V[:, axis]):
            print(f"Found exact state match for axis {axis} at time {t+1}")
            axis_to_remove.append(axis)
            period.append(t+1)
        # else:
        #     state_set_ax[axis] = this_set.union({this_state})
    for axis in axis_to_remove:
        state_set_ax.pop(axis)
    if len(state_set_ax) == 0:
        print(f"Total period: {np.lcm.reduce(period)}")
        break

    if t in (1000,):
        print(f"Energy at Step {t}: {get_energy(X, V)}")

    F = np.array([
            np.array([
                [0 if val == 0 else val / abs(val) 
                    for val in x_other-x_self]
            for x_other in X ]).sum(axis = 0) # axis 0 is over all others
        for x_self in X
    ])
    V = V + F
    X = X + V
    t += 1


7030162386
4686774924
