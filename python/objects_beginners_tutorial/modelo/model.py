"""
Optimization model to assign train stops
"""

from pyomo.environ import *


# This function creates the pyomo transport abstract model and return a pyomo abstract model

def get_transport_model():
    # Create model
    m = AbstractModel()

    # Model sets
    m.sPlants = Set()
    m.sCustomers = Set()

    # Model parameters
    m.pDemand = Param(m.sCustomers, mutable=True)
    m.pSupply = Param(m.sPlants, mutable=True)
    m.pUnitTransportCost = Param(m.sPlants, m.sCustomers, mutable=True)

    # # Model variables
    m.vTransport = Var(m.sPlants, m.sCustomers, within=NonNegativeReals)
    m.vTotalCost = Var(within=NonNegativeReals)

    # Constraints
    # Defining supply constraint rule
    def fcSupply(model, p):
        return sum(model.vTransport[p, c] for c in model.sCustomers) <= \
               model.pSupply[p]

    # Defining demand constraint rule
    def fcDemand(model, c):
        return sum(model.vTransport[p, c] for p in model.sPlants) >= \
               model.pDemand[c]

    # Defining total cost rule
    def fvTotalCost(model):
        return model.vTotalCost == sum(model.vTransport[p, c] * model.pUnitTransportCost[p, c]
                                       for p in model.sPlants
                                       for c in model.sCustomers)

    # Objective function: min. total cost
    def obj_expression(model):
        return model.vTotalCost

    # Activating constraints
    m.cSupply = Constraint(m.sPlants, rule=fcSupply)
    m.cDemand = Constraint(m.sCustomers, rule=fcDemand)
    m.cTotalCost = Constraint(rule=fvTotalCost)

    # Creating model instance
    m.fObj = Objective(rule=obj_expression, sense=minimize)

    return m
