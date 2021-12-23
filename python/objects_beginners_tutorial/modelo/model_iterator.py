from const import WARMSTART_FILE
from pyomo_utils import activate_constraint_list, deactivate_constraint_list, fix_variable_list, free_variable, \
    free_variable_list, write_cbc_warmstart_file


class ModelIterator:
    """

    """

    def __init__(self, instance, opt,
                 FIX_STOPS=False, stops_dict=None, FIX_PASSENGERS=False, passengers_dict=None, verbose=False):
        """

        :param instance: a pyomo instance of the model
        :param opt: the solver
        :param verbose: True to print the logs from the solver
        """
        self.status = ''
        self.instance = instance
        self.opt = opt
        self.FIX_STOPS = FIX_STOPS
        self.stops_dict = stops_dict
        self.FIX_PASSENGERS = FIX_PASSENGERS
        self.passengers_dict = passengers_dict
        self.verbose = verbose

        self.sTrains = [t for t in instance.sTrains]
        self.sStations = [s for s in instance.sStations]

        self.t_constraints_names = ["c17_one_or_more_stops_per_train"]

        self.t_s_constraints_names = ["c4_train_stops_after_first_stop",
                                      "c5_minimum_num_stops_between_consecutive_trains",
                                      "c6_passengers_getting_on_if_train_stops",
                                      "c7_maximum_num_passengers_waiting_per_station",
                                      "c8_passengers_getting_off_trains",
                                      "c24_total_passengers_getting_in_train"]

        self.t_s_1_constraints_names = ["c9a_occupancy_train_departure_model_1_range_1",
                                        "c9b_occupancy_train_departure_model_1_range_2",
                                        "c10a_occupancy_train_departure_model_1_value_1",
                                        "c10b_occupancy_train_departure_model_1_value_2",
                                        "c18_min_occupancy_train_departure_model_1",
                                        "c19a_max_value_vSlack10a",
                                        "c19b_max_value_vSlack10b",
                                        "c20_only_one_full_train_per_occupancy_model_1",
                                        "c21a_min_value_vSlack10a",
                                        "c21b_min_value_vSlack10b"]

        self.t_s_23_constraints_names = ["c11a_occupancy_train_departure_max_num_passengers",
                                         "c11b_occupancy_train_departure_min_num_passengers",
                                         "c12a_occupancy_train_departure_model_2_range_1",
                                         "c12b_occupancy_train_departure_model_2_range_2",
                                         "c13a_occupancy_train_departure_model_3_range_1",
                                         "c13b_occupancy_train_departure_model_3_range_2",
                                         "c15a_occupancy_train_departure_model_2_value_1",
                                         "c15b_occupancy_train_departure_model_2_value_2",
                                         "c16a_occupancy_train_departure_model_3_value_1",
                                         "c16b_occupancy_train_departure_model_3_value_2",
                                         ]

        self.t_s_s_constraints_names = ["c1_maximum_number_of_passengers_getting_on_train",
                                        "c2_passengers_in_train_after_train_departure",
                                        "c3_passengers_in_platform_after_train_departure"]

        self.deact_constraints_names = ["c9a_occupancy_train_departure_model_1_range_1",
                                        "c9b_occupancy_train_departure_model_1_range_2",
                                        "c10a_occupancy_train_departure_model_1_value_1",
                                        "c10b_occupancy_train_departure_model_1_value_2",
                                        "c11a_occupancy_train_departure_max_num_passengers",
                                        "c11b_occupancy_train_departure_min_num_passengers",
                                        "c12a_occupancy_train_departure_model_2_range_1",
                                        "c12b_occupancy_train_departure_model_2_range_2",
                                        "c13a_occupancy_train_departure_model_3_range_1",
                                        "c13b_occupancy_train_departure_model_3_range_2",
                                        "c15a_occupancy_train_departure_model_2_value_1",
                                        "c15b_occupancy_train_departure_model_2_value_2",
                                        "c16a_occupancy_train_departure_model_3_value_1",
                                        "c16b_occupancy_train_departure_model_3_value_2",
                                        "c18_min_occupancy_train_departure_model_1",
                                        "c19a_max_value_vSlack10a",
                                        "c19b_max_value_vSlack10b",
                                        "c20_only_one_full_train_per_occupancy_model_1",
                                        "c21a_min_value_vSlack10a",
                                        "c21b_min_value_vSlack10b"
                                        ]

        self.variable_list_names = ["vPassengersGettingOnTrain", "vPassengersGettingOffTrain",
                                    "vPassengersWaitingInStation", "vPassengersInTrain", "v01TrainStop",
                                    "v01OccupancyTrainDepartureModel_1", "v01OccupancyTrainDepartureModel_2",
                                    "v01OccupancyTrainDepartureModel_3", "v01HighTrainOccupancy", "vSlack10a",
                                    "vSlack10b", "v01NoFullTrain_a", "v01NoFullTrain_b",
                                    "vTotalPassengersGettingOnTrain"]

        if self.FIX_STOPS:
            self.variable_list_names.remove("v01TrainStop")

        if self.FIX_PASSENGERS:
            self.t_constraints_names = [c for c in self.t_constraints_names if c not in self.deact_constraints_names]

            self.t_s_constraints_names = [c for c in self.t_s_constraints_names if
                                          c not in self.deact_constraints_names]
            self.t_s_1_constraints_names = [c for c in self.t_s_1_constraints_names if
                                            c not in self.deact_constraints_names]
            self.t_s_23_constraints_names = [c for c in self.t_s_23_constraints_names if
                                            c not in self.deact_constraints_names]
            self.t_s_s_constraints_names = [c for c in self.t_s_s_constraints_names if
                                            c not in self.deact_constraints_names]

            self.variable_list_names.remove("vTotalPassengersGettingOnTrain")

        self.all_constraints_names = self.t_constraints_names + self.t_s_constraints_names + \
                                     self.t_s_1_constraints_names + self.t_s_23_constraints_names + \
                                     self.t_s_s_constraints_names

        self.t_constraints = [self.instance.__dict__[con] for con in self.t_constraints_names]
        self.t_s_constraints = [self.instance.__dict__[con] for con in self.t_s_constraints_names]
        self.t_s_1_constraints = [self.instance.__dict__[con] for con in self.t_s_1_constraints_names]
        self.t_s_23_constraints = [self.instance.__dict__[con] for con in self.t_s_23_constraints_names]
        self.t_s_s_constraints = [self.instance.__dict__[con] for con in self.t_s_s_constraints_names]
        self.deact_constrains = [self.instance.__dict__[con] for con in self.deact_constraints_names]
        self.all_constraints = [self.instance.__dict__[con] for con in self.all_constraints_names]
        self.variable_list = [self.instance.__dict__[con] for con in self.variable_list_names]


    def iterate(self, free_trains):
        """

        :param free_trains:
        :return:
        """
        instance = self.instance
        opt = self.opt
        deactivate_constraint_list(self.all_constraints)
        if self.FIX_PASSENGERS:
            deactivate_constraint_list(self.deact_constrains)
        fix_variable_list(self.variable_list)

        t_indices = free_trains
        t_s_indices = [(t, s) for (t, s) in instance.sTrains_Stations if t in free_trains]
        t_s_1_indices = [(t, s) for (t, s) in instance.sTrains_Stations_OccupancyTrainDepartureModel_1 if
                         t in free_trains]
        t_s_23_indices = [(t, s) for (t, s) in instance.sTrains_Stations_OccupancyTrainDepartureModel_2_3 if
                          t in free_trains]
        t_s_s_indices = [(t,s1,s2) for (t,s1,s2) in instance.sTrains_Stations_StationsOut if t in free_trains]

        activate_constraint_list(self.t_constraints, t_indices)
        activate_constraint_list(self.t_s_constraints, t_s_indices)
        activate_constraint_list(self.t_s_1_constraints, t_s_1_indices)
        activate_constraint_list(self.t_s_23_constraints, t_s_23_indices)
        activate_constraint_list(self.t_s_s_constraints, t_s_s_indices)

        free_variable(instance.vPassengersGettingOnTrain, t_s_s_indices)
        free_variable(instance.vPassengersGettingOffTrain, t_s_indices)
        free_variable(instance.vPassengersWaitingInStation, t_s_s_indices)
        free_variable(instance.vPassengersInTrain, t_s_s_indices)

        if not self.FIX_STOPS:
            free_variable(instance.v01TrainStop, t_s_indices)

        free_variable(instance.v01OccupancyTrainDepartureModel_1, t_s_1_indices)
        free_variable(instance.v01OccupancyTrainDepartureModel_2, t_s_23_indices)
        free_variable(instance.v01OccupancyTrainDepartureModel_3, t_s_23_indices)
        free_variable(instance.v01HighTrainOccupancy, t_s_23_indices)
        free_variable(instance.vSlack10a, t_s_1_indices)
        free_variable(instance.vSlack10b, t_s_1_indices)
        free_variable(instance.v01NoFullTrain_a, t_s_1_indices)
        free_variable(instance.v01NoFullTrain_b, t_s_1_indices)

        if not self.FIX_PASSENGERS:
            free_variable(instance.vTotalPassengersGettingOnTrain, t_s_indices)

        write_cbc_warmstart_file(WARMSTART_FILE, instance, opt)
        result = opt.solve(instance, tee=self.verbose, warmstart=True, warmstart_file=WARMSTART_FILE)
        status = result.solver.termination_condition
        obj = instance.f_obj()

        return str(status), obj


    def get_iterative_solution(self, k, reorganize=None):
        """

        :param k:
        :param reorganize:
        :return:
        """
        instance = self.instance
        opt = self.opt

        for variable in self.variable_list:
            variable.fix(0)

        if self.FIX_STOPS:
            for key, value in self.stops_dict.items():
                instance.v01TrainStop[key].fix(value)
        else:
            for i in instance.sTrains_Stations:
                instance.v01TrainStop[i] = 0

        if self.FIX_PASSENGERS:
            for key, value in self.passengers_dict.items():
                instance.vTotalPassengersGettingOnTrain[key].fix(value)

        n_total = len(self.sTrains)
        n = 0
        i = 0
        while n < n_total:
            n = min(n + k, n_total)
            if i == 0:
                free_trains = self.sTrains[(n - k):n]
            else:
                free_trains = self.sTrains[(n - k - 2):n]
            if (n - k) > 0:
                fixed_trains = self.sTrains[0:(n - k)]
            else:
                fixed_trains = []

            print("Solving trains:", free_trains)

            status, obj = self.iterate(free_trains)
            print(status)
            print(obj)

            i += 1

        print("Solving everything with warmstart")
        activate_constraint_list(self.all_constraints)
        free_variable_list(self.variable_list)
        write_cbc_warmstart_file(WARMSTART_FILE, instance, opt)
        result = opt.solve(instance, tee=self.verbose, warmstart=True, warmstart_file=WARMSTART_FILE)
        status = result.solver.termination_condition
        obj = instance.f_obj()
        print(status)
        print(obj)
        self.status = str(status)
