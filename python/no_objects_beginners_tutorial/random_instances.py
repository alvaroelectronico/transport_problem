import numpy as np

def generate_random_instance(no_plants=3, no_customers=5):

    total_capacity = 1000

    Plants = ["Planta{}".format(p) for p in range(1, no_plants+1)]
    Customers = ["Cliente{}".format(c) for c in range(1, no_customers+1)]

    avg_capacity = total_capacity/no_plants
    avg_demand = 0.9*total_capacity/no_customers

    Capacity = {p: np.round((0.8+0.4*np.random.random())*avg_capacity,0) for p in Plants}
    Demand = {c: np.round((0.9+0.2*np.random.random())*avg_demand, 0) for c in Customers}

    total_demand = sum(Demand[c] for c in Customers)
    total_capacity = sum(Capacity[p] for p in Plants)

    while total_demand>total_capacity:
        gap = total_demand - total_capacity
        cap_increase = np.ceil(gap/no_plants)
        Capacity = {p: Capacity[p] + cap_increase for p in Plants}
        total_demand = sum(Demand[c] for c in Customers)
        total_capacity = sum(Capacity[p] for p in Plants)

    min_cost = 10
    max_cost = 60
    UnitaryCost = {(p, c): np.round(np.random.uniform(min_cost, max_cost)) for p in Plants for c in Customers}

    return Plants, Customers, Capacity, Demand, UnitaryCost