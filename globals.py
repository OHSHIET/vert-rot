from datetime import datetime

from global_ureg import ureg

class Global:
    # string used to determine whether a .json file is the app's savefile
    SAVEFILE_TYPE = 'vert-rot-savefile'
    # indicates version of app and savefiles
    VERSION = 0.1

    # sets default both for dropdowns and converting when passing to the calculations
    DEFAULT_LENGTH = ureg.meter
    DEFAULT_MASS = ureg.tonne

    # dynamic variables
    current_length = DEFAULT_LENGTH
    current_mass = DEFAULT_MASS

    initial_state = None
    init_vals_table = None

    savedata = {
        "filetype": SAVEFILE_TYPE,
        "version": VERSION,
        "time_saved": str(datetime.now()),
        "measurements": { # data is saved in following preferred measurements
            "length": str(current_length), # changes when saved
            "mass": str(current_mass),
        },
        "data": { }
    }

    def handle_initial_data(data):
        return data