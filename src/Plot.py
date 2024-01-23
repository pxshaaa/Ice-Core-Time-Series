# Linn Habberstad

import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox,QPushButton
from PyQt5 import QtCore


####################### CHOOSE THE COLUMN TO PLOT GRAPH #######################

class Graph(QWidget):
    """Widget to open the graph + its buttons with csv data"""

    def __init__(self, dataframe):
        super().__init__()
        self.labelx = QLabel("No x-data chosen")
        self.labely = QLabel("No y-data chosen")
        self.df = dataframe  # data as a dataframe
        self.w = None  #### new window for the graph
        self.graph_windows = []  # List to keep track of graph windows

    # Activation of mouse tracking
        self.setMouseTracking(True)

    # Data to plot the graph. Originally None, when nothing is chosen.

        self.x = None
        self.y = None
        self.x_values = None
        self.y_values = None

    # Drop-down menu to choose x & y-axis data according to the value in the input data
        self.choix_x = QLabel("Choose x-data")
        combobox_abs = QComboBox()
        combobox_abs.addItem('Choose')
        combobox_abs.addItems(self.df.columns)

        self.choix_y = QLabel("Choose y-data")
        combobox_ord = QComboBox()
        combobox_ord.addItem('choose')
        combobox_ord.addItems(self.df.columns)

        combobox_abs.currentTextChanged.connect(self.push_choice_x)
        combobox_ord.currentTextChanged.connect(self.push_choice_y)


    # Create a QPushButton to perform the action
        self.perform_action_button = QPushButton("Visualisez")
        self.perform_action_button.clicked.connect(self.perform_action)

    # Window layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.choix_x)
        layout.addWidget(combobox_abs)
        layout.addWidget(self.labelx)
        layout.addWidget(self.choix_y)
        layout.addWidget(combobox_ord)
        layout.addWidget(self.labely)

        # Set spacing between widgets
        layout.setSpacing(15)  # You can adjust the value as needed

        layout.addStretch(1)
        layout.addWidget(self.perform_action_button)

        # Center the layout
        layout.setAlignment(QtCore.Qt.AlignCenter)


    #  Choice of data for x and y-axis, 
    # let's remember to use this code to extract the column's names to display the dataframe

     # Simplified method to handle x-axis choice
    def push_choice_x(self, index):
        if index in self.df.columns:
            self.x = index
            self.x_values = list(self.df[index])
            self.labelx.setText(f"x-data: {index}")


    # Simplified method to handle y-axis choice
    def push_choice_y(self, index):
        if index in self.df.columns:
            self.y = index
            self.y_values = list(self.df[index])
            self.labely.setText(f"y-data: {index}")


    def graphe(self): #edited by Pasha
        if self.x is not None and self.y is not None:
            # Create a new graph window and add it to the list
            graph_window = Fenetre_graphe(self.x_values, self.y_values, self.x, self.y)
            self.graph_windows.append(graph_window)
            graph_window.show()
    
        
    def perform_action(self):
        self.graphe()

class Choose_Data_Widget(QWidget):
    """Widget to open the graph + its buttons with csv data"""

    def __init__(self, dataframes, filepaths):
        super().__init__()
        self.files = filepaths # list  of files opened by the user
        self.dfs = dataframes  # list of dataframes
        self.w = None  #### new window for the graph

    # Activation of mouse tracking
        self.setMouseTracking(True)

    # Data to display Originally None, when nothing is chosen.

        self.dataframe_to_display = None
    # command to isplay the data

        self.data_window = None

    # Drop-down menu to choose file according to the value in the filepaths list
        self.choice_file = QLabel("Choose file")
        combobox_file = QComboBox()
        combobox_file.addItem('Choose')
        combobox_file.addItems(self.files)


        combobox_file.currentTextChanged.connect(self.push_choice_file)



    # Window layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.choice_file)
        layout.addWidget(combobox_file)
        self.layout = layout
    
        layout.setSpacing(20)  # You can adjust the value as needed

        # Center the layout
        layout.setAlignment(QtCore.Qt.AlignCenter)

    def push_choice_file(self,file):
        print('pushing choice')
        self.dataframe_to_display = file
        self.layout.addWidget(Graph(self.dfs[self.dataframe_to_display]))





class Fenetre_graphe(QtWidgets.QMainWindow):
    """Creates a pyQt graph (not a matplotlib one, unlike in Linage"""

    def __init__(self, x, y, abs, ord, title="Visualisation"):
        super(Fenetre_graphe, self).__init__()
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground((255, 255, 255))
        pen = pg.mkPen(color=(255, 0, 0), width=5)
        self.graphWidget.setLabel('left', ord)
        self.graphWidget.setLabel('bottom', abs)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.plot(x, y, pen=pen)

        self.setWindowTitle("AnalySerie - " + title)
        self.setMouseTracking(True)
        self.isClosed = False  # Add a flag to track if the window is closed

    def update_graph(self, x, y, abs, ord):
        # Clear the current graph
        self.graphWidget.clear()

        # Update the graph with new data
        pen = pg.mkPen(color=(255, 0, 0), width=5)
        self.graphWidget.setLabel('left', ord)
        self.graphWidget.setLabel('bottom', abs)
        self.graphWidget.plot(x, y, pen=pen)

    def closeEvent(self, event):
        self.isClosed = True  # Update the flag when the window is closed
        super(Fenetre_graphe, self).closeEvent(event)

def plot_widget(dataframes,filepaths):
    Data = Choose_Data_Widget(dataframes,filepaths)
    return Data

        