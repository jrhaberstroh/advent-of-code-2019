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

WALKWAY_SPACE = ('.',)
INVALID_SPACE = ('#', ' ')

## ---------  Recursion to find all valid pathways ----------
def get_accessible_entities_helper(tunnel_map, pos: AddTuple, length):
    if tunnel_map[pos] in INVALID_SPACE:
        return []
    elif tunnel_map[pos] != '.':
        return [(tunnel_map[pos], length)]

    copy_tm = tunnel_map.copy()
    copy_tm[pos] = INVALID_SPACE[0]

    while True:
        valid_moves = [
                pos + vec
                for vec in all_directions 
                if not copy_tm[pos + vec] in INVALID_SPACE
        ]
        if len(valid_moves) == 1 and copy_tm[next(iter(valid_moves))] == WALKWAY_SPACE:
            pos = next(iter(valid_moves))
            copy_tm[pos] = INVALID_SPACE[0]
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
        self.print_width = 4

    ## Query all states available from one particular state
    def get_available_states(self, state_list):
        ix_all_states = [np.where(self.index_names == k)[0][0] for k in state_list]
        available_states = {  
                target:dist
                for ix_state in ix_all_states
                for dist, target in zip(self.dist_mtx[ix_state, :], self.index_names) 
                if dist > 0
        }
        return(available_states)

    ## Collect some values and return a new MapDistMtx object
    def collect(self, state, new_state):
        old_value = [k1 for k1,k2 in zip(state, new_state) if k1 != k2][0]
        new_key   = [k2 for k1,k2 in zip(state, new_state) if k1 != k2][0]

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
            "".join([self.index_names[i-1].rjust(self.print_width) if i >= 1 and i <= len(self.index_names) else " "*self.print_width, " "] + 
                [
                str(d).rjust(self.print_width) for d in row
                ] +
                [" ", self.index_names[i-1] if i >= 1 and i <= len(self.index_names) else " "])    
            for i, row in enumerate([self.index_names] + list(self.dist_mtx) + [self.index_names])
            ]))


def make_dist_mtx(this_map, ignore_elements = INVALID_SPACE + WALKWAY_SPACE):
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
    return MapDistMtx(dist_mtx, all_elements)

# ---------- Spec out the state class -----------
@dataclass(frozen = True)
class RobotState:
    site: str
    level: int

def update_state(state, i_pos, value):
    new_pos  = "".join(
            value if i == i_pos else old_value
            for i, old_value in enumerate(state.pos)
    )
    new_keys = "".join(sorted(state.keys + state.pos[i_pos]))
    return RobotState(new_pos, new_keys)


def convert_donut_map(s_map):
    tunnel_map = [[ch for ch in l] for l in s_map.split('\n')]
    line_len = max([len(l) for l in tunnel_map])

    tunnel_map = np.array([[l[i] if i < len(l) else ' ' for i in range(line_len)] for l in s_map.strip('\n').split('\n')])
    print(tunnel_map.shape)
    
    outer_span = [(0, s-1) for s in tunnel_map.shape]
    outer_pos_ix = [(tuple(p_init+p for p in pos), ix)
            for ix in (0,1)
            for p_init, pos in zip(outer_span[ix], [(0,1), (-1,0)])]
    
    outers = [np.char.add(*(tunnel_map if ix == 0 else tunnel_map.T)[pos,:])
              for pos, ix in outer_pos_ix]
    print(outers)
    
    tunnel_map[  :2,  : ] = ' '
    tunnel_map[-2: ,  : ] = ' '
    tunnel_map[  : ,  :2] = ' '
    tunnel_map[  : ,-2: ] = ' '
    for l in tunnel_map:
        print(" ".join(l))
    
    inner_coords = np.where(np.char.isalpha(tunnel_map))
    inner_span = [(min(inner_coords[i]), max(inner_coords[i])) for i in (0,1)]
    print(inner_span)
    
    inner_pos_ix = [(tuple(p_init+p for p in pos), ix)
            for ix in (0,1)
            for p_init, pos in zip(inner_span[ix], [(0,1), (-1,0)])]
    
    inners = [np.char.add(*(tunnel_map if ix == 0 else tunnel_map.T)[pos,:])
              for pos, ix in inner_pos_ix]
    print(inners)
    
    tunnel_map = np.array([[v if not isalpha else ' ' for v, isalpha in zip(vec, np.char.isalpha(vec))] for vec in tunnel_map], 'U3')
    

    print(outer_pos_ix)
    print(inner_pos_ix)
    
    for which_dir, ((pos, ix), outer) in enumerate(zip(outer_pos_ix, outers)):
        this_dir = 1 if which_dir % 2 == 0 else -1
        this_ix  = 1 if which_dir % 2 == 0 else  0
        target_line = pos[this_ix] + this_dir 
        print(target_line)
        for j, (v, isalpha) in enumerate(zip(outer, np.char.isalpha(outer))):
            if isalpha:
                if ix == 0:
                    tunnel_map[target_line, j] = v if v in ("AA", "ZZ") else v+"o"
                if ix == 1:
                    tunnel_map[j, target_line] = v if v in ("AA", "ZZ") else v+"o"
    
    for which_dir, ((pos, ix), inner) in enumerate(zip(inner_pos_ix, inners)):
        this_dir = 1 if which_dir % 2 == 1 else -1
        this_ix  = 1 if which_dir % 2 == 1 else  0
        target_line = pos[this_ix] + this_dir 
        print(target_line)
        for j, (v, isalpha) in enumerate(zip(inner, np.char.isalpha(inner))):
            if isalpha:
                if ix == 0:
                    tunnel_map[target_line, j] = v if v in ("AA", "ZZ") else v+"i" 
                if ix == 1:
                    tunnel_map[j, target_line] = v if v in ("AA", "ZZ") else v+"i"

    return(tunnel_map)

