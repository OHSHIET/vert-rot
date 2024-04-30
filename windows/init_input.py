import sys
import json

import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal, Qt

from globals import Global
from global_g import ureg
from windows.global_windows import G_Windows
from windows.init_state_layout import init_state_layout

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

        self.main_layout = qtw.QVBoxLayout()

        self.init_state = init_state_layout()

        self.inputs = self.init_state.get_inputs()

        load_state_button = qtw.QPushButton("Load initial state")
        load_state_button.clicked.connect(self.load_initial_state)

        submit_button = qtw.QPushButton("Set initial state")
        submit_button.clicked.connect(self.submit_input)

        # set focus on set state button
        submit_button.setDefault(True)

        self.main_layout.addWidget(load_state_button)
        self.main_layout.addLayout(self.init_state.get_layout())
        self.main_layout.addWidget(submit_button)

        self.setLayout(self.main_layout)

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

    def submit_input(self):
        init_state = self.init_state.save_init_state(self)
        if not init_state:
            return
        self.input_submitted.emit(init_state)
        self.accept()

    def closeEvent(self, event):
        """
            finish the program if user closes the window
        """
        sys.exit()
