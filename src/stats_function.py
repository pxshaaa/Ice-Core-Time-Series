# Pasha Alidadi

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore, QtWidgets


import matplotlib
import numpy as np
from scipy import stats

# Import your custom functions from the uploaded files
from data import *
from file import *

# Plotting graph with matplotlib
matplotlib.use('Qt5Agg')

class StatsPlotGraph(QWidget):
    def __init__(self, filepaths, dataframes, parent=None):
        super().__init__(parent)
        self.filepaths = filepaths
        self.dataframes = {fp: df for fp, df in zip(filepaths, dataframes)}

        self.current_dataframe = None
        self.selected_variables = []

        self.setupUI()
        self.updateVariableComboBoxes()

    def setupUI(self):
        layout = QVBoxLayout()

        self.fileComboBox = QComboBox()
        self.fileComboBox.addItem("Select a file...")
        self.fileComboBox.addItems(self.filepaths)
        self.fileComboBox.currentIndexChanged.connect(self.onFileSelected)
        self.variableComboBox1 = QComboBox()
        self.variableComboBox2 = QComboBox()

        self.calculateButton = QPushButton("Calculate Descriptive Statistics")
        self.calculateButton.clicked.connect(self.calculateStatistics)
        self.calculateButton.setEnabled(False)

        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(9)  # Adjusted number of columns
        self.resultTable.setHorizontalHeaderLabels(
            ["Variable", "Mean", "Variance", "Mode", "Median", 
             "Pearson Coefficient", "P-value (Pearson)", 
             "Spearman Coefficient", "P-value (Spearman)"]
        )
        self.resultTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.resultTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.fileComboBox)
        layout.addWidget(self.variableComboBox1)
        layout.addWidget(self.variableComboBox2)
        layout.addWidget(self.calculateButton)
        layout.addWidget(self.resultTable)

        self.setLayout(layout)

        if self.filepaths:
            self.fileComboBox.setCurrentIndex(0)

    def onFileSelected(self):
        index = self.fileComboBox.currentIndex()
        if index > 0:
            filepath = self.filepaths[index - 1]
            self.current_dataframe = self.dataframes[filepath]
            self.updateVariableComboBoxes()

    def updateVariableComboBoxes(self):
        if self.current_dataframe is not None:
            self.variableComboBox1.clear()
            self.variableComboBox2.clear()
            self.variableComboBox1.addItems(self.current_dataframe.columns)
            self.variableComboBox2.addItems(self.current_dataframe.columns)
            self.calculateButton.setEnabled(True)
        else:
            self.calculateButton.setEnabled(False)

    def calculateStatistics(self):
        self.selected_variables = [self.variableComboBox1.currentText(), self.variableComboBox2.currentText()]
        self.resultTable.setRowCount(len(self.selected_variables))

        if len(self.selected_variables) == 2:
            data1 = self.current_dataframe[self.selected_variables[0]].dropna()
            data2 = self.current_dataframe[self.selected_variables[1]].dropna()
            pearson_coefficient, pearson_p_value = stats.pearsonr(data1, data2)
            spearman_coefficient, spearman_p_value = stats.spearmanr(data1, data2)

            for i, variable in enumerate(self.selected_variables):
                self.calculateAndDisplayStatsForRow(variable, i, pearson_coefficient, pearson_p_value, spearman_coefficient, spearman_p_value)

    def calculateAndDisplayStatsForRow(self, variable, row, pearson_coefficient=None, pearson_p_value=None, spearman_coefficient=None, spearman_p_value=None):
        data = self.current_dataframe[variable].dropna()

        # Define the statistics functions
        stats_funcs = {
            'mean': np.mean,
            'var': np.var,
            'mode': lambda x: stats.mode(x)[0][0] if len(stats.mode(x)[0]) > 0 else np.nan,
            'median': np.median,
        }

        self.resultTable.setItem(row, 0, QTableWidgetItem(variable))

        col_index = 1
        for key, func in stats_funcs.items():
            try:
                value = func(data)
                value_str = str(round(value, 4)) if not np.isnan(value) else 'NaN'
            except Exception as e:
                value_str = 'Error'
            self.resultTable.setItem(row, col_index, QTableWidgetItem(value_str))
            col_index += 1

        # Set Pearson and Spearman coefficients and their P-values
        self.resultTable.setItem(row, 5, QTableWidgetItem(str(round(pearson_coefficient, 4))))
        self.resultTable.setItem(row, 6, QTableWidgetItem(str(round(pearson_p_value, 4))))
        self.resultTable.setItem(row, 7, QTableWidgetItem(str(round(spearman_coefficient, 4))))
        self.resultTable.setItem(row, 8, QTableWidgetItem(str(round(spearman_p_value, 4))))
