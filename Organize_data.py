from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QLabel, QStyle,QComboBox,QDesktopWidget,QGroupBox, QGridLayout, QVBoxLayout, QLineEdit, QApplication,QPushButton,QWidget,QHBoxLayout,QVBoxLayout,QFrame,QTreeWidget, QTreeWidgetItem
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import ConnectionPatch
import matplotlib.pyplot as plt
import matplotlib

import numpy as np
import pandas as pd
from scipy import interpolate
import math

from pylab import rcParams


class WorkSheet(QtWidgets.QMainWindow):

    def __init__(self,dataframe, parent =None) -> None:
        super().__init__()
        self.df = dataframe
        self.columns = list(self.df)
        self.is_increasing = {}
        self.detect_monotony()

        self.setWindowTitle('Organize your Worksheet')
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2,
            self.width(),
            self.height()
        )

        self.setFixedSize(self.size())
        self.setWindowTitle('Organize your Worksheet')
        main_layout = QVBoxLayout()

        # create a frame to organize the worksheet
        self.dataBox = QFrame()
        self.dataBox.setFrameShape(QFrame.Box)
        self.dataBoxLayout = QVBoxLayout(self.dataBox)

        self.VBoxes = {}
        self.columnsnames ={}
        self.abcissas = {}
        monotonic = 0
        for i in range(len(self.columns)):
            self.VBoxes[self.columns[i]] = QHBoxLayout()
            self.VBoxes[self.columns[i]].addWidget(QLabel(f'{i+1}'))
            self.columnsnames[self.columns[i]]= QLineEdit()
            self.columnsnames[self.columns[i]].setText(self.columns[i])
            self.columnsnames[self.columns[i]].setFixedSize(self.columnsnames[self.columns[i]].sizeHint())
            self.VBoxes[self.columns[i]].addWidget(self.columnsnames[self.columns[i]])
            if self.is_increasing[self.columns[i]]:
                monotonic= i
                self.abcissas[self.columns[i]]= None
            else:
                self.chooseAbcissa = QLineEdit()
                self.abcissas[self.columns[i]] = self.columns[monotonic]
                self.chooseAbcissa.setText(self.columns[monotonic])
                self.VBoxes[self.columns[i]].addWidget(self.chooseAbcissa)

            self.dataBoxLayout.addLayout(self.VBoxes[self.columns[i]])

        main_layout.addWidget(self.dataBox)

        #add exit or cancel buttons
        cancelok = QHBoxLayout()
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close_window)
        cancel.setFixedSize(50, 25)
        ok = QPushButton('OK')
        ok.clicked.connect(self.displayWorksheet)
        ok.setFixedSize(50, 25)
        cancelok.addWidget(cancel)
        cancelok.addWidget(ok)

        main_layout.addLayout(cancelok)

        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()
    
    def close_window(self):
        self.close()
        
    def detect_monotony(self):
        for col in self.columns:
            cleaned_col = self.df[col].to_numpy()
            cleaned_col = cleaned_col[~np.isnan(cleaned_col)]
            if is_monotonic_increasing(cleaned_col):
                self.is_increasing[col]= True
            else:
                self.is_increasing[col]=False

    def displayWorksheet(self):
        self.worksheet = QtWidgets.QMainWindow()
        self.worksheet.setWindowTitle('Worksheet')

        
        central_widget = QtWidgets.QWidget(self.worksheet)
        self.worksheet.setCentralWidget(central_widget)
        self.worksheetlayout = QVBoxLayout(central_widget)
        


        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Series Name")
        
        
        self.worksheetlayout.addWidget(self.tree_widget)
        self.add_columns_to_tree()

        self.worksheet.show()
 

    def add_columns_to_tree(self):
        for column_name in self.columns:
            item = QTreeWidgetItem(self.tree_widget, [column_name])
            
            # Set icon based on whether it's a file or folder (you can customize the icons)
            if self.abcissas[column_name] is None:
                icon = self.style().standardIcon(QStyle.SP_DirIcon)
                item.setIcon(0, icon)
            else:
                icon = self.style().standardIcon(QStyle.SP_FileIcon)

                item.setIcon(0, icon)
                item.setText(0, ' ' * 10 + column_name+ ' '+ self.abcissas[column_name])


def is_monotonic_increasing(array):
    return np.all(np.diff(array) >= 0)
    


