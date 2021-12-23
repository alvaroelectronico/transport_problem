
import pandas as pd
import warnings

from pyomo_utils import var_to_dict
from pyomo.environ import *
from const import FIXED_PEOPLE_IN


class SolutionChecker:
    
    def __init__(self, instance, precision=0.01, proportion_precision =0.1):
        
        self.precision = precision
        self.proportion_precision = proportion_precision
        self.instance = instance
        self.no_stops = {}
        self.inconsistent_stops = {}
        self.bad_frequency = {}
        self.train_problem = []

        self.passengers_on_no_stop = {}
        self.passengers_off_no_stop = {}
        self.passengers_on_wrong = {}
        self.passengers_off_wrong = {}
        self.too_many_passengers_on = {}
        self.passengers_left = {}
        self.platform_balance = {}
        self.platform_limit = {}
        self.proportion_problem = {}
        self.train_passengers_problem = []
        self.platform_balance_problem = []
        self.any_problem = {}

        self.linear_proportion_problem= {}
        
    def check_train_consistency(self):
        instance = self.instance
        freq = value(instance.pNumConsecutiveTrains)
        v01TrainStop = var_to_dict(instance.v01TrainStop)
        sTrains = instance.sTrains
        sTrains_Stations = instance.sTrains_Stations
        sStations = set([s for t, s in sTrains_Stations])
        sStation_precedences = [(s1, s2) for s1 in sStations for s2 in sStations if s2 > s1]
        
        for t in instance.sTrains:
            self.no_stops[t] = (sum(v01TrainStop[t1, s] for (t1, s) in sTrains_Stations if t == t1) == 0)
            self.inconsistent_stops[t] = any(v01TrainStop[t, s1] > v01TrainStop[t, s2]
                                             for (s1, s2) in sStation_precedences)
            if t <= freq:
                self.bad_frequency[t] = False
            else:
                self.bad_frequency[t] =\
                    any(sum(v01TrainStop[t1, s] for t1 in range(t-freq,t+1)) == 0 for s in sStations)
                
        self.train_problem = [t for t in sTrains
                              if self.no_stops[t] or self.inconsistent_stops[t] or self.bad_frequency[t]]
        print("Problems with train stops consistency: " % self.train_problem)
    
    def check_train_passenger_balance(self):
        p = self.precision
        instance = self.instance
        v01TrainStop = var_to_dict(instance.v01TrainStop)
        vPassengersGettingOnTrain = var_to_dict(instance.vPassengersGettingOnTrain)
        vPassengersGettingOffTrain = var_to_dict(instance.vPassengersGettingOffTrain)
        vPassengersInTrain = var_to_dict(instance.vPassengersInTrain)
        vPassengersWaitingInStation = var_to_dict(instance.vPassengersWaitingInStation)
        pPassengersArrivingAtStationPerDestination = var_to_dict(instance.pPassengersArrivingAtStationPerDestination)
        pMaximumTrainCapacity = value(instance.pMaximumTrainCapacity)
        sTrains_Stations = instance.sTrains_Stations
        sStations = instance.sStations
        
        for (t, s) in sTrains_Stations:
            # 2.1 Are there passengers getting on train in a station where the train doesn't stop ?
            self.passengers_on_no_stop[t, s] = (sum(vPassengersGettingOnTrain[t, s, s1]
                                                    for s1 in sStations if s1 > s) > p and v01TrainStop[t, s] == 0)
            # 2.2 Are there passengers getting off train in a station where the train doesn't stop ?
            self.passengers_off_no_stop[t, s] = (vPassengersGettingOffTrain[t, s] > 0 and v01TrainStop[t, s] == 0)
            # 2.3 Is there a difference between the number of passengers getting off train and the passenger in the train
            # with this destination ?
            if s > 1:
                self.passengers_off_wrong[t, s] = (abs(vPassengersGettingOffTrain[t, s] - vPassengersInTrain[t, s-1, s]) > p)
            else:
                self.passengers_off_wrong[t, s] = False
            # 2.4 Is there a difference between the number of passengers getting on train and the passenger in the train
            # from the same station ?
            self.passengers_on_wrong[t, s] = any(abs(sum(vPassengersGettingOnTrain[t, s1, s2] for s1 in sStations if s1 <= s) -
                                                     vPassengersInTrain[t, s, s2]) > p for s2 in sStations if s2 > s)
            # 2.5 Are there more passengers getting on train than the one who where on the platform ?
            if t > 1:
                self.too_many_passengers_on[t, s] = any(vPassengersGettingOnTrain[t, s, s1] -
                    vPassengersWaitingInStation[t-1, s, s1] - pPassengersArrivingAtStationPerDestination[t, s, s1]
                                                        > self.precision for s1 in sStations if s1 > s)
            else:
                self.too_many_passengers_on[t, s] = any(vPassengersGettingOnTrain[t, s, s1] -
                    pPassengersArrivingAtStationPerDestination[t, s, s1] > self.precision for s1 in sStations if s1 > s)
            # 2.6 Are there passengers left in the platform when the train still have capacity ?
            self.passengers_left[t,s] = (v01TrainStop[t, s] > 0 and
                    sum(vPassengersWaitingInStation[t, s, s1] for s1 in sStations if s1 > s) > p and
                    sum(vPassengersInTrain[t, s, s1] for s1 in sStations if s1 > s) < pMaximumTrainCapacity)
                  
        self.train_passengers_problem = [(t,s) for (t, s) in sTrains_Stations
                              if self.passengers_on_no_stop[t, s] or
                                         self.passengers_off_no_stop[t, s] or
                                         self.passengers_off_wrong[t, s] or
                                         self.passengers_on_wrong[t, s] or
                                         self.too_many_passengers_on[t, s]
                                         ]
        print("Problems with passenger balance on train with the following indices: %s"
              % self.train_passengers_problem)
    
    def check_waiting_passengers_balance(self):
        instance = self.instance
        p = self.precision
        p2 = self.proportion_precision
        sTrain = instance.sTrains
        sTrains_Stations = instance.sTrains_Stations
        sStations = instance.sStations

        v01TrainStop = var_to_dict(instance.v01TrainStop)
        vPassengersGettingOnTrain = var_to_dict(instance.vPassengersGettingOnTrain)
        vPassengersWaitingInStation = var_to_dict(instance.vPassengersWaitingInStation)
        pPassengersArrivingAtStation = var_to_dict(instance.pPassengersArrivingAtStation)
        pPassengersArrivingAtStationPerDestination = var_to_dict(instance.pPassengersArrivingAtStationPerDestination)
        pMaximumNumPassengersWaitingInStation = var_to_dict(instance.pMaximumNumPassengersWaitingInStation)
        
        self.proportion_station = {(t, s1, s2): vPassengersWaitingInStation[t, s1, s2] /
                              max(self.precision, sum(vPassengersWaitingInStation[t, s1, s3] for s3 in sStations if s3 > s1))
                              for t, s1, s2 in vPassengersWaitingInStation.keys()}
        self.proportion_train = {(t, s1, s2): vPassengersGettingOnTrain[t, s1, s2] /
                            max(self.precision, sum(vPassengersGettingOnTrain[t, s1, s3] for s3 in sStations if s3 > s1))
                            for t, s1, s2 in vPassengersGettingOnTrain.keys()}
        
        self.proportion_parameter = {(t, s1, s2): sum(pPassengersArrivingAtStationPerDestination[t2, s1, s2]
                                                      for t2 in sTrain if t2 <= t) /
                                     sum(pPassengersArrivingAtStation[t2, s1] for t2 in sTrain if t2 <= t)
                                     for t, s1, s2 in pPassengersArrivingAtStationPerDestination.keys()}
        
        self.absolute_error = {(t, s1, s2): (self.proportion_station[t, s1, s2] - self.proportion_train[t, s1, s2]) *
            (pPassengersArrivingAtStationPerDestination[t, s1, s2] + vPassengersWaitingInStation[t-1, s1, s2])
        if t > 1 else (self.proportion_station[t, s1, s2] - self.proportion_train[t, s1, s2]) *
                      pPassengersArrivingAtStationPerDestination[t, s1, s2]
                               for t, s1, s2 in vPassengersWaitingInStation.keys()}

        self.absolute_error = {(t, s1, s2):self.absolute_error[t, s1, s2] if self.proportion_station[t, s1, s2] and
            v01TrainStop[t, s1] else 0 for t, s1, s2 in self.absolute_error.keys()}
        
        for (t,s) in sTrains_Stations:
            # 3.1 Is the balance between passengers on platform and passengers getting on train right?
            if t > 1:
                self.platform_balance[t, s] = any(
                    abs(vPassengersGettingOnTrain[t, s, s1] + vPassengersWaitingInStation[t, s, s1] -
                        pPassengersArrivingAtStationPerDestination[t, s, s1] - vPassengersWaitingInStation[t-1, s, s1])
                    > p for s1 in sStations if s1 > s)
            else:
                self.platform_balance[t, s] = any(
                    abs(vPassengersGettingOnTrain[t, s, s1] + vPassengersWaitingInStation[t, s, s1] -
                        pPassengersArrivingAtStationPerDestination[t, s, s1]) > p for s1 in sStations if s1 > s)
            # 3.2 Is the platform occupation limit respected ?
            self.platform_limit[t, s] = (sum(vPassengersWaitingInStation[t, s, s1] for s1 in sStations if s1 > s) >
                                        pMaximumNumPassengersWaitingInStation[s])
            # 3.3 Do people getting on train and people staying in the platform have the same proportions
            # going to every station? 
            self.proportion_problem[t, s] = any(abs(self.proportion_station[t, s, s1] -
                self.proportion_train[t, s, s1]) > p2 for s1 in sStations if s1 > s) \
                and sum(self.proportion_station[t, s, s1] for s1 in sStations if s1 > s) > 0 \
                and v01TrainStop[t,s] > 0
            
            # 3.4 Is the linear approximation of proportions respected ?
            self.linear_proportion_problem[t, s] = any(abs(self.proportion_station[t, s, s1] -
                self.proportion_parameter[t, s, s1]) > p2 for s1 in sStations if s1 > s) \
                and sum(self.proportion_station[t, s, s1] for s1 in sStations if s1 > s) > 0 \
                and v01TrainStop[t,s] > 0
            
        self.platform_balance_problem = [(t, s) for (t, s) in sTrains_Stations if self.platform_balance[t, s]
                                         or self.platform_limit[t, s]
                                         or self.proportion_problem[t, s]
                                         #or self.linear_proportion_problem[t, s]
                                         ]
        print("Problems with passenger balance on platform with the following indices: %s"
              % self.platform_balance_problem)

    def check_OF(self):
        pass
    
    def check_all(self):
        self.check_train_consistency()
        self.check_train_passenger_balance()
        self.check_waiting_passengers_balance()
        self.check_OF()
        
        self.any_problem = {(t,s):((t, s) in self.train_problem
                                   or (t, s) in self.train_passengers_problem
                                   or (t,s) in self.platform_balance_problem)
                            for (t, s) in self.instance.sTrains_Stations}
        
        if any(i for i in self.any_problem.values()):
            problem_indices = [k for k in self.any_problem.keys() if self.any_problem[k]]
            warnings.warn("Problem found with the following trains and stations: %s \\n Check the file in data/checks"
                          % problem_indices)
        
        
    def to_excel(self, file):
        instance = self.instance
        vPassengersWaitingInStation = var_to_dict(instance.vPassengersWaitingInStation)
        passengers_waiting = {(t, s1, s2): vPassengersWaitingInStation[t-1, s1, s2] if t > 1 else 0
                                    for t, s1, s2 in vPassengersWaitingInStation.keys()}
        
        table = {}
        
        self.add_column(table, [k for k in instance.vPassengersGettingOnTrain.keys()], "(t, s1, s2)")
        self.add_column(table, [(t, s1) for (t,s1,s2) in instance.vPassengersGettingOnTrain.keys()], "(t, s)")
        
        self.add_filter_column(table, self.any_problem, "e0: any error", "(t, s)")
        self.add_filter_column(table, self.no_stops, "e1.1: 0 stop", "(t, s)")
        self.add_filter_column(table, self.inconsistent_stops,"e1.2: stop rule",  "(t, s)")
        self.add_filter_column(table, self.bad_frequency, "e1.3: frequency", "(t, s)")
        self.add_filter_column(table, self.passengers_on_no_stop, "e2.1: passengers on, no stop", "(t, s)")
        self.add_filter_column(table, self.passengers_off_no_stop, "e2.2: passengers off, no stop", "(t, s)")
        self.add_filter_column(table, self.passengers_on_wrong, "e2.3: passengers on", "(t, s)")
        self.add_filter_column(table, self.passengers_off_wrong, "e2.4: passengers off", "(t, s)")
        self.add_filter_column(table, self.too_many_passengers_on, "e2.5: too many passengers on", "(t, s)")
        #self.add_filter_column(table, self.passengers_left, "e2.6: passengers on platform", "(t, s)")
        self.add_filter_column(table, self.platform_balance, "e3.1: platform balance", "(t, s)")
        self.add_filter_column(table, self.platform_limit, "e3.2: platform limit", "(t, s)")
        self.add_filter_column(table, self.proportion_problem, "e3.3 proportions", "(t, s)")
        #self.add_filter_column(table, self.linear_proportion_problem, "e3.4: model proportions", "(t, s)")
        
        self.add_var_column(table, instance.v01TrainStop, "v01TrainStop", "(t, s)")
        self.add_var_column(table, instance.pPassengersArrivingAtStation, "pPassengersArrivingAtStation", "(t, s)")
        self.add_var_column(table, passengers_waiting, "Passengers on platform", "(t, s1, s2)")
        self.add_var_column(table, instance.pPassengersArrivingAtStationPerDestination,
                            "pPassengersArrivingAtStationPerDestination", "(t, s1, s2)")
        self.add_var_column(table, instance.vPassengersGettingOnTrain, "vPassengersGettingOnTrain", "(t, s1, s2)")
        self.add_var_column(table, self.proportion_station, "Proportions in station", "(t, s1, s2)")
        self.add_var_column(table, self.proportion_train, "Proportions in train", "(t, s1, s2)")
        self.add_var_column(table, self.proportion_parameter, "Proportions parameter", "(t, s1, s2)")
        self.add_var_column(table, self.absolute_error, "Absolute difference", "(t, s1, s2)")
        self.add_var_column(table, instance.vPassengersGettingOffTrain, "vPassengersGettingOffTrain", "(t, s)")
        self.add_var_column(table, instance.vPassengersInTrain, "vPassengersInTrain", "(t, s1, s2)")
        self.add_var_column(table, instance.vPassengersWaitingInStation, "vPassengersWaitingInStation", "(t, s1, s2)")
        if not FIXED_PEOPLE_IN:
            self.add_var_column(table, instance.v01OccupancyTrainDepartureModel_1,
                                "v01OccupancyTrainDepartureModel_1", "(t, s)")
            self.add_var_column(table, instance.v01OccupancyTrainDepartureModel_2,
                                "v01OccupancyTrainDepartureModel_2", "(t, s)")
            self.add_var_column(table, instance.v01OccupancyTrainDepartureModel_3,
                                "v01OccupancyTrainDepartureModel_3", "(t, s)")
            self.add_var_column(table, instance.v01HighTrainOccupancy, "v01HighTrainOccupancy", "(t, s)")
            self.add_var_column(table, instance.v01NoFullTrain_a, "v01NoFullTrain_a", "(t, s)")
            self.add_var_column(table, instance.v01NoFullTrain_b, "v01NoFullTrain_b", "(t, s)")
            self.add_var_column(table, instance.vSlack10a, "vSlack10a", "(t, s)")
            self.add_var_column(table, instance.vSlack10b, "vSlack10b", "(t, s)")
        self.add_var_column(table, instance.vDiscrepancyV1, "vDiscrepancyV1", "(t, s1, s2)")

        df = pd.DataFrame.from_dict(table)
        df.to_excel(file, **self.get_xl_options())
    
    @staticmethod
    def add_column(table, values, col_name):
        table[col_name] = values
    
    @staticmethod
    def add_var_column(table, variable, col_name, key=None):
        v = var_to_dict(variable)
        if key is None:
            table[col_name] = [i for i in v.values()]
        else:
            key_exist = [k for k in v.keys()]
            table[col_name] = [v[k] if k in key_exist else "" for k in table[key]]
    
    @staticmethod
    def add_filter_column(table, filter, col_name, key=None):
        if any(val for val in filter.values()):
            if key is None:
                table[col_name] = [i for i in filter.values()]
            else:
                key_exist = [k for k in filter.keys()]
                table[col_name] = [filter[k] if k in key_exist else "" for k in table[key]]

    @staticmethod
    def get_xl_options():
        return {
            "index":False
            
        }
    
        
    def write_summary(self):
        pass