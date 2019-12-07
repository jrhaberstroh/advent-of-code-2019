import sys

with open("day6.in") as f:
    orbits = [l.strip().split(')') for l in f.readlines()]


def add_orbit_depth(orbits, obj, depth):
    suborbits = [o for o in orbits if o[0] == obj]
    if not suborbits:
        return depth
    subdepths = [add_orbit_depth(orbits, o[1], depth+1) for o in suborbits]
    return sum(subdepths) + depth

orbit_checksum = add_orbit_depth(orbits, 'COM', 0)
print(orbit_checksum)


def min_route(orbits, start, end, dist):
    tfers = [o for o in orbits if o[0] == obj or o[1] == obj]
    if not tfers:
        return depth
    subdepths = [add_orbit_depth(orbits, o[1], depth+1) for o in suborbits]
    return sum(subdepths) + depth


def reverse_path(orbits, obj):
    orbiting = [o for o in orbits if o[1] == obj]
    if len(orbiting) > 1:
        raise RuntimeError("")
    if not orbiting:
        return [obj]
    return [obj] + reverse_path(orbits, orbiting[0][0])

you_path = reverse_path(orbits, "YOU")
san_path = reverse_path(orbits, "SAN")

print(you_path)
print(san_path)
min_dist = None
min_junction = None
for you_d, you_obj in enumerate(you_path):
    for san_d, san_obj in enumerate(san_path):
        if you_obj == san_obj:
            this_dist = (you_d - 1) + (san_d - 1)
            if min_dist is None:
                min_dist = this_dist
                min_junction = you_obj
            elif this_dist < min_dist:
                min_dist = this_dist
                min_junction = you_obj

print(min_dist)
print(min_junction)

        