# PART 1
with open('day20.in') as f:
    s_map = f.read()


## s_map = """
##          A
##          A
##   #######.#########
##   #######.........#
##   #######.#######.#
##   #######.#######.#
##   #######.#######.#
##   #####  B    ###.#
## BC...##  C    ###.#
##   ##.##       ###.#
##   ##...DE  F  ###.#
##   #####    G  ###.#
##   #########.#####.#
## DE..#######...###.#
##   #.#########.###.#
## FG..#########.....#
##   ###########.#####
##              Z
##              Z
## """

tunnel_map = convert_donut_map(s_map)

# dist_mtx = MapDistMtx(*get_accessible_entities(tunnel_map))
dist_mtx = make_dist_mtx(tunnel_map)

for ix, name in enumerate(dist_mtx.index_names):
    if name[-1] == 'i':
        other_name = name[0:2]+'o'
        other_ix = np.where(dist_mtx.index_names == other_name)[0][0]
        dist_mtx.dist_mtx[ix, other_ix] = 1
        dist_mtx.dist_mtx[other_ix, ix] = 1
print(dist_mtx)


visited = {'AA': 0}
while True:
    print(visited.items())
    visited_new = {
            state_new: d+d_new
            for state_old, d in visited.items()
            for state_new, d_new in {**dist_mtx.get_available_states([state_old]), state_old:d}.items()
            if state_new not in visited or 
              (state_new in visited and d + d_new <= visited.get(state_new))
    }
    print(visited_new)
    if visited_new == visited:
        break
    else:
        visited = visited_new
    print(visited)


## Need -2 correction for two extra spaces walked?
print(visited['ZZ'] - 2)



# PART 2
with open('day20.in') as f:
    s_map = f.read()

## s_map = """
##              Z L X W       C                 
##              Z P Q B       K                 
##   ###########.#.#.#.#######.###############  
##   #...#.......#.#.......#.#.......#.#.#...#  
##   ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  
##   #.#...#.#.#...#.#.#...#...#...#.#.......#  
##   #.###.#######.###.###.#.###.###.#.#######  
##   #...#.......#.#...#...#.............#...#  
##   #.#########.#######.#.#######.#######.###  
##   #...#.#    F       R I       Z    #.#.#.#  
##   #.###.#    D       E C       H    #.#.#.#  
##   #.#...#                           #...#.#  
##   #.###.#                           #.###.#  
##   #.#....OA                       WB..#.#..ZH
##   #.###.#                           #.#.#.#  
## CJ......#                           #.....#  
##   #######                           #######  
##   #.#....CK                         #......IC
##   #.###.#                           #.###.#  
##   #.....#                           #...#.#  
##   ###.###                           #.#.#.#  
## XF....#.#                         RF..#.#.#  
##   #####.#                           #######  
##   #......CJ                       NM..#...#  
##   ###.#.#                           #.###.#  
## RE....#.#                           #......RF
##   ###.###        X   X       L      #.#.#.#  
##   #.....#        F   Q       P      #.#.#.#  
##   ###.###########.###.#######.#########.###  
##   #.....#...#.....#.......#...#.....#.#...#  
##   #####.#.###.#######.#######.###.###.#.#.#  
##   #.......#.......#.#.#.#.#...#...#...#.#.#  
##   #####.###.#####.#.#.#.#.###.###.#.###.###  
##   #.......#.....#.#...#...............#...#  
##   #############.#.#.###.###################  
##                A O F   N                     
##                A A D   M                    
## """


