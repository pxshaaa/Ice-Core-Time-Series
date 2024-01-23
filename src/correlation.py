# Pasha Alidadi

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import numpy as np

# Assuming these functions are in prepare_linage.py
# Import your custom functions from the uploaded files
from data import *
from file import *

# Plotting graph with matplotlib
matplotlib.use('Qt5Agg')

class CorrelationPlotGraph(QtWidgets.QWidget):
    def __init__(self, filepaths, dataframes, parent=None):
        super().__init__(parent)
        self.filepaths = filepaths
        self.dataframes = {fp: df for fp, df in zip(filepaths, dataframes)}

        self.current_dataframe = None

        # Additional attributes for the second file selection
        self.current_dataframe2 = None
        self.yFilePath = None  # To track the file path for the Y-axis variable

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.subplot_axes = []  # List to keep track of subplot axes
        self.max_plots = 4      # Maximum number of plots to display

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        # File selection ComboBox for X-axis variable
        self.fileComboBox = QComboBox()
        self.fileComboBox.addItem("Select a file for X...")
        self.fileComboBox.addItems(self.filepaths)
        self.fileComboBox.currentIndexChanged.connect(lambda: self.onFileSelected('x'))

        # File selection ComboBox for Y-axis variable
        self.fileComboBox2 = QComboBox()
        self.fileComboBox2.addItem("Select a file for Y...")
        self.fileComboBox2.addItems(self.filepaths)
        self.fileComboBox2.currentIndexChanged.connect(lambda: self.onFileSelected('y'))

        # Data selection ComboBoxes
        self.xComboBox = QComboBox()
        self.yComboBox = QComboBox()

        self.plotButton = QPushButton("Plot and Calculate Correlation")
        self.plotButton.clicked.connect(self.plotAndCalculateCorrelation)
        self.plotButton.setEnabled(False)

        layout.addWidget(self.fileComboBox)
        layout.addWidget(self.xComboBox)
        layout.addWidget(self.fileComboBox2)
        layout.addWidget(self.yComboBox)
        layout.addWidget(self.plotButton)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        if self.filepaths:
            # Initialize both ComboBoxes with the first file
            self.fileComboBox.setCurrentIndex(1)
            self.fileComboBox2.setCurrentIndex(1)

    def onFileSelected(self, axis):
        index = self.fileComboBox.currentIndex() - 1 if axis == 'x' else self.fileComboBox2.currentIndex() - 1
        if index >= 0 and index < len(self.filepaths):
            filepath = self.filepaths[index]
            if axis == 'x':
                self.current_dataframe = self.dataframes[filepath]
                self.updateDataUI('x')
            else:
                self.current_dataframe2 = self.dataframes[filepath]
                self.updateDataUI('y')

    def updateDataUI(self, axis):
        if axis == 'x' and self.current_dataframe is not None:
            self.xComboBox.clear()
            self.xComboBox.addItems(self.current_dataframe.columns)
        elif axis == 'y' and self.current_dataframe2 is not None:
            self.yComboBox.clear()
            self.yComboBox.addItems(self.current_dataframe2.columns)
        self.plotButton.setEnabled(self.xComboBox.count() > 0 and self.yComboBox.count() > 0)

    def plotAndCalculateCorrelation(self):
        x_var = self.xComboBox.currentText()
        y_var = self.yComboBox.currentText()

        if x_var and y_var and self.current_dataframe is not None and self.current_dataframe2 is not None:
            x_ref, y_ref = get_data_ready_for_linage(self.current_dataframe, x_var, self.current_dataframe2, y_var)

            if x_ref is not None and y_ref is not None:
                # Check if maximum number of plots reached
                if len(self.subplot_axes) >= self.max_plots:
                    # Clear the figure and reset subplot axes list
                    self.figure.clear()
                    self.subplot_axes = []

                # Add new plot
                ax_new = self.figure.add_subplot(2, 2, len(self.subplot_axes) + 1)
                ax_new.scatter(x_ref, y_ref, c='b', marker='o', label='Dataset')
                ax_new.set_xlabel(x_var)
                ax_new.set_ylabel(y_var)
                ax_new.legend()

                # Annotate with the correlation coefficient
                correlation = np.corrcoef(x_ref, y_ref)[0, 1]
                ax_new.annotate(f'Correlation: {correlation:.2f}', xy=(0.5, 1), xycoords='axes fraction', ha='center')

                self.subplot_axes.append(ax_new)
                self.canvas.draw()

# Modify the get_data_ready_for_linage function for two variables, this can be used here as well for the correlation function
def get_data_ready_for_linage(data_array1, col1, data_array2, col2): 
    '''This function handles data from different sources and aligns them by length after removing NaN values'''

    x_ref = data_array1[col1].dropna().to_numpy()
    y_ref = data_array2[col2].dropna().to_numpy()

    # Truncate the longer array to match the length of the shorter one
    min_length = min(len(x_ref), len(y_ref))
    x_ref = x_ref[:min_length]
    y_ref = y_ref[:min_length]

    return x_ref, y_ref