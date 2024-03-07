import sys
import json
from collections import OrderedDict

import pint
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal, Qt

from globals import Global

class InputDialog(qtw.QDialog):
    input_submitted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.GV = Global

        self.setWindowTitle("Initial state")
        self.setGeometry(250, 200, 500, 250)
        # removes the question mark "?" (for help) at the top of the window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = qtw.QVBoxLayout()
        dropdown_layout = qtw.QGridLayout()
        input_layout = qtw.QGridLayout()

        with open('initial_values.json', 'r') as init_file:
            self.json_data = json.load(init_file)
            self.initial_values = self.json_data['vals']
            
        # also change the dict in show_init_vals when adding new measurements
        # !!! make this more convenient to change
        self.length = OrderedDict({
            "Meters": self.GV.ureg.metre,
            "Kilometers": self.GV.ureg.kilometre,
            "Inches": self.GV.ureg.inch,
            "Feet": self.GV.ureg.foot,
            "Yards": self.GV.ureg.yard,
            "Miles": self.GV.ureg.mile
        })
        self.mass = OrderedDict({
            "Grams": self.GV.ureg.gram,
            "Kilograms": self.GV.ureg.kilogram,
            "Tonnes": self.GV.ureg.tonne,
            "Ounces": self.GV.ureg.ounce,
            "Pounds": self.GV.ureg.pound
        })

        self.length_dropdown = qtw.QComboBox()
        self.mass_dropdown = qtw.QComboBox()

        self.init_dropdown(self.length_dropdown, self.length, self.GV.DEFAULT_LENGTH)
        self.init_dropdown(self.mass_dropdown, self.mass, self.GV.DEFAULT_MASS)

        self.current_length = self.length[self.length_dropdown.currentText()]
        self.current_mass = self.mass[self.mass_dropdown.currentText()]

        self.length_dropdown.activated.connect(self.length_change)
        self.mass_dropdown.activated.connect(self.mass_change)

        dropdown_layout.addWidget(self.length_dropdown, 0, 0)
        dropdown_layout.addWidget(self.mass_dropdown, 0, 1)

        self.inputs = {}
        for index, val in enumerate(self.initial_values):
            if self.initial_values[val]['disable']['field']:
                continue
            input_layout.addWidget(qtw.QLabel(val + ':'), index, 0)
            self.inputs[val] = qtw.QLineEdit()

            initial_val = self.initial_values[val]['initial']
            if initial_val != None:
                self.inputs[val].setPlaceholderText(str(initial_val))

            input_layout.addWidget(self.inputs[val], index, 1)

        submit_button = qtw.QPushButton("Set initial state")
        submit_button.clicked.connect(self.submit_input)

        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(submit_button)

        self.setLayout(main_layout)

    def length_change(self, chosen_index):
        """
            chosen_index corresponds for index of the chosen option in the dropdown
            sets current_length/mass to current dropdown in pint representation
        """
        self.current_length = self.measurement_change(self.length_dropdown, self.length, self.current_length, 'length')
    
    def mass_change(self, chosen_index):
        self.current_mass = self.measurement_change(self.mass_dropdown, self.mass, self.current_mass, 'mass')

    def measurement_change(self, dropdown, measurement_arr, current_measurement, type):
        """
            gets fired when length or mass dropdowns are changed
        """
        selected_option = measurement_arr[dropdown.currentText()]

        for key, value in self.inputs.items():
            datatype = self.initial_values[key]['type']

            input = value.text()
            placeholder = None
            try: 
                placeholder = float(self.inputs[key].placeholderText())
            except ValueError:
                pass

            if not datatype[type] or (not input and placeholder == 0):
                continue

            if len(input) == 0:
                placeholder *= current_measurement
                self.inputs[key].setPlaceholderText(str(placeholder.to(selected_option).magnitude))
            else:
                try:
                    input = float(input)
                    if input == 0:
                        continue
                    input *= current_measurement
                except ValueError:
                    continue

                self.inputs[key].setText(str(input.to(selected_option).magnitude))
        return selected_option

    def init_dropdown(self, dropdown, measurement_arr, default_dropdown):
        """
            adds text to mass and length dropdowns.
            automatically sets default chosen dropdown based on the default_dropdown value
        """
        counter = 0
        for measurement_str, measurement in measurement_arr.items():
            dropdown.addItem(measurement_str)
            if default_dropdown == measurement:
                dropdown.setCurrentIndex(counter)
            counter += 1

    def submit_input(self):
        """
            gets fired when user clicks on submitting their input

            handles checking if data is not how we like it, based on the initial_values.json

            after passing all the checks puts all the good inputs in initial_state,
            with fields 'converted' and 'inputted'
            'converted' converts the num-values to default specified length/mass
            'inputted' leaves them as user typed them in
        """
        initial_state = {}
        bad_inputs = [] # user's inputs that didnt pass the tests and we need to warn the user about it

        for key, value in self.inputs.items():
            input = value.text()
            initial_state[key] = {}
            current_state = initial_state[key]
            initial_key = self.initial_values[key]
            datatype = initial_key['type']

            if len(input) == 0:
                if initial_key['initial'] == None:
                    bad_inputs.append(f'<b>{key}:</b> required field.')
                else:
                    current_state['converted'] = initial_key['initial']
                    placeholder = self.inputs[key].placeholderText()
                    try:
                        placeholder = float(placeholder)
                        if datatype['length']:
                            placeholder *= self.current_length
                        elif datatype['mass']:
                            placeholder *= self.current_mass
                    except ValueError:
                        pass
                    finally:
                        current_state['inputted'] = placeholder

            else:
                json_helpers = self.json_data['helpers']

                if datatype['num']:
                    try:
                        temp_input = float(input)
                    except ValueError:
                        bad_inputs.append(f'<b>{key}:</b> the input value should be a number.')
                        continue
                    
                    greater_than = initial_key['range']['greater_than']
                    less_than = initial_key['range']['less_than']
                    
                    if (greater_than != None and temp_input <= greater_than) or (less_than != None and temp_input >= less_than):
                        bad_inputs.append(f'<b>{key}:</b> the input value should be {f'greater than {greater_than}' if greater_than != None else ''}{' and ' if greater_than != None and less_than != None else ''}{f'less than {less_than}' if less_than != None else ''}.')
                        continue
                    
                    input = temp_input
                    
                elif datatype['string']:
                    current_state['inputted'] = input
                    if len(input) > json_helpers['max_string_len']:
                        bad_inputs.append(f'<b>{key}:</b> the input string should be max {json_helpers['max_string_len']} chars in length.')
                        continue

                # if user is submitting input values not in tonnes and meters, convert the values back
                if datatype['length']:
                    current_state['inputted'] = input * self.current_length
                    if self.current_length != self.GV.DEFAULT_LENGTH:
                        input *= self.current_length
                        input = input.to(self.GV.DEFAULT_LENGTH).magnitude
                
                elif datatype['mass']:
                    current_state['inputted'] = input * self.current_mass
                    if self.current_length != self.GV.DEFAULT_MASS:
                        input *= self.current_mass
                        input = input.to(self.GV.DEFAULT_MASS).magnitude

                current_state['converted'] = input

        if bad_inputs:
            qtw.QMessageBox.warning(self, "Error", '<br />'.join(bad_inputs))
            return False
        
        self.GV.initial_state = initial_state
        print("\n---- INPUT DATA ----:\n", initial_state)
        self.input_submitted.emit(initial_state)
        self.accept()

    def closeEvent(self, event):
        """
            finish the program if user closes the window
        """
        sys.exit()
