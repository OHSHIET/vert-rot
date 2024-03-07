import pint
from collections import OrderedDict

class Global:
    ureg = pint.UnitRegistry()
    # sets default both for dropdowns and converting when passing to the calculations
    DEFAULT_LENGTH = ureg.meter
    DEFAULT_MASS = ureg.tonne

    # string used to determine whether a .json file is the app's savefile
    SAVEFILE_TYPE = 'vert-rot-savefile'

    initial_state = None
    init_vals_table = None

    def handle_initial_data(data):
        return data