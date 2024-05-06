import sys

import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot

from graphs.eq_VerticalROTnoForces import Graphs
from windows.init_input import InputDialog
from windows.init_vals import InitialValuesWindow

from globals import Global
from global_g import global_app

class Sidebar(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.sidebar_width_percent = 0.4

        self.figure = Graphs(G.initial_state)
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(self.figure)
        self.setLayout(layout)

    def update_graphs(self, initial_values):
        """
            update the graphs when user updates the initial values
        """
        # calls the whole file again to redraw
        self.figure = Graphs(initial_values)
        layout = self.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        layout.addWidget(self.figure)

    def get_width_percent(self):
        return self.sidebar_width_percent

class MainWindow(qtw.QMainWindow):
    @pyqtSlot(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Plot Layout")

        # window position and size
        self.setGeometry(100, 100, 800, 800)

        self.sidebar = Sidebar()

        # main layout
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = qtw.QHBoxLayout()
        central_widget.setLayout(main_layout)

        # view initial state
        initial_state_button = qtw.QPushButton("Initial state")
        initial_state_button.clicked.connect(self.show_initial_state)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(initial_state_button)

        self.input_layout = InitialValuesWindow.get_instance(self)
        self.input_layout.initial_values_updated.connect(self.sidebar.update_graphs)

    def show_initial_state(self):
        new_window = InitialValuesWindow.get_instance(self)
        new_window.show()

    def resizeEvent(self, event):
        """
            resize the sidebar:
            * on init
            * recalculate when user resizes the window
        """
        window_width = self.width()
        sidebar_width = window_width * self.sidebar.get_width_percent()

        self.sidebar.setFixedWidth(int(sidebar_width))

        super().resizeEvent(event)

    def closeEvent(self, event):
        """
            finish the program if user closes the window
        """
        sys.exit()


if __name__ == '__main__':
    app = global_app
    G = Global
    input_dialog = InputDialog()

    input_dialog.input_submitted.connect(lambda data: setattr(sys.modules[__name__], 'G.initial_state', G.handle_initial_data(data)))
    input_dialog.exec_()

    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())