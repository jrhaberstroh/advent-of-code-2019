import numpy as np


class BugMapRec:
    def __init__(self, map_string, max_steps = None):
        if max_steps is None:
            self.num_layers = 1
            self.center = 0
        else:
            self.num_layers = (max_steps // 2 + 2) * 2 + 1
            self.center = self.num_layers // 2
        self.bugmap = self.__get_empty_array()
        self.upmap  = self.__get_empty_array()

        self.mapper = {'#':1, '.':0}
        self.unmapper = {v:k for k,v in self.mapper.items()}
        start_layer = np.array([
            [self.mapper[s] for s in row] 
            for row in map_string.strip().split('\n')
        ])
        self.bugmap[self.center, :, :] = start_layer[:, :]
        print(self.bugmap[self.center, :, :])

    def __get_empty_array(self):
        return np.zeros((self.num_layers, 5, 5), dtype = int)

    def rot90(self):
        self.bugmap = np.rot90(self.bugmap, axes = (1,2))
        self.upmap  = np.rot90(self.upmap, axes = (1,2))

    def update_layer(self):
        self.upmap[:, :-1, :] += self.bugmap[:, 1:, :]

    def update_recursion_up(self):
        self.upmap[:-1, 1, 2] += self.bugmap[1:, 0, :].sum(axis = 1)

    def update_recursion_down(self):
        self.upmap[1:, 0, :]  += self.bugmap[:-1, 1, 2][:, np.newaxis]

    def clear_centers(self):
        self.upmap[:, 2, 2] = 0
    
    def reset_updater(self):
        self.upmap[:,:,:] = 0

    def new_bugs(self):
        self.bugmap = (((np.equal(self.bugmap, 1) * np.equal(self.upmap, 1)) +
                        (np.equal(self.bugmap, 0) * np.equal(self.upmap, 1)) +
                        (np.equal(self.bugmap, 0) * np.equal(self.upmap, 2)) )
                        .astype(bool).astype(int))

    def step_nonrec(self):
        for _ in range(4):
            self.update_layer()
            self.rot90()
        self.new_bugs()
        self.reset_updater()

    def step_rec(self):
        if self.bugmap[0, :, :].sum() > 0 or self.bugmap[-1, :, :].sum() > 0:
            raise IndexError("Reached max level of grid recursion")

        self.reset_updater()
        for _ in range(4):
            self.update_layer()
            self.update_recursion_up()
            self.update_recursion_down()
            self.rot90()
        self.clear_centers()
        self.new_bugs()

    def print_layers(self, layers):
        these_layers = self.bugmap[tuple(int(l + self.center) for l in layers), :, :]
        print("\n".join([ "   ".join([" ".join([self.unmapper[x] for x in row_layer]) for row_layer in these_layers[:, row, :]])
            for row in range(these_layers.shape[1])
        ]))
        print("\n")

    def print_upmap_layers(self, layers):
        these_layers = self.upmap[tuple(int(l + self.center) for l in layers), :, :]
        print("\n".join([ "   ".join([" ".join([str(x) for x in row_layer]) for row_layer in these_layers[:, row, :]])
            for row in range(these_layers.shape[1])
        ]))
        print("\n")

    def get_occupied_layers(self):
        return [ix - self.center 
                for ix, n_in_layer in enumerate(self.bugmap.sum(axis = (1,2)))
                if n_in_layer > 0]

    def serialize(self):
        return(tuple(self.bugmap.flatten()))



# ---------- PART 1 -------------
def part1(inputs):
    bugmap = BugMapRec(inputs) 
    
    known_maps = {bugmap.serialize():0}
    for i in range(1000):
        bugmap.step_nonrec()
        serial_map = bugmap.serialize()
        if serial_map in known_maps:
            break
        else:
            known_maps[serial_map] = i
    
    print(sum([2**(i) * v  for i,v in enumerate(bugmap.serialize())]))


# ---------- PART 2 -------------
def part2(inputs):
    bugmap = BugMapRec(inputs, 200) 
    
    known_maps = {bugmap.serialize():0}
    for i in range(200):
        bugmap.step_rec()
        bugmap.print_layers(tuple(range(-4, 5)))
        serial_map = bugmap.serialize()
        if serial_map in known_maps:
            break
        else:
            known_maps[serial_map] = i
    
    bugmap.print_layers(tuple(range(-1, 2)))
    print(bugmap.bugmap.sum())

    
    ## print(sum([2**(i) * v  for i,v in enumerate(bugmap.serialize())]))


inputs = """
..#..
##..#
##...
#####
.#.##
""".strip()


# ----------- MAIN ------------
if __name__ == "__main__":
    # part1(inputs)

    part2(inputs)



## def step_rec(bugmap):
##     if len(bugmap.shape) == 2:
##         raise IndexError("")
##     z = bugmap.shape[0]
##     x = bugmap.shape[1]
##     y = bugmap.shape[2]
##     newmap = np.zeros((z, x, y))
##     for _ in range(4):
##         newmap[:,  :-1,  :  ] += bugmap[:, 1:  ,  :  ]
##         newmap.rot90(axes = (1,2))
##         newmap.rot90(axes = (1,2))
## 
## 
## 
##     newmap[:, 1:  ,  :  ] += bugmap[:,  :-1,  :  ]
##     newmap[:,  :  ,  :-1] += bugmap[:,  :  , 1:  ]
##     newmap[:,  :  , 1:  ] += bugmap[:,  :  ,  :-1]
## 
##     newmap[[
## 
##     return ((np.equal(bugmap, 1) * np.equal(newmap, 1)) +
##             (np.equal(bugmap, 0) * np.equal(newmap, 1)) +
##             (np.equal(bugmap, 0) * np.equal(newmap, 2)) ).astype(bool).astype(int)



