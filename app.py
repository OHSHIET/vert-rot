import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal

from eq_VerticalROTnoForces import Main


def handle_initial_data(data):
    return data


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class InputDialog(qtw.QDialog):
    input_submitted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Initial values (leave empty for default)")
        self.setGeometry(250, 200, 500, 250)

        layout = qtw.QGridLayout()

        # change initial state to support only positive values, only ints and only strings
        self.labels = ["Displacement tonnage:", "X:", "Y:", "Z:"]  # initial_state
        self.inputs = {}

        for row, label in enumerate(self.labels):
            layout.addWidget(qtw.QLabel(label), row, 0)
            self.inputs[label] = qtw.QLineEdit()
            layout.addWidget(self.inputs[label], row, 1)

        self.submit_button = qtw.QPushButton("Set initial state")
        self.submit_button.clicked.connect(self.submit_input)
        layout.addWidget(self.submit_button, len(self.labels), 0, 1, 2)

        self.setLayout(layout)

    def submit_input(self):
        initial_state = {key: None if (len(value.text()) == 0 or not is_number(value.text())) else float(value.text()) for key, value in self.inputs.items()}
        print("---- INPUT DATA ----:\n", initial_state)
        self.input_submitted.emit(initial_state)
        self.accept()


class PlotWidget(qtw.QWidget):
    def __init__(self, initial_state):
        super().__init__()

        self.figure = Main.gui(self, initial_state)
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