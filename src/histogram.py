# Pasha Alidadi

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

# Assuming these functions are in prepare_linage.py
# Import your custom functions from the uploaded files

from data import *
from file import *

# Plotting graph with matplotlib
matplotlib.use('Qt5Agg')

class HistogramPlotGraph(QWidget):
    def __init__(self, filepaths, dataframes, parent=None):
        super().__init__(parent)
        self.filepaths = filepaths
        self.dataframes = {fp: df for fp, df in zip(filepaths, dataframes)}

        self.current_dataframe = None
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        self.fileComboBox = QComboBox()
        self.fileComboBox.addItem("Select a file for X...")
        self.fileComboBox.addItems(self.filepaths)
        self.fileComboBox.currentIndexChanged.connect(lambda: self.onFileSelected('x'))

        self.variableComboBox = QComboBox()

        self.plotTypeComboBox = QComboBox()
        self.plotTypeComboBox.addItems(["PDF", "Cumulative", "Specific Values"])

        self.plotButton = QPushButton("Plot Histogram")
        self.plotButton.clicked.connect(self.plotHistogram)
        self.plotButton.setEnabled(False)

        layout.addWidget(self.fileComboBox)
        layout.addWidget(self.variableComboBox)
        layout.addWidget(self.plotTypeComboBox)
        layout.addWidget(self.plotButton)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        if self.filepaths:
            self.fileComboBox.setCurrentIndex(1)

    def onFileSelected(self, axis):
        index = self.fileComboBox.currentIndex() - 1
        if index >= 0 and index < len(self.filepaths):
            filepath = self.filepaths[index]
            self.current_dataframe = self.dataframes[filepath]
            self.updateVariableComboBox()

    def updateVariableComboBox(self):
        if self.current_dataframe is not None:
            self.variableComboBox.clear()
            self.variableComboBox.addItems(self.current_dataframe.columns)
            self.plotButton.setEnabled(True)

    def plotHistogram(self):
        variable = self.variableComboBox.currentText()
        plot_type = self.plotTypeComboBox.currentText()

        if variable and self.current_dataframe is not None:
            data = self.current_dataframe[variable].dropna()

            self.figure.clear()
            ax = self.figure.add_subplot(111)

            if plot_type == "PDF":
                ax.hist(data, bins=30, density=True, alpha=0.7, color='b')
                ax.set_ylabel('Probability Density')
            elif plot_type == "Cumulative":
                ax.hist(data, bins=30, density=True, alpha=0.7, color='b', cumulative=True)
                ax.set_ylabel('Cumulative Probability')
            elif plot_type == "Specific Values":
                # For specific values, you might want to plot a bar chart or similar
                # This part depends on how you want to represent specific values
                # For example, here's a simple bar plot of value counts
                value_counts = data.value_counts()
                ax.bar(value_counts.index, value_counts.values)
                ax.set_ylabel('Counts')

            ax.set_xlabel(variable)
            ax.set_title(f'{plot_type} Histogram of {variable}')

            self.canvas.draw()