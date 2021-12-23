from typing import re

from pyomo.environ import *
from pyomo.environ import SolverFactory


def DemandRule(model, c):
    return (sum(model.Transport[p, c] for p in model.Plants) >= model.Demand[c])


def CapacityRule(model, p):
    return (sum(model.Transport[p, c] for c in model.Customers) >= model.Capacity[p])


def MinCost(model):
    return sum(model.Transport[p, c] * model.UnitaryCost[p, c] for p in model.Plants for c in model.Customers)


def create_model(Plants, Customers, Capacity, Demand, UnitaryCost):
    # del model
    model = AbstractModel()
    model.Plants = Set(initialize=Plants)
    model.Customers = Set(initialize=Customers)
    model.Capacity = Param(model.Plants, initialize=Capacity)
    model.Demand = Param(model.Customers, initialize=Demand)
    model.UnitaryCost = Param(model.Plants, model.Customers, initialize=UnitaryCost)
    model.Transport = Var(model.Plants, model.Customers, within=NonNegativeReals)

    model.cDemanda = Constraint(model.Customers, rule=DemandRule)
    model.cCapacity = Constraint(model.Plants, rule=CapacityRule)
    model.Obj = Objective(rule=MinCost, sense=minimize)
    return model


def CreateInstance(model):
    instance = model.create_instance()
    return instance


def SolveInstance(instance):
    opt = SolverFactory("cbc")
    results = opt.solve(instance)
    results.write()
    instance.Transport.display()
    print("Total cost %s" % value(instance.Obj.expr()))
    print(instance.Obj)
    for s in [(p1, c1) for p1 in instance.Plants for c1 in instance.Customers]:
        print("%i trucks from %s to %s" % (instance.Transport[s[0], s[1]].value, s[0], s[1]))
    return instance

# instance.pprint()
