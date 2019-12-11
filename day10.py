import numpy as np
import math

## PART 1
def get_num_sight(asteroid_pos, pos):
    other_asteroid = asteroid_pos - {pos}
    disps      = [
            tuple(x_o - x_p for x_o,x_p in zip(other, pos)) 
            for other in other_asteroid
    ]
    angles     = { int(round(math.atan2(disp[0], disp[1]) * 1E8)) for disp in disps }
    return len(angles)

def parse_asteroids(text):
    asteroid_map = np.array([[0 if v == '.' else 1 for v in l] for l in text])
    asteroid_pos = {tuple(pos) for pos in np.argwhere(asteroid_map)}
    return (asteroid_map, asteroid_pos)


def solve_asteroid(text, show = False):
    asteroid_map, asteroid_pos = parse_asteroids(text)    

    result = {
            pos:get_num_sight(asteroid_pos, pos) 
            for pos in asteroid_pos
    }
    num_can_see = result.values()
    can_see_pos = result.keys()

    if show:
        asteroid_map_show = np.copy(asteroid_map)
        for pos, n in result.items():
            asteroid_map_show[pos] = n
        for l in asteroid_map_show:
            print("".join('.' if x == 0 else str(x) for x in l))
    

    most_can_see = max(num_can_see)
    optimum_pos = tuple(p for p, n in zip(can_see_pos, num_can_see) if n == max(num_can_see))

    return(most_can_see, optimum_pos, len(asteroid_pos))



## PART 2
def fire_the_laser(text, pos, show = False):
    asteroid_map, asteroid_pos = parse_asteroids(text)    

    if show:
        for i, row in enumerate(asteroid_map):
            print(''.join([
                'X' if i == pos[0] and j == pos[1] else 
                '#' if v == 1 else '.' 
                for j, v in enumerate(row)
            ]))
    
    other_asteroid = list(asteroid_pos - {pos})
    disps      = [ tuple(x_o - x_p for x_o,x_p in zip(other, pos)) for other in other_asteroid ]
    positive_atan = lambda y, x: math.atan2(y, x) if y >= 0 else math.atan2(y, x) + 2 * np.pi
    angles     = [ int(round(positive_atan(disp[1], -disp[0]) * 1E8)) for disp in disps ]
    dists2     = [ disp[0]**2 + disp[1]**2 for disp in disps ]

    print(len(dists2), len(angles), len(other_asteroid))

    
    sorted_angles = sorted(list(set(angles)))
    angle_to_pos  = {a:[] for a in angles}
    angle_to_dist = {a:[] for a in angles}

    # Sort in order of distances
    for pos, a, d in sorted(zip(other_asteroid, angles, dists2), key=lambda arr:arr[2]):
        angle_to_pos[a].append(pos)
        angle_to_dist[a].append(d)
        this_dists = angle_to_dist[a]
        if not all(this_dists[i] <= this_dists[i+1] for i in range(len(this_dists)-1)):
            print(pos, a, d)
            print(this_dists)
            raise AssertionError("Failed test")

    explode_order = []
    for i, a in enumerate(sorted_angles):
        if i < 10:
            print(a, angle_to_pos[a], angle_to_dist[a])
        if angle_to_pos[a]:
            explode_order.append(angle_to_pos[a].pop(0))

    return explode_order
    



with open('day10.in') as f:
    text = [l.strip() for l in f.readlines()]

most_can_see, opt_pos, num_asteroids = solve_asteroid(text)
print(most_can_see, opt_pos[0])
explode_order = fire_the_laser(text, opt_pos[0], show=False)
def rev_all(x):
    try:
        return [y[::-1] for y in x]
    except IndexError:
        return x[::-1]
print(rev_all(explode_order[0:3]))
print(rev_all(explode_order[ 10 - 1]))
print(rev_all(explode_order[ 20 - 1]))
print(rev_all(explode_order[ 50 - 1]))
print(rev_all(explode_order[199 - 1]))
print(rev_all(explode_order[200 - 1]))


