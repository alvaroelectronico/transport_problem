from typing import re
from lectura_excel_transport import leerExcel
#Importing pyomo
from pyomo.environ import*
from pyomo.environ import SolverFactory

#Reading input info
Plants, Customers, Capacity, Demand, UnitaryCost = leerExcel("datos_entrada.xlsx")

# Creating funtions for constraints and objective
def DemandRule (model, c):
    return (sum(model.Transport[p, c] for p in model.Plants) >= model.Demand[c])
def CapacityRule (model, p):
    return (sum(model.Transport[p, c] for c in model.Customers) >= model.Capacity[p])
def MinCost (model):
    return sum(model.Transport[p,c]*model.UnitaryCost[p,c] for p in model.Plants for c in model.Customers)


#Defining sets, parameters and variable.s
model = AbstractModel()
model.Plants = Set(initialize=Plants)
model.Customers = Set(initialize=Customers)
model.Capacity = Param(model.Plants, initialize=Capacity)
model.Demand = Param(model.Customers, initialize=Demand)
model.UnitaryCost = Param(model.Plants, model.Customers, initialize=UnitaryCost)
model.Transport = Var(model.Plants, model.Customers, within=NonNegativeReals)
# Building the model
model.cDemanda = Constraint(model.Customers, rule = DemandRule)
model.cCapacity = Constraint(model.Plants, rule = CapacityRule)
model.Obj = Objective(rule=MinCost, sense=minimize)


# Creating the instance
instance = model.create_instance()

# Solving the instance
opt = SolverFactory("gurobi")
results = opt.solve(instance)
# Displyaing results
results.write()
instance.Transport.display()
print("Total cost %s" % value(instance.Obj.expr()))
print(instance.Obj)
for s in [(p1, c1) for p1 in instance.Plants for c1 in instance.Customers]:
    print("%i trucks from %s to %s" % (instance.Transport[s[0], s[1]].value, s[0], s[1]))

