from collections import defaultdict, UserDict
from functools import reduce
import math

class ReactionDict(dict):
    def __init__(self, dict_in):
        super().__init__(dict_in)

    def __missing__(self, key):
        return 0

    def __add__(self, other_rxn):
        return_dict = ReactionDict(self.copy())
        for k,v in other_rxn.items():
            my_v = return_dict.__getitem__(k)
            return_dict.__setitem__(k, my_v + v)
        return return_dict
    
    def __sub__(self, other_rxn):
        return_dict = ReactionDict(self.copy())
        for k,v in other_rxn.items():
            my_v = return_dict.__getitem__(k)
            return_dict.__setitem__(k, my_v - v)
        return return_dict

    def __mul__(self, n):
        if not isinstance(n, int):
            raise TypeError("Can only multiply reaction by integer")
        if n < 0:
            raise ValueError("Must multiply reaction by positive value")
        return ReactionDict({k:v*n for k,v in self.items()})

    def get_reagents(self):
        return [k for k,v in self.items() if v > 0]

    def get_products(self):
        return [k for k,v in self.items() if v < 0]

    def get_pure_product_count(self):
        pr = self.get_products()
        if len(pr) != 1:
            raise ValueError("Equation requesting get_pure_product_count is not a pure reaction")
        return abs(self.__getitem__(pr[0]))


def vars_from_term(term):
    n, elem = term.strip().split(' ')
    n = int(n)
    return {elem:n}

def parse_reactions(s_reactions):
    reactions = {}
    for eq in s_reactions:
        lhs, rhs = eq.split('=>')
        lhs, rhs = [[vars_from_term(term) for term in side.strip().split(',')] for side in (lhs, rhs)]
        lhs, rhs = [reduce(lambda a,b: {**a, **b}, side) for side in (lhs, rhs)]
        product = next(iter(rhs.keys()))
        rhs = {k:-v for k,v in rhs.items()}
        reactions.update({product:ReactionDict({**lhs, **rhs})})
    return(reactions)



def simplify_to_ore(pure_reaction_dict, composite_rxn):
    while composite_rxn.get_reagents() != ['ORE']:
        ## Add new products to override missing reagents
        for new_product in composite_rxn.get_reagents():
            # For base reagents, e.g. ORE
            if new_product not in pure_reaction_dict:
                continue
            new_reaction = pure_reaction_dict[new_product]
            n_needed   = composite_rxn[new_product]
            n_product  = new_reaction.get_pure_product_count()
            n_reaction = n_needed // n_product + (0 if n_needed % n_product == 0 else 1)
            composite_rxn += new_reaction * n_reaction
    return(composite_rxn)


# Now undo some reactions
def clear_excess_product(pure_reaction_dict, composite_rxn, excess_product):
    # For base reagents, e.g. ORE
    if excess_product not in pure_reaction_dict:
        return(composite_rxn)
    excess_reaction = pure_reaction_dict[excess_product]
    n_excess        = abs(composite_rxn[excess_product])
    n_product       = excess_reaction.get_pure_product_count()
    n_reaction      = n_excess // n_product
    composite_rxn  -= excess_reaction * n_reaction
    composite_rxn   = simplify_to_ore(pure_reaction_dict, composite_rxn)
    return(composite_rxn)

if __name__ == "__main__":
    with open('day14.in') as f:
        s_reactions = [l.strip() for l in f.readlines()]
    pure_reaction_dict = parse_reactions(s_reactions)
    
    ore_per_fuel = simplify_to_ore(pure_reaction_dict, pure_reaction_dict['FUEL'])['ORE']
    print(f"Ore for a single fuel: {ore_per_fuel}")
    
    guesstimate = int(1E12 // ore_per_fuel) 
    max_n_fuel = 0
    upper_bound = guesstimate 
    lower_bound = guesstimate * 10
    while (abs(upper_bound - lower_bound) > 10):
        n_fuel = int((upper_bound + lower_bound) / 2)
        fuel_cost = simplify_to_ore(pure_reaction_dict, pure_reaction_dict['FUEL'] * n_fuel)['ORE'] 
        if fuel_cost <= 1E12:
            upper_bound = n_fuel
            max_n_fuel = max(n_fuel, max_n_fuel)
        else:
            lower_bound = n_fuel
    
    for n_fuel in range(max_n_fuel - 100, max_n_fuel + 100):
        full_reaction = simplify_to_ore(pure_reaction_dict, pure_reaction_dict['FUEL'] * n_fuel)
        fuel_cost = full_reaction['ORE']
        if fuel_cost <= 1E12:
            max_n_fuel = n_fuel
    
    print(f"Max fuel produced: {max_n_fuel}")
    
    
    
