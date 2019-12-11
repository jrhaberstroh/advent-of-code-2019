## def num_sight_recursive(asteroid_map_masked, newest_pos, visited_pos, center):
##     asteroid_map_masked = np.copy(asteroid_map_masked)
##     one_off = (-1,0,1)
##     center     = np.array(center)
##     shape      = asteroid_map_masked.shape
##     nrow, ncol = asteroid_map_masked.shape
##     trial_pos = {
##             (x+dx,y+dy) 
##             for dx in one_off 
##             for dy in one_off 
##             for x,y in newest_pos 
##             if (x+dx < nrow and x+dx >= 0 and y+dy < ncol and y+dy >= 0)
##     } - visited_pos
##     if len(trial_pos) == 0:
##         return 0
##     new_asteroid = {pos for pos in trial_pos if asteroid_map_masked[pos]}
##     new_offset   = {(x1-center[0], y1-center[1]) for x1,y1 in new_asteroid}
##     for offset in new_offset:
##         np_offset = np.array(offset) // math.gcd(*offset)
##         n = 2
##         while True:
##             np_offset_pos = np_offset*n + center
##             if np.any(np_offset_pos < (0,0)) or np.any(np_offset_pos >= shape):
##                 break
##             else:
##                 asteroid_map_masked[tuple(np_offset_pos)] = 0
##             n += 1
##     all_visited = visited_pos.union(trial_pos)
##     n_out     = len(new_asteroid)
##     n_recurse = num_sight_recursive(asteroid_map_masked, trial_pos, all_visited, center)
##     return n_out + n_recurse
## 
## def get_num_sight(asteroid_map, asteroid_pos, pos):
##     asteroid_map      = np.copy(asteroid_map)
##     visited_pos       = {pos}
##     asteroid_map[pos] = 0
##     return num_sight_recursive(asteroid_map, visited_pos, visited_pos, pos)


## def remove_common_factor(x, y):
##     max_norm = max(abs(x),abs(y))
##     if x == 0 or y == 0:
##         return (x/max_norm, y/max_norm)
##     this_factor = math.gcd(abs(x), abs(y))
##     x, y = x//this_factor, y//this_factor
##     return (x,y)
## 
## def get_num_sight(asteroid_pos, pos):
##     other_asteroid = asteroid_pos - {pos}
##     dists      = {tuple(x - y for x,y in zip(other, pos)) for other in other_asteroid}
##     dists_norm = { remove_common_factor(dist[1], dist[0]) for dist in dists }
##     return len(dists_norm)


