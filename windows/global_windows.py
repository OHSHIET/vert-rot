from collections import OrderedDict

from PyQt5.QtWidgets import QComboBox, QGridLayout, QWidget

from global_g import ureg, global_app

class G_Windows:
    # since pint for some reason doesnt provide readable measurements...
    # also change "readable_measurement" when changing this
    LENGTH = OrderedDict({
        "Meters": ureg.metre,
        "Kilometers": ureg.kilometre,
        "Inches": ureg.inch,
        "Feet": ureg.foot,
        "Yards": ureg.yard,
        "Miles": ureg.mile
    })
    MASS = OrderedDict({
        "Grams": ureg.gram,
        "Kilograms": ureg.kilogram,
        "Tonnes": ureg.tonne,
        "Ounces": ureg.ounce,
        "Pounds": ureg.pound
    })

    # also change length and mass dicts when changing this
    READABLE_MEASUREMENT = {
        "meter": "m",
        "kilometer": "km",
        "inch": "in",
        "foot": "ft",
        "yard": "yd",
        "mile": "mi",
        "gram": "g",
        "kilogram": "kg",
        "metric_ton": "t",
        "ounce": "oz",
        "pound": "ld"
    }

    initial_values = None

    input_layout = QGridLayout()

    length_dropdown = QComboBox()
    mass_dropdown = QComboBox()

    def load_file_change_dropdown(MEASUREMENT_ARR, preferred_measurement, measurement_dropdown):
        for index, (_key, value) in enumerate(MEASUREMENT_ARR.items()):
            if ureg.Quantity(1, preferred_measurement) == 1 * value:
                measurement_dropdown.setCurrentIndex(index)
                return value