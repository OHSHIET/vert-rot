import sys
import json
from datetime import datetime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import PyQt5.QtWidgets as qtw

from graphs.eq_VerticalROTnoForces import Main
from windows.init_input import InputDialog
from windows.show_init_vals import InitialValuesWindow
from globals import Global

class PlotWidget(qtw.QWidget):
    def __init__(self):
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

        # buttons layout
        buttons_layout = qtw.QGridLayout()

        save_initial_state_button = qtw.QPushButton("Save initial state")
        save_initial_state_button.clicked.connect(self.save_initial_state)
        buttons_layout.addWidget(save_initial_state_button, 0, 0)

        show_initial_state_button = qtw.QPushButton("Show initial state")
        show_initial_state_button.clicked.connect(self.show_initial_state)
        buttons_layout.addWidget(show_initial_state_button, 0, 1)

        # add buttons and graphs to the main layout
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(plot_widget)

    def save_initial_state(self):
        for key, value in initial_state.items():
            val = value['inputted']
            G.savedata['data'][key] = val if isinstance(val, str) else val.magnitude

        G.savedata['measurements']['length'] = str(G.current_length)
        G.savedata['measurements']['mass'] = str(G.current_mass)
        G.savedata['time_saved'] = str(datetime.now())

        file_path, _ = qtw.QFileDialog.getSaveFileName(self, "Save your initial state", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "w") as file:
                json.dump(G.savedata, file, indent=4)
            
        G.savedata['data'] = { }

    def show_initial_state(self):
        self.new_window = InitialValuesWindow(self)
        self.new_window.show()

    def closeEvent(self, event):
        """
            finish the program if user closes the window
        """
        sys.exit()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    G = Global
    input_dialog = InputDialog()

    initial_state = {}
    input_dialog.input_submitted.connect(lambda data: setattr(sys.modules[__name__], 'initial_state', G.handle_initial_data(data)))
    input_dialog.exec_()

    plot_widget = PlotWidget()
    main_window = MainWindow(plot_widget)

    main_window.show()
    sys.exit(app.exec_())