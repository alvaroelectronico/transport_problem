import pandas as pd
from const import BASE_OUTPUT_PATH

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 50)


def calculate_percentage(numerator, denominator, prec=5):
    """
    Function to calculate a percentage error but to give back a 100% in case the denominator is 0

    :param numerator: number that only appears in the numerator of the division
    :param denominator: number that appears in the denominator of the division and the numerator
    :return: the percentage error calculated
    """
    if denominator == 0:
        percentage = 100
    else:
        percentage = round(abs(numerator - denominator) / denominator * 100, prec)
    return percentage


def compare_output(input_data, output_data):
    """
    Function to compare the input data with the output data of the model.

    :param input_data: stopTimes_peopleFlow raw file input
    :param output_data: results from the model
    :return: a new data frame with the format of stopTimes_peopleFlow with the results of the model added to it.
    """
    compare_df = input_data.sort_values('trainOrder', ascending=True)

    # STOPS
    compare_df['stops'] = compare_df.apply(
        lambda row: row['peopleIn'] != 0 or row['OccupancyArrival'] != row['OccupancyDeparture'], axis=1)

    compare_df = pd.merge(compare_df, output_data['TrainStops'], how='left', on=['trainOrder', 'stop']).rename(
        columns={'stops_x': 'stops'})
    compare_df['stops_output'] = compare_df.apply(lambda row: row['stops_y'] == 1, axis=1)
    compare_df = compare_df.drop(['stops_y'], axis=1)
    compare_df['stops_diff'] = compare_df.apply(lambda row: row['stops'] != row['stops_output'], axis=1)

    # PEOPLE IN
    temp_df = output_data['Boarding'].groupby(['trainOrder', 'stop'], as_index=False)[['peopleIn']].sum().rename(
        columns={'peopleIn': 'peopleIn_output'})

    compare_df = pd.merge(compare_df, temp_df, how='left', on=['trainOrder', 'stop'])
    compare_df['peopleIn_diff'] = compare_df.apply(lambda row: row['peopleIn'] - row['peopleIn_output'], axis=1)
    compare_df['peopleIn_diff_abs'] = compare_df.apply(lambda row: abs(row['peopleIn'] - row['peopleIn_output']),
                                                       axis=1)
    compare_df['peopleIn_diff_perc'] = compare_df.apply(
        lambda row: calculate_percentage(row['peopleIn_output'], row['peopleIn']), axis=1)
    compare_df['peopleIn_diff_perc_2'] = compare_df.apply(
        lambda row: calculate_percentage(row['peopleIn'], row['peopleIn_output']), axis=1)

    # PEOPLE OUT
    temp_df = output_data['Unboarding'].rename(columns={'peopleOut': 'peopleOut_output'})

    compare_df = pd.merge(compare_df, temp_df, how='left', on=['trainOrder', 'stop'])
    compare_df['peopleOut_diff'] = compare_df.apply(lambda row: row['peopleOut'] - row['peopleOut_output'], axis=1)
    compare_df['peopleOut_diff_abs'] = compare_df.apply(lambda row: abs(row['peopleOut'] - row['peopleOut_output']),
                                                        axis=1)
    compare_df['peopleOut_diff_perc'] = compare_df.apply(
        lambda row: calculate_percentage(row['peopleOut_output'], row['peopleOut']), axis=1)
    compare_df['peopleOut_diff_perc_2'] = compare_df.apply(
        lambda row: calculate_percentage(row['peopleOut'], row['peopleOut_output']), axis=1)

    # PEOPLE WAITING
    temp_df = output_data['Waiting'].groupby(['trainOrder', 'stop'], as_index=False)[['FTB']].sum().rename(
        columns={'FTB': 'FTB_output'})

    compare_df = pd.merge(compare_df, temp_df, how='left', on=['trainOrder', 'stop'])
    compare_df['FTB_diff'] = compare_df.apply(lambda row: row['FTB'] - row['FTB_output'], axis=1)
    compare_df['FTB_diff_abs'] = compare_df.apply(lambda row: abs(row['FTB'] - row['FTB_output']),
                                                  axis=1)
    compare_df['FTB_diff_perc'] = compare_df.apply(
        lambda row: calculate_percentage(row['FTB_output'], row['FTB']), axis=1)
    compare_df['FTB_diff_perc_2'] = compare_df.apply(
        lambda row: calculate_percentage(row['FTB'], row['FTB_output']), axis=1)

    compare_df.to_csv(path_or_buf=BASE_OUTPUT_PATH + 'StopTimes_PeopleFlow.csv', index=False)

    return compare_df


def get_kpi(data):
    """
    Function to calculate different kpi of the comparision

    :param data: the compare data frame calculated by the compare_output function
    :return: a dict with different data frames to compare data
    """
    result = dict()
    train = data.groupby('trainOrder', as_index=False)[['peopleIn_diff', 'peopleOut_diff', 'FTB_diff']].sum().rename(
        columns={'peopleIn_diff': 'peopleIn', 'peopleOut_diff': 'people_out', 'FTB_diff': 'FTB'})
    result['Train'] = train

    return result
