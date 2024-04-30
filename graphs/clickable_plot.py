import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from windows.plot_window import PlotWindow

class ClickablePlot(FigureCanvas):
    def __init__(self):
        """
            initialize grid
        """
        self.fig = plt.figure()
        self.axes = []
        # 8x2 grid of plots
        self.rows = 8
        self.cols = 2
        self.fig.canvas.mpl_connect('button_press_event', lambda event: self.on_click(event))
        super().__init__(self.fig)

    def new_plot(self, coords, time, firstPlot, secondPlot, ylabel, title):
        """
            add new plot to the grid
        """
        super().__init__(self.fig)

        ax = self.fig.add_subplot(self.rows, self.cols, coords[0] * self.cols + coords[1] + 1)
        ax.plot(time, firstPlot, 'r')
        if(secondPlot is not None):
            ax.plot(time, secondPlot, 'g')
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Time, s")
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        self.axes.append(ax)

    def apply_settings(self):
        plt.grid(True, linestyle='-', color='0.75')
        plt.tight_layout()
    
    def get_fig(self):
        return self.fig
    
    def on_click(self, event):
        for ax in self.axes:
            if ax.contains(event)[0]:
                plot_window = PlotWindow(ax, self)
                plot_window.show()
                break