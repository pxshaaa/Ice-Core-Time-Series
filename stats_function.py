from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout, QVBoxLayout,
    QFileDialog, QApplication, QWidget, QTableWidget, QTableWidgetItem
)
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib

import numpy as np
import pandas as pd
from scipy import stats

# Import your custom functions from the uploaded files
from Data import *
from File import *

# Plotting graph with matplotlib
matplotlib.use('Qt5Agg')

class DescriptiveStatistics(QWidget):
    def __init__(self, filepaths, dataframes, parent=None):
        super().__init__(parent)
        self.filepaths = filepaths
        self.dataframes = {fp: df for fp, df in zip(filepaths, dataframes)}

        self.current_dataframe = None

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        self.fileComboBox = QComboBox()
        self.fileComboBox.addItem("Select a file...")
        self.fileComboBox.addItems(self.filepaths)
        self.fileComboBox.currentIndexChanged.connect(self.onFileSelected)

        self.variableComboBox = QComboBox()

        self.calculateButton = QPushButton("Calculate Descriptive Statistics")
        self.calculateButton.clicked.connect(self.calculateStatistics)
        self.calculateButton.setEnabled(False)

        self.resultTable = QTableWidget()
        self.resultTable.setRowCount(1)  # One row for the results
        self.resultTable.setColumnCount(9)  # Nine columns for different statistics
        self.resultTable.setHorizontalHeaderLabels(["Statistic", "Value"])
        self.resultTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.resultTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.resultTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        layout.addWidget(self.fileComboBox)
        layout.addWidget(self.variableComboBox)
        layout.addWidget(self.calculateButton)
        layout.addWidget(self.resultTable)

        self.setLayout(layout)

        if self.filepaths:
            self.fileComboBox.setCurrentIndex(0)

    def onFileSelected(self):
        index = self.fileComboBox.currentIndex()
        if index >= 0 and index < len(self.filepaths):
            filepath = self.filepaths[index]
            self.current_dataframe = self.dataframes[filepath]
            self.updateVariableComboBox()

    def updateVariableComboBox(self):
        if self.current_dataframe is not None:
            self.variableComboBox.clear()
            self.variableComboBox.addItems(self.current_dataframe.columns)
            self.calculateButton.setEnabled(True)

    def calculateStatistics(self):
        variable = self.variableComboBox.currentText()

        if variable and self.current_dataframe is not None:
            data = self.current_dataframe[variable].dropna()

            mean = data.mean()
            variance = data.var()
            mode = data.mode().values[0]
            median = data.median()
            pearson_coefficient = stats.pearsonr(data, data)[0]
            std_deviation = data.std()
            data_range = data.max() - data.min()
            skewness = data.skew()
            kurtosis = data.kurtosis()
            iqr = data.quantile(0.75) - data.quantile(0.25)
            cv = (std_deviation / mean) * 100  # Coefficient of Variation

            # Update the table with statistics
            self.resultTable.setItem(0, 0, QTableWidgetItem("Mean"))
            self.resultTable.setItem(0, 1, QTableWidgetItem(str(mean)))
            self.resultTable.setItem(0, 2, QTableWidgetItem("Variance"))
            self.resultTable.setItem(0, 3, QTableWidgetItem(str(variance)))
            self.resultTable.setItem(0, 4, QTableWidgetItem("Mode"))
            self.resultTable.setItem(0, 5, QTableWidgetItem(str(mode)))
            self.resultTable.setItem(0, 6, QTableWidgetItem("Median"))
            self.resultTable.setItem(0, 7, QTableWidgetItem(str(median)))
            self.resultTable.setItem(0, 8, QTableWidgetItem("Pearson Coefficient"))
            self.resultTable.setItem(1, 0, QTableWidgetItem(str(pearson_coefficient)))
            self.resultTable.setItem(1, 1, QTableWidgetItem("Standard Deviation"))
            self.resultTable.setItem(1, 2, QTableWidgetItem(str(std_deviation)))
            self.resultTable.setItem(1, 3, QTableWidgetItem("Range"))
            self.resultTable.setItem(1, 4, QTableWidgetItem(str(data_range)))
            self.resultTable.setItem(1, 5, QTableWidgetItem("Skewness"))
            self.resultTable.setItem(1, 6, QTableWidgetItem(str(skewness)))
            self.resultTable.setItem(1, 7, QTableWidgetItem("Kurtosis"))
            self.resultTable.setItem(1, 8, QTableWidgetItem(str(kurtosis)))
            self.resultTable.setItem(2, 0, QTableWidgetItem("Interquartile Range (IQR)"))
            self.resultTable.setItem(2, 1, QTableWidgetItem(str(iqr)))
            self.resultTable.setItem(2, 2, QTableWidgetItem("Coefficient of Variation (CV)"))
            self.resultTable.setItem(2, 3, QTableWidgetItem(str(cv)))

# Assuming these functions are in prepare_linage.py
from prepare_linage import get_data_ready_for_linage