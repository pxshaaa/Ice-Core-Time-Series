# Teddy Tonin, Pasha Alidadi

import io
from PyQt5.QtWidgets import QWidget,  QLabel, QTableView,QHBoxLayout ,QVBoxLayout,  QComboBox
from PyQt5 import  QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from data import read_data

class DataFrameModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[section])
        return None


class DataWidget(QWidget):
    def __init__(self, df):
        super().__init__()
        self.table = QTableView()
        self.model = DataFrameModel(df)
        self.table.setModel(self.model)

        # Add label to show dataframe info
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        buf = io.StringIO()
        df.info(buf=buf)
        self.info_label.setText(buf.getvalue())

        # create a vertical layout for the widget and add the table view and info label to it
        
        hlayout = QHBoxLayout(self)
        hlayout.addWidget(self.info_label)
        hlayout.addWidget(self.table)
        

        
def load_file(filepath):
    df = read_data(filepath)
    return df


def load_file_on_widget(dataframes,filepaths):
    Data = Choose_Data_Widget(dataframes,filepaths)
    return Data


def file_save(self):
    pass


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
    
    def push_choice_file(self,file):
        print('pushing choice')
        self.dataframe_to_display = file
        self.datawidget = DataWidget(self.dfs[self.dataframe_to_display])
        self.data_window = DataWindow()
        self.data_window.setCentralWidget(self.datawidget)
        self.data_window.show()
        
    
class   DataWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnalySeries")
