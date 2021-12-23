from pyomo.environ import SolverFactory, value
from model import get_transport_model
from input_data import InputData
from output_data import export_data
# from check_solution import SolutionChecker
# from compare_output import compare_output, get_kpi
# from const import FIXED_TRAINS, SOLVER_PARAMETERS, FIXED_PEOPLE_IN, C22_VERSION
# from model_iterator import ModelIterator
# from pyomo_utils import is_feasible
# from project_utils import set_c22_version, fix_solution

# Get model
model = get_transport_model()

# selected_trains = [i for i in range(1, 74)]

# Create instance
input_data = InputData()
input_data.read_inputs_xlsx("data/input/input_data_transport.xlsx")
data = input_data.get_transport_model_data()

# Creating the model instance
instance1 = model.create_instance(data, report_timing=True)
# set_c22_version(instance1, C22_VERSION)
# #fix_solution(instance1, input_data, FIXED_TRAINS, FIXED_PEOPLE_IN)
#
# # instance1.pprint()
# # Write instance.display() in a file
# with open("../data/checks/instance_pprint.txt", "w") as f:
#     instance1.pprint(ostream=f)
#
# Solve instance
opt = SolverFactory('gurobi')
# opt.options.update(SOLVER_PARAMETERS)
result = opt.solve(instance1, tee=True)
instance1.display()
output_data = export_data(instance1)

# if not is_feasible(iterator.status):
#     raise Exception("Problem infeasible !!!")
#
#
# # Write instance.display() in a file
# with open("../data/checks/instance_display.txt", "w") as f:
#     iterator.instance.display(ostream=f)
#
# result1 = {(i, j): value(iterator.instance.v01TrainStop[i, j]) for (i, j) in iterator.instance.sTrains_Stations}
# list_stops = {i: [j for j in iterator.instance.sStations if (i, j) in result1 and result1[i, j] > 0] for i in
#               iterator.instance.sTrains}
#
# for i in list_stops.keys():
#     print("Train %s stop in station %s" % (i, list_stops[i]))
#

#
# check = SolutionChecker(iterator.instance)
# check.check_all()
#
# check.to_excel("../data/checks/check_errors.xlsx")
#
# compare_data = compare_output(input_data.stop_times_raw, output_data)
# kpi_data = get_kpi(compare_data)
