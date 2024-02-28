import sys
import json

import pint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal, Qt

from eq_VerticalROTnoForces import Main

def handle_initial_data(data):
    return data

class InputDialog(qtw.QDialog):
    input_submitted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ureg = pint.UnitRegistry()

        self.setWindowTitle("Initial values (leave empty for default)")
        self.setGeometry(250, 200, 500, 250)
        # removes the question mark "?" (for help) at the top of the window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = qtw.QVBoxLayout()
        dropdown_layout = qtw.QGridLayout()
        input_layout = qtw.QGridLayout()

        with open('initial_values.json', 'r') as init_file:
            self.json_data = json.load(init_file)
            self.initial_values = self.json_data['vals']
            
        self.length = {"Metres": self.ureg.metre, "Kilometres": self.ureg.kilometre, "Inches": self.ureg.inch, "Feet": self.ureg.foot, "Yards": self.ureg.yard, "Miles": self.ureg.mile}
        self.mass = {"Grams": self.ureg.gram, "Kilograms": self.ureg.kilogram, "Tonnes": self.ureg.tonne, "Ounces": self.ureg.ounce, "Pounds": self.ureg.pound}

        self.length_dropdown = qtw.QComboBox()
        self.mass_dropdown = qtw.QComboBox()

        self.init_dropdown(self.length_dropdown, self.length, 0)
        self.init_dropdown(self.mass_dropdown, self.mass, 2)

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
            self.inputs[val].setPlaceholderText(str(self.initial_values[val]['initial']))
            input_layout.addWidget(self.inputs[val], index, 1)

        self.submit_button = qtw.QPushButton("Set initial state")
        self.submit_button.clicked.connect(self.submit_input)

        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.submit_button)

        self.setLayout(main_layout)

    def length_change(self):
        self.current_length = self.measurement_change(self.length_dropdown, self.length, self.current_length, 'length')
    
    def mass_change(self):
        self.current_mass = self.measurement_change(self.mass_dropdown, self.mass, self.current_mass, 'mass')

    def measurement_change(self, dropdown, measurement_arr, current_measurement, type):
        selected_option = measurement_arr[dropdown.currentText()]

        for key, value in self.inputs.items():
            datatype = self.initial_values[key]['type']

            input = value.text()
            placeholder = float(self.inputs[key].placeholderText())

            if not datatype[type] or (not input and placeholder == 0):
                continue

            if len(input) == 0:
                placeholder *= current_measurement
                self.inputs[key].setPlaceholderText(str(placeholder.to(selected_option).magnitude)) # func for transforming
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

    def init_dropdown(self, dropdown, measurement_arr, default_index):
        for measurement in measurement_arr.keys():
            dropdown.addItem(measurement)
        dropdown.setCurrentIndex(default_index)

    def submit_input(self):
        initial_state = {}
        bad_inputs = [] # user's inputs that didnt pass the tests and we need to warn the user about it

        for key, value in self.inputs.items():
            input = value.text()

            if len(input) == 0: # use initial value, if input is empty
                initial_state[key] = self.initial_values[key]['initial']

            else:
                json_helpers = self.json_data['helpers']
                datatype = self.initial_values[key]['type']

                if datatype['num']:
                    try:
                        temp_input = float(input)
                    except ValueError:
                        bad_inputs.append(f'<b>{key}:</b> the input value should be a number.')
                        continue
                    
                    greater_than = self.initial_values[key]['range']['greater_than']
                    less_than = self.initial_values[key]['range']['less_than']
                    
                    if (greater_than != None and temp_input <= greater_than) or (less_than != None and temp_input >= less_than):
                        bad_inputs.append(f'<b>{key}:</b> the input value should be {f'greater than {greater_than}' if greater_than != None else ''}{' and ' if greater_than != None and less_than != None else ''}{f'less than {less_than}' if less_than != None else ''}.')
                        continue
                    
                    input = temp_input
                    
                elif datatype['string'] and len(input) > json_helpers['max_string_len']:
                    bad_inputs.append(f'<b>{key}:</b> the input string should be max {json_helpers['max_string_len']} chars in length.')
                    continue

                # if user is submitting input values not in tonnes and meters, convert the values back
                if datatype['length'] and self.current_length != self.ureg.meter:
                    input *= self.current_length
                    input = input.to(self.ureg.meter).magnitude
                
                elif datatype['mass'] and self.current_length != self.ureg.tonne:
                    input *= self.current_mass
                    input = input.to(self.ureg.tonne).magnitude

                initial_state[key] = input

        if bad_inputs:
            qtw.QMessageBox.warning(self, "Error", '<br />'.join(bad_inputs))
            return False
        
        print("---- INPUT DATA ----:\n", initial_state)
        self.input_submitted.emit(initial_state)
        self.accept()

    # finish the program if user closes the window
    def closeEvent(self, event):
        sys.exit()


class PlotWidget(qtw.QWidget):
    def __init__(self, initial_state):
        super().__init__()

        self.figure = Main(initial_state)
        self.canvas = FigureCanvas(self.figure)

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class MainWindow(qtw.QMainWindow):
    def __init__(self, plot_widget):
        super().__init__()
        self.setWindowTitle("Grid Plot Layout")

        # window position and size
        self.setGeometry(100, 100, 800, 600)

        # main layout for graphs + buttons
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = qtw.QVBoxLayout()
        central_widget.setLayout(main_layout)

        # buttons widget
        buttons_layout = qtw.QGridLayout()

        buttons = [
            ("Button 1", 0, 0),
            ("Button 2", 0, 1),
            ("Button 3", 1, 0),
            ("Button 4", 1, 1)
        ]

        for text, row, col in buttons:
            button = qtw.QPushButton(text)
            buttons_layout.addWidget(button, row, col)

        # add buttons and graphs to the main layout
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(plot_widget)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    input_dialog = InputDialog()

    initial_state = {}
    input_dialog.input_submitted.connect(lambda data: setattr(sys.modules[__name__], 'initial_state', handle_initial_data(data)))
    input_dialog.exec_()

    plot_widget = PlotWidget(initial_state)
    main_window = MainWindow(plot_widget)

    main_window.show()
    sys.exit(app.exec_())