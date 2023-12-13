from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout, QVBoxLayout, QFileDialog, QApplication
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib

import numpy as np
import pandas as pd
from scipy import stats
# Assuming these functions are in prepare_linage.py
from prepare_linage import get_data_ready_for_linage
# Import your custom functions from the uploaded files
from Data import *
from File import *

# Plotting graph with matplotlib
matplotlib.use('Qt5Agg')

class PlotGraph(QWidget):
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
        self.fileComboBox.addItem("Select a file...")
        self.fileComboBox.addItems(self.filepaths)
        self.fileComboBox.currentIndexChanged.connect(self.onFileSelected)

        self.variableComboBox = QComboBox()

        self.plotButton = QPushButton("Plot Histogram")
        self.plotButton.clicked.connect(self.plotHistogram)
        self.plotButton.setEnabled(False)

        layout.addWidget(self.fileComboBox)
        layout.addWidget(self.variableComboBox)
        layout.addWidget(self.plotButton)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def onFileSelected(self, index):
        if index > 0:
            filepath = self.filepaths[index - 1]
            self.current_dataframe = self.dataframes[filepath]
            self.updateVariableComboBox()

    def updateVariableComboBox(self):
        if self.current_dataframe is not None:
            self.variableComboBox.clear()
            self.variableComboBox.addItems(self.current_dataframe.columns)
            self.plotButton.setEnabled(True)

    def plotHistogram(self):
        variable = self.variableComboBox.currentText()

        if variable and self.current_dataframe is not None:
            data = self.current_dataframe[variable].dropna()

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.hist(data, bins=30, density=True, alpha=0.7, color='b')
            ax.set_xlabel(variable)
            ax.set_ylabel('Probability Density')
            ax.set_title(f'PDF Histogram of {variable}')

            self.canvas.draw()