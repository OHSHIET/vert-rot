import PyQt5.QtWidgets as qtw
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PlotWindow(qtw.QMainWindow):
    def __init__(self, ax, parent=None):
        super().__init__(parent)

        title = ax.get_title()
        axlines = ax.get_lines()[0]

        self.setWindowTitle(f'Plot: {title}')

        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        layout = qtw.QVBoxLayout(central_widget)

        figure = plt.figure()
        new_ax = figure.add_subplot(1, 1, 1)
        new_ax.plot(axlines.get_xdata(), axlines.get_ydata(), color=axlines.get_color())
        new_ax.set_title(title)
        new_ax.set_xlabel(ax.get_xlabel())
        new_ax.set_ylabel(ax.get_ylabel())

        layout.addWidget(FigureCanvas(figure))

    def closeEvent(self, event):
        """
            cleanup the plot from memory on close
        """
        plt.close()