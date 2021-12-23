
import datetime as dt
from pyomo_utils import deactivate_constraint_list


def format_date(date):
    """
    
    :param date:
    :return:
    """
    return dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")


def set_c22_version(instance, c22_version):
    """
    
    :param instance: a model instance
    :param c22_version: 1 or 2
    :return: activate or deactivate constraint in the instance
    """
    
    if c22_version == 1:
        instance.c22_v2_discrepancy_estimate.deactivate()
        instance.c22_v1_discrepancy_estimate.activate()
        # deactivate_constraint(instance.c22_v2_discrepancy_estimate)
        # activate_constraint(instance.c22_v1_discrepancy_estimate)
    elif c22_version == 2:
        instance.c22_v2_discrepancy_estimate.activate()
        instance.c22_v1_discrepancy_estimate.deactivate()
        # deactivate_constraint(instance.c22_v1_discrepancy_estimate)
        # activate_constraint(instance.c22_v2_discrepancy_estimate)
    else:
        raise Exception("c22 version must be set to 1 or 2")


def fix_solution(instance, input_data, fixed_trains, fixed_people_in):
    """
    
    :param instance: a pyomo instance
    :param input_data: the instance input data
    :param fixed_trains: True if the train stops must be fixed
    :param fixed_people_in:  True if the number of people getting on train must be fixed
    :return: modify the isntance
    """
    if fixed_trains or fixed_people_in:
        for k, v in input_data.fixed_stops.items():
            instance.v01TrainStop[k].fix(v)
    
    c_to_be_deactivated = [
        instance.c9a_occupancy_train_departure_model_1_range_1,
        instance.c9b_occupancy_train_departure_model_1_range_2,
        instance.c10a_occupancy_train_departure_model_1_value_1,
        instance.c10b_occupancy_train_departure_model_1_value_2,
        instance.c11a_occupancy_train_departure_max_num_passengers,
        instance.c11b_occupancy_train_departure_max_num_passengers,
        instance.c12a_occupancy_train_departure_model_2_range_1,
        instance.c12b_occupancy_train_departure_model_2_range_2,
        instance.c13a_occupancy_train_departure_model_3_range_1,
        instance.c13b_occupancy_train_departure_model_3_range_2,
        instance.c15a_occupancy_train_departure_model_2_value_1,
        instance.c15b_occupancy_train_departure_model_2_value_2,
        instance.c16a_occupancy_train_departure_model_3_value_1,
        instance.c16b_occupancy_train_departure_model_3_value_2,
        instance.c18_min_occupancy_train_departure_model_1,
        instance.c19b_max_value_vSlack10b,
        instance.c20_only_one_full_train_per_occupancy_model_1,
        instance.c21a_min_value_vSlack10a,
        instance.c21b_min_value_vSlack10b
    ]
    
    if fixed_people_in:
        deactivate_constraint_list(c_to_be_deactivated)
        for k, v in input_data.fixed_people_in.items():
            instance.vTotalPassengersGettingOnTrain[k].fix(v)



