import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import Qt

from globals import Global
from windows.global_windows import G_Windows

class InitialValuesWindow(qtw.QMainWindow):
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
        layout = qtw.QVBoxLayout(central_widget)

        # if the table has already been populated once, store it in the memory and use it from there
        self.table = self.G.init_vals_table
        if self.table == None:
            self.table = qtw.QTableWidget()
            self.table.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
            self.table.setColumnCount(2) # variable and initial value of that variable
            self.table.setHorizontalHeaderLabels(["Variable", "Initial value"])

            self.populate_table()

        layout.addWidget(self.table, alignment=Qt.AlignCenter)

    def populate_table(self):
        self.table.clearContents()
        initial_state = self.G.initial_state

        self.table.setRowCount(len(initial_state))
        row = 0
        for key, value in initial_state.items():

            self.table.setItem(row, 0, qtw.QTableWidgetItem(key))
            inputted_value = value['inputted']
            table_cell_val = str(inputted_value)
            if not isinstance(inputted_value, str):
                readable_unit = self.GW.READABLE_MEASUREMENT[str(inputted_value.units)]
                table_cell_val = f"{inputted_value.magnitude} {readable_unit}"
            self.table.setItem(row, 1, qtw.QTableWidgetItem(table_cell_val))
            row += 1

        self.table.resizeColumnsToContents()
        self.table.setSizePolicy(
            self.table.sizePolicy().horizontalPolicy(),
            self.table.sizePolicy().verticalPolicy()
        )

        self.G.init_vals_table = self.table
