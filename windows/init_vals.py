import json
from datetime import datetime

import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal

from globals import Global
from windows.global_windows import G_Windows
from windows.init_state_layout import init_state_layout

class InitialValuesWindow(qtw.QMainWindow):
    _instance = None
    initial_values_updated = pyqtSignal(dict)

    def __new__(cls, *args, **kwargs):
        """
            make the window/class singleton
            so every time user clicks it, we dont create it again
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    @staticmethod
    def get_instance(parent):
        if InitialValuesWindow._instance is None:
            InitialValuesWindow._instance = InitialValuesWindow(parent)
        return InitialValuesWindow._instance

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Initial state")

        self.G = Global
        self.GW = G_Windows

        # set window in center
        parent_rect = parent.geometry()
        self.move(
            parent_rect.center().x() - self.rect().center().x(),
            parent_rect.center().y() - self.rect().center().y()
        )

        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = qtw.QVBoxLayout(central_widget)
        buttons_layout = qtw.QGridLayout()

        savefile_state_button = qtw.QPushButton("Save to file")
        savefile_state_button.clicked.connect(self.save_to_file)
        buttons_layout.addWidget(savefile_state_button, 0, 0)

        self.init_state = init_state_layout()
        save_state_button = qtw.QPushButton("Save")
        save_state_button.clicked.connect(self.save_input)
       # save_state_button.setDefault(True) set focus on save button
        buttons_layout.addWidget(save_state_button, 0, 1)

        main_layout.addLayout(self.init_state.get_layout())
        main_layout.addLayout(buttons_layout)

    def save_input(self):
        data = self.init_state.save_init_state(self)
        self.initial_values_updated.emit(self.G.initial_state)
        """ m = MainWindow()
        m.show() """
        # redraw the graphs
        return data

    def save_to_file(self):
        if not self.save_input():
            return
        for key, value in self.G.initial_state.items():
            val = value['inputted']
            self.G.savedata['data'][key] = val if isinstance(val, str) else val.magnitude

        self.G.savedata['measurements']['length'] = str(self.G.current_length)
        self.G.savedata['measurements']['mass'] = str(self.G.current_mass)
        self.G.savedata['time_saved'] = str(datetime.now())

        file_path, _ = qtw.QFileDialog.getSaveFileName(self, "Save your initial state", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "w") as file:
                json.dump(self.G.savedata, file, indent=4)
            
        self.G.savedata['data'] = { }