import sys
import json

import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal, Qt

from globals import Global
from global_g import ureg
from windows.global_windows import G_Windows

class InputDialog(qtw.QDialog):
    input_submitted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.G = Global
        self.GW = G_Windows

        self.setWindowTitle("Initial state")
        self.setGeometry(250, 200, 500, 250)
        # removes the question mark "?" (for help) at the top of the window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = qtw.QVBoxLayout()
        dropdown_layout = qtw.QGridLayout()
        input_layout = qtw.QGridLayout()

        with open('initial_values.json', 'r') as init_file:
            self.json_data = json.load(init_file)
            self.GW.initial_values = self.json_data['vals']

        self.init_dropdown(self.GW.length_dropdown, self.GW.LENGTH, self.G.DEFAULT_LENGTH)
        self.init_dropdown(self.GW.mass_dropdown, self.GW.MASS, self.G.DEFAULT_MASS)

        self.G.current_length = self.GW.LENGTH[self.GW.length_dropdown.currentText()]
        self.G.current_mass = self.GW.MASS[self.GW.mass_dropdown.currentText()]

        self.GW.length_dropdown.activated.connect(self.length_change)
        self.GW.mass_dropdown.activated.connect(self.mass_change)

        dropdown_layout.addWidget(self.GW.length_dropdown, 0, 0)
        dropdown_layout.addWidget(self.GW.mass_dropdown, 0, 1)

        self.inputs = {}
        for index, val in enumerate(self.GW.initial_values):
            if self.GW.initial_values[val]['disable']['field']:
                continue
            input_layout.addWidget(qtw.QLabel(val + ':'), index, 0)
            self.inputs[val] = qtw.QLineEdit()

            initial_val = self.GW.initial_values[val]['initial']
            if initial_val != None:
                self.inputs[val].setPlaceholderText(str(initial_val))

            input_layout.addWidget(self.inputs[val], index, 1)

        submit_button = qtw.QPushButton("Set initial state")
        submit_button.clicked.connect(self.submit_input)

        load_state_button = qtw.QPushButton("Load initial state")
        load_state_button.clicked.connect(self.load_initial_state)

        main_layout.addWidget(load_state_button)
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(submit_button)

        self.setLayout(main_layout)

    def load_initial_state(self):
        file_name, _ = qtw.QFileDialog.getOpenFileName(self, "Open .json file with initial state", "", "JSON Files (*.json)")
        error_box = qtw.QMessageBox()

        if not file_name:
            return

        with open(file_name, 'r') as file:
            try:
                save = json.load(file)
                version = save['version']
                version_err_msg = f'<br /><br />Save file version: <b>{version}</b>. Program version: <b>{self.G.VERSION}</b>.'

                saved_length = save['measurements']['length']
                saved_mass = save['measurements']['mass']
                is_length_same = ureg.Quantity(1, saved_length) == 1 * self.G.current_length
                is_mass_same = ureg.Quantity(1, saved_mass) == 1 * self.G.current_mass

                if save['filetype'] != self.G.SAVEFILE_TYPE:
                    error_box.setWindowTitle("Error")
                    error_box.setIcon(qtw.QMessageBox.Critical)
                    error_box.setText("The loaded .json file is not of the correct format.")
                    error_box.exec_()
                    return
                
                unrecognized_values = []

                for key, value in save['data'].items():
                    try:
                        self.inputs[key].setText(str(value))
                    
                    # if "key" fails the execution will continue here
                    except KeyError as err:
                        unrecognized_values.append(f'<b>{err}</b>')
                        continue

                if len(unrecognized_values) != 0:
                    error_box.setWindowTitle("Warning")
                    error_box.setIcon(qtw.QMessageBox.Warning)
                    error_box.setText(f"The following fields: {', '.join(unrecognized_values)} were skipped, since they were not recognized as initial value.<br /><br />Either they are not part of the program's state anymore, or the save data was edited manually.{version_err_msg}")
                    error_box.exec_()

                # if mass and length preferred measurements differ from current, change dropdown menus chosen items                
                if not is_length_same:
                    self.G.current_length = self.GW.load_file_change_dropdown(self.GW.LENGTH, saved_length, self.GW.length_dropdown)
                if not is_mass_same:
                    self.G.current_mass = self.GW.load_file_change_dropdown(self.GW.MASS, saved_mass, self.GW.mass_dropdown)

            except (json.JSONDecodeError, KeyError) as err:
                print(f'Error reading JSON: {err}')
                error_box.setWindowTitle("Error")
                error_box.setIcon(qtw.QMessageBox.Critical)
                error_box.setText(f"An error occurred while reading the JSON file: <b>{err}</b>.{version_err_msg}")
                error_box.exec_()

        return

    def length_change(self, chosen_index):
        """
            chosen_index corresponds for index of the chosen option in the dropdown
            sets current_length/mass to current dropdown in pint representation
        """
        self.G.current_length = self.measurement_change(self.GW.length_dropdown, self.GW.LENGTH, self.G.current_length, 'length')

    def mass_change(self, chosen_index):
        self.G.current_mass = self.measurement_change(self.GW.mass_dropdown, self.GW.MASS, self.G.current_mass, 'mass')

    def measurement_change(self, dropdown, measurement_arr, current_measurement, type):
        """
            gets fired when length or mass dropdowns are changed
        """
        selected_option = measurement_arr[dropdown.currentText()]

        for key, value in self.inputs.items():
            datatype = self.GW.initial_values[key]['type']

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
            first initialization of dropdowns
            adds text to mass and length dropdowns.
            sets default dropdown based on the default_dropdown value (DEFAULT_LENGTH, DEFAULT_MASS)
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
        
        len_mass_map = { # for values and measurements conversion
            'length': (self.G.current_length, self.G.DEFAULT_LENGTH),
            'mass': (self.G.current_mass, self.G.DEFAULT_MASS)
        }

        for key, value in self.inputs.items():
            input = value.text()
            initial_state[key] = {}
            current_state = initial_state[key]
            initial_key = self.GW.initial_values[key]
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
                            placeholder *= self.G.current_length
                        elif datatype['mass']:
                            placeholder *= self.G.current_mass
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
                for key, value in len_mass_map.items():
                    if datatype[key]:
                        (current_measurement, default_measurement) = len_mass_map[key]
                        current_state['inputted'] = input * current_measurement
                        if current_measurement != default_measurement:
                            input *= current_measurement
                            input = input.to(default_measurement).magnitude
                        break

                current_state['converted'] = input

        if bad_inputs:
            qtw.QMessageBox.warning(self, "Error", '<br />'.join(bad_inputs))
            return False
        
        self.G.initial_state = initial_state
        print("\n---- INPUT DATA ----:\n", initial_state)
        self.input_submitted.emit(initial_state)
        self.accept()

    def closeEvent(self, event):
        """
            finish the program if user closes the window
        """
        sys.exit()
