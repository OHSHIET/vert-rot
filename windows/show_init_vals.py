import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import Qt

from globals import Global

class InitialValuesWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Initial state")
        #self.setGeometry(300, 300, 400, 300)

        self.GV = Global

        # set window in center
        parent_rect = parent.geometry()
        self.move(
            parent_rect.center().x() - self.rect().center().x(),
            parent_rect.center().y() - self.rect().center().y()
        )

        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        layout = qtw.QVBoxLayout(central_widget)

        # if the table has already been populated once, store it in the memory and use it from there
        self.table = self.GV.init_vals_table
        if self.table == None:
            self.table = qtw.QTableWidget()
            self.table.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
            self.table.setColumnCount(2) # variable and initial value of that variable
            self.table.setHorizontalHeaderLabels(["Variable", "Initial value"])

            self.populate_table()

        layout.addWidget(self.table, alignment=Qt.AlignCenter)

    def populate_table(self):
        self.table.clearContents()
        initial_state = self.GV.initial_state

        # also change the dict in init_input when adding new measurements
        # make this more convenient to change
        readable_measurement = {
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

        self.table.setRowCount(len(initial_state))
        row = 0
        for key, value in initial_state.items():

            self.table.setItem(row, 0, qtw.QTableWidgetItem(key))
            inputted_value = value['inputted']
            table_cell_val = str(inputted_value)
            if not isinstance(inputted_value, str):
                readable_unit = readable_measurement[str(inputted_value.units)]
                table_cell_val = f"{inputted_value.magnitude} {readable_unit}"
            self.table.setItem(row, 1, qtw.QTableWidgetItem(table_cell_val))
            row += 1

        self.table.resizeColumnsToContents()
        self.table.setSizePolicy(
            self.table.sizePolicy().horizontalPolicy(),
            self.table.sizePolicy().verticalPolicy()
        )

        self.GV.init_vals_table = self.table