print("PRINTING MAP")
print(s_map)
tunnel_map = convert_donut_map(s_map)


# dist_mtx = MapDistMtx(*get_accessible_entities(tunnel_map))
dist_mtx = make_dist_mtx(tunnel_map)

def get_new_depth(s_old, s_new): 
    if s_new[0:2] == s_old[0:2] and s_new[-1] == 'o' and s_old[-1] == 'i':
        return 1
    elif s_new[0:2] == s_old[0:2] and s_new[-1] == 'i' and s_old[-1] == 'o':
        return -1
    return 0

def get_new_state(sl_old, s_new):
    return (s_new, sl_old[1] + get_new_depth(sl_old[0], s_new))

## def is_allowed_site_level(site_level):
##     if site_level[1] != 1:
##         if site_level[0] in ("ZZ", "AA"):
##             return False
##     return True

## Closure on dist_mtx_outer, dist_mtx_inner
def get_available_site_levels(dist_mtx, site_level_old):
    available_site_dist = dist_mtx.get_available_states([site_level_old[0]])
    new_states = {
            get_new_state(site_level_old, new_site):d 
            for new_site, d 
            in available_site_dist.items()
    }
    ## Add teleport moves to the list
    teleport_state = {}
    this_site = site_level_old[0]
    this_level = site_level_old[1]
    if this_site[-1] == 'i':
        teleport_state = {(this_site[0:2]+'o', this_level+1):1}
    if this_site[-1] == 'o' and this_level != 1:
        teleport_state = {(this_site[0:2]+'i', this_level-1):1}
    return({**new_states, **teleport_state})

# def dfs_recursive_maze(dist_mtx_outer, dist_mtx_inner, visited, maxdepth):

visited = {('AA', 1): 0}
remaining_depth = 500
max_depth = 40
while remaining_depth > 0:
    print(remaining_depth)
    remaining_depth -= 1

    visited_new = { state_new:d+d_new
            for site_level_old, d in visited.items()
            ## Get all available moves, and also include the null move
            for state_new, d_new in {**get_available_site_levels(dist_mtx, site_level_old), site_level_old:0}.items()
            if site_level_old[1] <= max_depth and (
                state_new not in visited or (state_new in visited and d + d_new <= visited.get(state_new)))
    }
    if visited_new == visited:
        break
    else:
        visited = visited_new

## Need -2 correction for two extra spaces walked?
# [print(v) for k,v in visited.items() if k[0] == 'ZZ']
# print("XIo9", visited[('XIo', 9)])
print("AA to PPo (passing through YAi)", visited[('PPo', 4)])
print("+8 loop @ YAi", visited[('YAi', 9)] - visited[('YAi', 1)])
print("-19 loop @ PPo", visited[('PPo', 9)] - visited[('PPo', 28)])
print("PPo to ZZ", visited[('ZZ', 8)] - visited[('PPo', 20)])

print("Heuristic distance to ZZ1 = ", 
        (visited[('PPo', 4)] + 
            ## +104 = PPo 104
            (visited[('YAi', 9)] - visited[('YAi', 1)]) * 13 + 
            ## - 95 = PPo 13
            (visited[('PPo', 9)] - visited[('PPo', 28)]) * 5 +
            ## PPo13 up 12 floors to ZZ1
            visited[('ZZ', 8)] - visited[('PPo', 20)])
)

try:
    print("Dist to ZZ1: ", visited[('ZZ', 1)])
except IndexError:
    print("No route made it to ZZ1")







