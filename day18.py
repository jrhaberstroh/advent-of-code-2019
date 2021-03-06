import numpy as np 
import resource 
import sys
import operator
from typing import Tuple
from dataclasses import dataclass

class AddTuple(tuple):
    def __add__(self, other):
        return self.__class__(map(operator.add, self, other))

UP    = AddTuple((-1,  0))
DOWN  = AddTuple(( 1,  0))
LEFT  = AddTuple(( 0, -1))
RIGHT = AddTuple(( 0,  1))
all_directions = [UP, DOWN, LEFT, RIGHT]

def single_where(arr, value):
    all_matches = np.where(tunnel_map == value)
    if (len(all_matches[0]) != 1):
        raise ValueError(f"Not exactly one match found for {value}")
    return ( all_matches[0][0], all_matches[1][0] )


## ---------  Recursion to find all valid pathways ----------
def get_accessible_entities_helper(tunnel_map, pos: AddTuple, length):
    if tunnel_map[pos] == '#':
        return []
    elif tunnel_map[pos] != '.':
        return [(tunnel_map[pos], length)]

    copy_tm = tunnel_map.copy()
    copy_tm[pos] = '#'

    while True:
        valid_moves = [
                pos + vec
                for vec in all_directions 
                if copy_tm[pos + vec] != '#'
        ]
        if len(valid_moves) == 1 and copy_tm[next(iter(valid_moves))] == '.':
            pos = next(iter(valid_moves))
            copy_tm[pos] = '#'
            length += 1
        else:
            # Aggregate all results
            return [ x
                    for move in valid_moves
                    for x in get_accessible_entities_helper(copy_tm, move, length + 1) 
                    if x is not None
            ]

def get_accessible_entities(tunnel_map, pos: tuple):
    this_tm = tunnel_map.copy()
    this_tm[pos] = '.'
    pos = AddTuple(pos)
    all_result = get_accessible_entities_helper(this_tm, pos, 0)
    reduced_result = {}
    for key, value in all_result:
        if key in reduced_result:
            reduced_result[key] = min(reduced_result[key], value)
        else:
            reduced_result[key] = value 
    return reduced_result



## ----  Create distance matrix using the above recursion code  -----
def make_dist_mtx(this_map, ignore_elements = ['.', '#']):
    uq_elements = [x for x in np.unique(tunnel_map) if not x in ignore_elements]
    all_elements = np.array(sorted(uq_elements))
    dist_mtx = np.zeros((len(all_elements), len(all_elements)), dtype = int)
    for i_x, x_elem in enumerate(all_elements):
        elem_pos = single_where(tunnel_map, x_elem)
        distances = get_accessible_entities(tunnel_map, elem_pos)
        for y_elem, dist in distances.items():
            i_y = np.where(all_elements == y_elem)[0]
            dist_mtx[i_x, i_y] = int(dist)
    assert((dist_mtx == dist_mtx.T).all())
    return (dist_mtx, all_elements)

def remove_connection_inplace(dist_mtx, i, index_names = None):
    j_conn = [j for j, d in enumerate(dist_mtx[i]) if d > 0]
    for j in j_conn:
        for k in (k for k in j_conn if k > j):
            if j == k:
                continue
            through_path = dist_mtx[j, i] + dist_mtx[i, k]
            if dist_mtx[j, k] == 0:
                min_dist = through_path
            else:
                min_dist     = min(through_path, dist_mtx[j, k])
            dist_mtx[j, k] = min_dist
            dist_mtx[k, j] = min_dist
    dist_mtx[i, :] = 0
    dist_mtx[:, i] = 0

