fuel_total = 0
with open("day1.in") as f:
    for l in f:
        this_fuel = int(l) // int(3) - 2
        fuel_total += this_fuel

print(fuel_total)
