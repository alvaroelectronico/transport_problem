import time
import math
import pandas as pd
import xlrd


#from project_utils import format_date
#from const import STATIONS_NAMES, ADJUST_ARRIVALS, FIXED_PEOPLE_IN

class InputData:

    def __init__(self):
        """
        Class to prepare and store the input data.
        """
        self.transport_model_data = dict()
        self.plants = dict()
        self.customers = dict()
        self.costs = dict()
        # self.stations = {STATIONS_NAMES[k]: k for k in STATIONS_NAMES.keys()}
        # self.problem_parameters = dict()
        # self.fixed_stops = dict()
        # self.get_problem_parameters()
    
    
    #def read_inputs(self, stop_times_file, od_matrix_file, day, selected_trains=None):
    def read_inputs_xlsx(self, input_file):
        """
        Method to read the data files
        :param input_file: route to the input info
        :return:
        """
        wb = xlrd.open_workbook(input_file)
        sheet = wb.sheet_by_name("oferta")
        self.plants = {sheet.cell_value(r, 0): sheet.cell_value(r, 1)
                  for r in range(0, sheet.nrows)}

        sheet = wb.sheet_by_name("demanda")
        self.customers = {sheet.cell_value(r, 0): sheet.cell_value(r, 1)
                   for r in range(0, sheet.nrows)}

        sheet = wb.sheet_by_name("coste_transporte")
        self.costs = {(sheet.cell_value(r, 0), sheet.cell_value(r, 1)): sheet.cell_value(r, 2)
                         for r in range(0, sheet.nrows)}

        print("Input data read")

    def get_transport_model_data(self):
        plants = self.plants
        sPlants = [p for p in plants.keys()]  #set(plants["trainOrder"])
        customers = self.customers
        sCustomers = [c for c in customers.keys()]
        costs = self.costs

        self.transport_model_data.update({'sPlants': {None: sPlants}})
        self.transport_model_data.update({'sCustomers': {None: sCustomers}})
        self.transport_model_data.update({'pSupply': plants})
        self.transport_model_data.update({'pDemand': customers})
        self.transport_model_data.update({'pUnitTransportCost': costs})

        return {None: self.transport_model_data}

    # def get_problem_parameters(self):
    #     # number of consecutive trains to evaluate the number of trains which stop in a station
    #     self.problem_parameters['pNumConsecutiveTrains'] = {None: 3}
    #     # minimum number of stops between consecutive trains. pMinimumNumStopsBetweenConsecutiveTrains <=
    #     # pNumConsecutiveTrains
    #     self.problem_parameters['pMinimumNumStopsBetweenConsecutiveTrains'] = {None: 1}

    def read_inputs_csv(self, input_file):
        # self.stop_times_raw = pd.read_csv(stop_times_file).fillna(0)
        # od_matrix_raw = pd.read_csv(od_matrix_file)
        #
        # if selected_trains is not None:
        #     self.stop_times_raw = self.stop_times_raw[self.stop_times_raw.trainOrder.isin(selected_trains)]
        #     od_matrix_raw = od_matrix_raw[od_matrix_raw.trainOrder.isin(selected_trains)]
        #
        # self.stop_times = self.stop_times_raw.loc[self.stop_times_raw.snapshot == day, :].copy()
        #
        # # Filter the original data frame to the set day in order to
        # self.stop_times_raw = self.stop_times_raw[self.stop_times_raw.snapshot == day]
        #
        # self.stop_times.loc[:, "departureTime"] = self.stop_times.loc[:, "departureTime"].apply(format_date)
        # self.stop_times.loc[:, "arrivalTime"] = self.stop_times.loc[:, "arrivalTime"].apply(format_date)
        #
        # self.stop_times["station"] = [self.stations[i] for i in self.stop_times.loc[:, "stop"]]
        # self.od_matrix = od_matrix_raw.loc[od_matrix_raw.snapshot == day, :].copy()
        # self.od_matrix["stationIn"] = [self.stations[i] for i in self.od_matrix.loc[:, "stopIn"]]
        # self.od_matrix["stationOut"] = [self.stations[i] for i in self.od_matrix.loc[:, "stopOut"]]
        #
        # self.stop_times = self.stop_times.to_dict(orient="list")
        # self.od_matrix = self.od_matrix.to_dict(orient="list")

        print("Input data read")

