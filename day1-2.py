def fuel_recursion(l):
    fuel_req = int(l) // int(3) - 2
    if fuel_req <= 0:
        return(0)
    else:
        return(fuel_req + fuel_recursion(fuel_req))

fuel_total = 0
with open("day1.in") as f:
    for l in f:
        this_fuel = fuel_recursion(int(l))
        fuel_total += this_fuel

print(fuel_total)