## Need to provide simple constructor to allow distance matrix to make copies of itself
class MapDistMtx:
    def __init__(self, dist_mtx, index_names):
        self.dist_mtx = dist_mtx.copy()
        self.index_names = index_names.copy()

    ## Query all states available from one particular state
    def get_available_states(self, state):
        ix_all_states = [np.where(self.index_names == k)[0][0] for k in state.pos]
        available_states = {  
                update_state(state, i_robot, target):dist
                for i_robot, ix_state in enumerate(ix_all_states)
                for dist, target in zip(self.dist_mtx[ix_state, :], self.index_names) 
                if target.islower() and dist > 0
        }
        return(available_states)

    ## Collect some values and return a new MapDistMtx object
    def collect(self, state, new_state):
        old_value = [k1 for k1,k2 in zip(state.pos, new_state.pos) if k1 != k2][0]
        new_key   = [k2 for k1,k2 in zip(state.pos, new_state.pos) if k1 != k2][0]

        dist_mtx = self.dist_mtx.copy()
        
        ## Remove linkage from the position being moved
        i_moving = np.where(self.index_names == old_value)[0][0]
        i_key    = np.where(self.index_names == new_key)[0][0]
        dist_travelled = dist_mtx[i_moving, i_key]
        remove_connection_inplace(dist_mtx, i_moving, self.index_names)

        ## Remove the door if the new key matches a door
        if new_key.islower() and (new_key.upper() in self.index_names):
            i_door = np.where(self.index_names == new_key.upper())[0][0]
            remove_connection_inplace(dist_mtx, i_door, self.index_names)

        return dist_travelled, MapDistMtx(dist_mtx, self.index_names)


    def keys_remaining(self):
        return [
                n 
                for d_row, n in zip(self.dist_mtx, self.index_names) 
                if any(d_row != 0) and n.islower()
        ]
        
    def __str__(self):
        return("\n".join([
            "".join([self.index_names[i-1] if i >= 1 and i <= len(self.index_names) else " ", " "] + 
                [
                str(d).rjust(3) for d in row
                ] +
                [" ", self.index_names[i-1] if i >= 1 and i <= len(self.index_names) else " "])    
            for i, row in enumerate([self.index_names] + list(self.dist_mtx) + [self.index_names])
            ]))

# ---------- Spec out the state class -----------
@dataclass(frozen = True)
class RobotState:
    pos : str
    keys: str

def update_state(state, i_pos, value):
    new_pos  = "".join(
            value if i == i_pos else old_value
            for i, old_value in enumerate(state.pos)
    )
    new_keys = "".join(sorted(state.keys + state.pos[i_pos]))
    return RobotState(new_pos, new_keys)


## ---------  Use distance matrix to quickly search paths -----------
def find_best_path_multi(input_dist_mtx, starting_pos):
    starting_state = RobotState(starting_pos, "")
    current_pathlen  = {starting_state:0}
    current_distmtx  = {starting_state:input_dist_mtx}
    
    counter = 0
    while True:
        new_pathlen = {}
        new_distmtx = {}

        for state, state_distmtx in current_distmtx.items():
            d_so_far = current_pathlen[state]
            possible_moves = state_distmtx.get_available_states(state)
            for move in possible_moves:
                d, reduced_dist_mtx = state_distmtx.collect(state, move)
             
                if move in new_pathlen:
                    new_pathlen[move] = min(d_so_far + d, new_pathlen[move])
                else:
                    new_pathlen[move] = d_so_far + d
                    new_distmtx[move] = reduced_dist_mtx
        if not new_pathlen:
            return(current_pathlen)
        current_pathlen  = new_pathlen.copy()
        current_distmtx = new_distmtx.copy()


# PART 1
with open('day18.in') as f:
    s_map = f.read()
tunnel_map = np.array([[ch for ch in l.strip()] for l in s_map.strip().split('\n')])
dist_mtx = MapDistMtx(*make_dist_mtx(tunnel_map))
print(min(find_best_path_multi(dist_mtx, "@").values()))


# PART 2
tunnel_map = np.array([[ch for ch in l.strip()] for l in s_map.strip().split('\n')])
center_pos = single_where(tunnel_map, '@')
tunnel_map[center_pos[0]-1:center_pos[0]+2,
           center_pos[1]-1:center_pos[1]+2] = '#'

i = 1
for dx in [-1, +1]:
    for dy in [-1, +1]:
        tunnel_map[center_pos[0]+dx, center_pos[1]+dy] = str(i)
        i += 1
dist_mtx = MapDistMtx(*make_dist_mtx(tunnel_map))
print(min(find_best_path_multi(dist_mtx, "1234").values()))

## Show the map
# print("\n".join([" ".join([s for s in row]) for row in tunnel_map])  )



