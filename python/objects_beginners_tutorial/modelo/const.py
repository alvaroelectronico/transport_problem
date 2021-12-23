# {'columns': [], 'variable':'', 'set':'', 'file_name':''}
OUTPUT_TABLES_CONFIG = {'Transport': {'columns': ['plant', 'customer', 'stops'], 'variable': 'vTransport',
                                       'set': 'sCustomers', 'file_name': 'transport.csv'}}

BASE_OUTPUT_PATH = 'data/output/'

# Version of the c22 in the model
#C22_VERSION = 1

# Force the solution from the input data:
# FIXED_TRAINS = False
# FIXED_PEOPLE_IN = False

# 0: no adjusting
# 1: adjust OD_matrix data with PeopleFlow data
# 2: adjust PeopleIn values with OD_matrix values.
# ADJUST_ARRIVALS = 0

SOLVER_PARAMETERS = {
    # maximum resolution time
    "sec": 600,
    # accepted absolute gap
    "allow": 1,
    # accepted relative gap (0.01 = 1%)
    "ratio": 0.01,
    # model tolerance
    "primalT": 10 ** -7
}

WARMSTART_FILE = "cbc_warmstart.soln"
