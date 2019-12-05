with open('day3.in') as f:
    wire_raw = f.readlines()

wire_cmd = [[(w[0], int(w[1:])) for w in l.strip().split(',')] for l in wire_raw]

wire_cmd_test = [[('U', 5), ('R', 3), ('D', 7)],
                 [('R', 8)]]

class WireLine:
    def __init__(self, wire):
        self.wire = wire
        self.ix = 0
        self.pos = [0, 0]
    def __iter__(self):
        return self
    def __next__(self):
        if self.ix >= len(self.wire):
            raise StopIteration
        ## if (self.ix == -1):
        ##     self.ix += 1
        ##     return(self.pos)
        this_cmd = self.wire[self.ix]
        self.ix += 1
        direction = this_cmd[0]
        value = this_cmd[1]

        # Horizontal is index 0
        # Vertical is index 1
        switcher_angle_sign = {
                'U': (1,  1)
               ,'D': (1, -1)
               ,'R': (0,  1)
               ,'L': (0, -1)
        }

        angle, sign = switcher_angle_sign.get(direction)
        other_angle = (angle + 1) % 2

        this_diff = [0, 0]
        this_diff[angle] = value * sign 
        
        fixed_position = self.pos[other_angle]
        moving_position_0 = self.pos[angle]

        self.pos = [x + d for x, d in zip(self.pos, this_diff)]

        moving_position_1 = self.pos[angle]

        return (angle, fixed_position, [moving_position_0, moving_position_1])

print(wire_cmd_test)
# wire_pos_test = [[x for x in  WirePos(this_wire)] for this_wire in wire_cmd_test]
wire_line_test = [[x for x in  WireLine(this_wire)] for this_wire in wire_cmd_test]
print(wire_line_test)

wire_line = [[x for x in  WireLine(this_wire)] for this_wire in wire_cmd]


def get_intersect(line1, line2, verbose = False):
    line_pair = [line1, line2]
    ## Return no-intersection if they are moving in the same direction
    if line1[0] == line2[0]:
        return []
    intersect = [0, 0]
    ## The intersection occurs on the direction orthogonal to the facing
    for line in line_pair:
        intersect[ (line[0] + 1) % 2 ] = line[1]
    ## Return no-intersection if they intersect at the origin
    if intersect == [0, 0]:
        return []

    def check_one(line1, line2):
        y  = line1[1]
        y0 = min(line2[2])
        y1 = max(line2[2])
        return ((y0 <= y) and (y <= y1))

    if verbose:
        print(check_one(line1, line2))
        print(check_one(line2, line1))
        print(line_pair)

    ## Do bi-directional check of intersection
    if check_one(line1, line2) and check_one(line2, line1):
        return([intersect])
    else:
        return([])

## done = False
## for i,wire_i in enumerate(wire_line_test[0]):
##     for j, wire_j in enumerate(wire_line_test[1]):
##         intersect = get_intersect(wire_i, wire_j)
##         if intersect:
##             print("Successful intersect for test set")
##             print(intersect)
##             done = True
##             break
##     if done:
##         break


# First, collect all intersections
all_intersects = []
min_dist = []
sum_dist = []
for i, wire_i in enumerate(wire_line[0]):
    for j, wire_j in enumerate(wire_line[1]):
        this_intersect = get_intersect(wire_i, wire_j)
        all_intersects += this_intersect
        if this_intersect:
            this_intersect = this_intersect[0]
            # x[1] is the line distance
            dist_base_i = sum([abs(x[2][0] - x[2][1]) for x in wire_line[0][0:i]])
            dist_base_j = sum([abs(x[2][0] - x[2][1]) for x in wire_line[1][0:j]])
            final_i = abs(wire_i[2][0] - this_intersect[wire_i[0]])
            final_j = abs(wire_j[2][0] - this_intersect[wire_j[0]])
            dist_i = dist_base_i + final_i
            dist_j = dist_base_j + final_j
            min_dist.append(min(dist_i, dist_j))
            sum_dist.append(dist_i + dist_j)

# print(len(all_intersects))
# print(all_intersects[0:5])
print(wire_line[0][1:5])
print("min_dist", min_dist[1:5])
print("sum_dist", sum_dist[1:5])

print(min(min_dist))
print(min(sum_dist))

