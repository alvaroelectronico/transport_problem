import pandas as pd
from pyomo.environ import value

from const import BASE_OUTPUT_PATH, OUTPUT_TABLES_CONFIG, STATIONS_NAMES


def export_data(instance):

    output_df = dict()

    for tab in OUTPUT_TABLES_CONFIG:
        data = dict()
        table = OUTPUT_TABLES_CONFIG[tab]
        for col in table['columns']:
            data[col] = list()

        for var in getattr(instance, table['set']):
            val = value(getattr(instance, table['variable'])[var])
            if val >= 0:
                for x in range(0, len(var)):
                    #if table['columns'][x] == 'stop':
                    #    data[table['columns'][x]].append(STATIONS_NAMES[var[x]])
                    #else:
                    data[table['columns'][x]].append(var[x])
                data[table['columns'][-1]].append(round(val, 4))

        output_df[tab] = pd.DataFrame.from_dict(data)
        output_df[tab].to_csv(path_or_buf=BASE_OUTPUT_PATH + table['file_name'], index=False)

    return output_df
