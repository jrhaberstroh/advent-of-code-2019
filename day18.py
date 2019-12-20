import numpy as np 
from typing import Tuple
import resource 
import sys

import operator
class AddTuple(tuple):
    def __add__(self, other):
        return self.__class__(map(operator.add, self, other))

# pre-compute n^2 shortest path from key_i to key_j
#  ** return conditionals for each path

# fully recursive solution: n^n solution :(
#  -- but try it first!


def single_where(arr, value):
    all_matches = np.where(tunnel_map == value)
    if (len(all_matches[0]) != 1):
        raise ValueError(f"Not exactly one match found for {value}")
    return ( all_matches[0][0], all_matches[1][0] )

UP    = AddTuple((-1,  0))
DOWN  = AddTuple(( 1,  0))
LEFT  = AddTuple(( 0, -1))
RIGHT = AddTuple(( 0,  1))
all_directions = [UP, DOWN, LEFT, RIGHT]

def get_accessible_keys_helper(tunnel_map, pos: AddTuple, length):
    if tunnel_map[pos] == '#':
        return []
    if tunnel_map[pos].isupper():
        return []
    if tunnel_map[pos].islower():
        return [(tunnel_map[pos], length)]

    copy_tm = tunnel_map.copy()
    copy_tm[pos] = '#'

    while True:
        valid_moves = [
                pos + vec
                for vec in all_directions 
                if copy_tm[pos + vec] == '.' or copy_tm[pos + vec].islower()
        ]
        if len(valid_moves) == 1 and copy_tm[next(iter(valid_moves))] == '.':
            pos = next(iter(valid_moves))
            copy_tm[pos] = '#'
            length += 1
        else:
            # Aggregate all results
            return [ x
                    for move in valid_moves
                    for x in get_accessible_keys_helper(copy_tm, move, length + 1) 
                    if x is not None
            ]

def get_accessible_keys(tunnel_map, pos: tuple):
    pos = AddTuple(pos)
    all_result = get_accessible_keys_helper(tunnel_map, pos, 0)
    reduced_result = {}
    for key, value in all_result:
        if key in reduced_result:
            reduced_result[key] = min(reduced_result[key], value)
        else:
            reduced_result[key] = value 
    return reduced_result


def search_keys_recursive(tunnel_map, pos: tuple, wall_starting_pos = False):
    all_accessible_keys = get_accessible_keys(tunnel_map, pos)
    if wall_starting_pos:
        tunnel_map[pos] = '#'
    print(all_accessible_keys)
    if len(all_accessible_keys) == 0:
        return 0

    trial_dists = []
    for key, dist in all_accessible_keys.items():
        pos      = single_where(tunnel_map, key)
        copy_tm = tunnel_map.copy()
        copy_tm[     pos] = '.'
        try:
            door_pos = single_where(tunnel_map, key.upper())
            copy_tm[door_pos] = '.'
        except ValueError:
            pass
        trial_dists.append(dist + search_keys_recursive(copy_tm, pos))
    return(min(trial_dists))




with open('day18.in') as f:
    s_map = f.read()

## s_map = """
## ########################
## #@..............ac.GI.b#
## ###d#e#f################
## ###A#B#C################
## ###g#h#i################
## ########################
## """

tunnel_map = np.array([[ch for ch in l.strip()] for l in s_map.strip().split('\n')])


opening_pos = single_where(tunnel_map, '@')
print(get_accessible_keys(tunnel_map, opening_pos))
print(search_keys_recursive(tunnel_map, opening_pos, wall_starting_pos = True))

# TODO: Insert choke points
choke_points = [AddTuple(opening_pos) + AddTuple(a) for a in ((1,1), (1,-1), (-1,1), (-1,-1))]
for i, cp in enumerate(choke_points):
    tunnel_map[cp] = i


# TODO: Create sparse distance matrix
## do DFS:
## return (prev_point, new_point, dist)




# TODO: Define recursion through distance matrix






