# Teddy Tonin

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout, QVBoxLayout, QApplication,QPushButton,QWidget
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import ConnectionPatch
import matplotlib.pyplot as plt
import matplotlib

import numpy as np
from scipy import interpolate
import math

from pylab import rcParams

from prepare_linage import get_data_ready_for_linage, sort_with_indices
from data import titlecolumns

# Plotting graph with matplotlib
matplotlib.use('tkagg')
matplotlib.use('Qt5Agg')


class Click:

    def __init__(self, x, y, plotno):
        self._x = x
        self._y = y
        self._plotno = plotno


class PlotGraph(QtWidgets.QWidget):
    '''This is the Linage widget that will be merged with the Home window'''

    def __init__(self, data,organizer, parent=None):
        '''Data is the only argument of this function. The Linge will start running when data is uploaded on the software'''

        super().__init__(parent)
        self.organizer = organizer
        self.df = data
        self.columns = titlecolumns(self.df)

    # Intialize variables that will be used later

        self.linage_point_pairs = ['No pair added yet']
        self.linage_points_prep = ['No click yet', 'No click yet']

        # we initialize the choices of the user to None. ´Thoses variables will be updated when the user choose what he wants to plot

        self.abs_ref, self.abs_dis, self.ord_ref, self.ord_dis = None, None, None, None # the names of the columns inside the dataframe
        self.x_ref, self.y_ref, self.x_dis, self.y_dis = None, None, None, None # the x and y -data to start ploting
        self.pushed_data = {}
        self.titles = []

        self.clicks_dis= []
        self.clicks_ref= []
        # we initiale the list containing the correlation and overlapping windows

        self.switchButtons = {}
        self.correlation_window = None
        self.overlapping_windows = []
    
        # we initialize the two interpolation functions: f and its inverse

        self.f = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')
        self.g = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')


    # Widget Layout

        self.setMouseTracking(True)
        self.setGeometry(0, 0, 1500, 1000)


        # Link the different graphs to the figure canvas
        self.figure_left = plt.figure(tight_layout=True) 
        self.canvas_left = FigureCanvas(self.figure_left) # this graph plots sedimentation rate. it is implemented inside thefigure_left method

        self.figure_right = plt.figure(tight_layout=True)
        self.canvas_right = FigureCanvas(self.figure_right) # this one is to plot age scale
        self.figure_right.tight_layout(pad=100.0)
        # a third graph will be added after the method Linage is called. That one will be to plot reference and distorded

        # those 4 objects will be linked to the FigureCanvas just like the previous graphs. They will contain the menus to help the user choose
        self.topLeft()
        self.topRight()
        self.center()
        self.bottomRight()

        # This is to set the size of the 4 previous objects we will merge to the widget.
        self.mainLayout = QGridLayout()
        # First we define the grid in which the differents boxes of the windows will be casted
        grid = (
            (0, 0, 5, 3),
            (0, 3, 5, 1),
            (5, 0, 4, 4),
            (9, 0, 1, 4),
        )
        label = {
            0: self.topLeftBox,
            1: self.topRightBox,
            2: self.centerBox,
            3: self.bottomRightBox,
        }

        for i, (row, col, row_span, col_span) in enumerate(grid):
            self.mainLayout.addWidget(label[i], row, col, row_span, col_span)

        self.setLayout(self.mainLayout)

        QApplication.setStyle("Fusion")

    # Those are the commands that actually show all the graphs
        self.show()

    def plot_reference(self):
        '''creates the reference graph and add it to the figurecanvas'''

        self.ax1 = self.figure.add_subplot(211)

        # we only plot when the userboth x and y are chosen by 
        if (self.x_ref is not None) and (self.y_ref is not None):
            self.ax1.plot(self.x_ref, self.y_ref, color= 'g', linewidth=0.5)
            self.ax1.set_xlim([self.x_ref[0], self.x_ref[-1]])
            # labels only added if they exist
            if (self.abs_ref is not None) and (self.ord_ref is not None):
                self.ax1.set(xlabel=self.abs_ref, ylabel=self.ord_ref)
                self.ax1.legend()
            self.ax1.set_title('Reference', loc = 'right')

        self.plot_label_no = 10  # determines the number of labels of the X-Axes of the 

    def plot_distorded(self):
        '''Creates the graph to distord (lower graph)'''

        self.ax2 = self.figure.add_subplot(212)
        if (self.x_dis is not None) and (self.y_dis is not None):
            self.ax2.plot(self.f(self.x_dis), self.y_dis, color="r", linewidth=0.5)
            self.ax2.set_xlim([self.x_ref[0], self.x_ref[-1]])
           
            self.ax2.set_xticks(self.clicks_ref)
            self.ax2.set_xticklabels(np.round(self.clicks_dis))

            if (self.abs_dis is not None) and (self.ord_dis is not None):
                self.ax2.set(xlabel=self.abs_dis, ylabel=self.ord_dis)
                self.ax2.legend()
            self.ax2.set_title('Distorted', loc= 'left')
                
            

        new_ref_function = interpolate.interp1d(self.x_ref, self.y_ref
            , fill_value='extrapolate')
        new_dis_function = interpolate.interp1d(self.x_dis, self.y_dis
            , fill_value='extrapolate')
    
        
        qrows = len(self.linage_point_pairs)
        if not self.linage_point_pairs == ['No pair added yet']:
            for i in range(0,qrows): # à vectoriser
                con = ConnectionPatch(xyA=(self.clicks_ref[i],float(new_ref_function(self.clicks_ref[i])) ), xyB=(
                    self.clicks_ref[i], float(new_dis_function(self.g(self.clicks_ref[i])))), coordsA="data", coordsB="data", axesA=self.ax1, axesB=self.ax2, color='b')
                
                self.ax2.add_artist(con)
            




    # The 4 next functions are triggered when the user make his choices. The graph are ploted as a result

    def push_choice_x1(self, index):
        self.abs_ref = index
        xx = math.inf
        i = 0
        while (xx == math.inf) and i < len(list(self.columns)):
            if list(self.columns)[i] == index:
                xx = list(self.columns)[i]
            i += 1
        self.labelx1.setText("x-data: {}".format(index))

    def push_choice_y1(self, index):
        self.ord_ref = index
        yy = math.inf
        i = 0
        while (yy == math.inf) and i < len(list(self.columns)):
            if list(self.columns)[i] == index:
                yy = list(self.columns)[i]
            i += 1
        self.labely1.setText("y-data: {}".format(index))

    def push_choice_x2(self, index):
        self.abs_dis = index
        xx = math.inf
        i = 0
        while (xx == math.inf) and i < len(list(self.columns)):
            if list(self.columns)[i] == index:
                xx = list(self.columns)[i]
            i += 1
        self.labelx2.setText("x-data: {}".format(index))


    def push_choice_y2(self, index):
        self.ord_dis = index
        yy = math.inf
        i = 0
        while (yy == math.inf) and i < len(list(self.columns)):
            if list(self.columns)[i] == index:
                yy = list(self.columns)[i]
            i += 1
        self.labely2.setText("y-data: {}".format(index))

    def createswitchbutton(self, abs_ref, ord_ref, abs_dis, ord_dis):

        # create switch to button

        title = f"{self.ord_ref} {self.abs_ref} vs {self.ord_ref} {self.abs_dis}"
        self.switchbutton = QPushButton("Switch to  "+title)
        self.switchbutton.setMaximumWidth(len(title)*8)
        self.switchbutton.setMaximumHeight(40)
        self.switchbutton.clicked.connect(lambda: self.switch_action(abs_ref, ord_ref, abs_dis, ord_dis))
        return self.switchbutton
    
    def switch_action(self,abs_ref, ord_ref, abs_dis, ord_dis):
        self.abs_ref,self.ord_ref,self.ord_dis,self.ord_dis = abs_ref, ord_ref, abs_dis, ord_dis
        self.perform_plot_action()
        
        
    def perform_plot_action(self):

        if (self.abs_dis is not None) and (self.ord_dis is not None) and (self.ord_ref is not None) and (self.abs_ref is not None):

            # Creates a Figure object

                self.updatedData()
                title = f"{self.ord_ref} {self.abs_ref} vs {self.ord_ref} {self.abs_dis}"

                if title not in self.switchButtons:
                    self.switchButtons[title] = self.createswitchbutton(self.abs_ref,self.ord_ref,self.abs_dis,self.ord_dis)
                    self.overlapping_windows.append(self.draw_graphs_overlapped(self.abs_ref,self.ord_ref,self.abs_dis,self.ord_dis,
                                                                                  self.x_ref, self.y_ref, self.x_dis, self.y_dis))

        
                self.plot_reference()
                self.plot_distorded()

                self.start_linage()
                self.graph.draw()
                self.show()

                plt.close()


                if self.correlation_window is not None:
                    self.correlation_window.close()
                    self.correlation_window = self.Correlation_window()
                    self.correlation_window.show()
                else:
                    self.correlation_window = self.Correlation_window()
                    self.correlation_window.show()

                                    


    def updatedData(self):
        self.x_ref, self.y_ref, self.x_dis, self.y_dis = \
            get_data_ready_for_linage(
                self.df, self.abs_ref, self.ord_ref, self.abs_dis, self.ord_dis)
        title = f"{self.ord_ref} {self.abs_ref} vs {self.ord_ref} {self.abs_dis}"
        if title not in  self.pushed_data:
            self.pushed_data[title] =(self.abs_ref,self.ord_ref,self.abs_dis,self.ord_dis,self.x_ref, self.y_ref, self.x_dis, self.y_dis)
            self.titles.append(title)

    
        
        # Update the Figure object so it corresponds to the new data
        self.figure = Figure()
        self.figure.tight_layout()
        self.graph = FigureCanvas(self.figure) # The canvas is basically an object that allows you to draw.
                                                # We call it graph here because we are interested in drawing graphs
  
    def start_linage(self):
        '''Once the graphs are plotted, this function creates the pointers to allow the clicks'''

        self.ax1.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.ax2.figure.canvas.mpl_connect('button_press_event', self.onclick)
        print("Linage can start now. The user can click on the graphs")

        self.graph.draw()
        self.show()


# the serie of methods that follows creates the four objects that were linked to the Figure canvas earlier


    def center(self):
        '''
        Function that create the central - horizontal bar where the buttons to reset the plots,
        to change the plot of the overlapped graphs with the plot of the rate and the Comboboxes
        to change the axis of the graphs.
        '''

        self.centerBox = QGroupBox()

        self.reset = QPushButton('Reset')
        self.reset.setDisabled(True)
        self.reset.clicked.connect(self.reset_button_clicked)


        ####################

        self.labelx1 = QLabel("x-data: {}".format(self.abs_ref))
        self.labely1 = QLabel("y-data: {}".format(self.ord_ref))

        self.labelx2 = QLabel(str(self.abs_dis))
        self.labely2 = QLabel(str(self.ord_dis))

        self.graph1_txt = QLabel("First graph (Reference): ")
        self.graph2_txt = QLabel("Second graph (Distorted): ")

        # Menu to change x & y data for the first graph
        combobox_abs_ref = QComboBox()
        combobox_abs_ref.addItem("Change")
        combobox_abs_ref.addItems(self.columns)

        combobox_ord_ref = QComboBox()
        combobox_ord_ref.addItem('Change')
        combobox_ord_ref.addItems(self.columns)

        combobox_abs_ref.currentTextChanged.connect(self.push_choice_x1)
        combobox_ord_ref.currentTextChanged.connect(self.push_choice_y1)

        # Menu to choose x & y data for the second graph
        combobox_abs_dis = QComboBox()
        combobox_abs_dis.addItem('Choose')
        combobox_abs_dis.addItems(self.columns)

        combobox_ord_dis = QComboBox()
        combobox_ord_dis.addItem('Choose')
        combobox_ord_dis.addItems(self.columns)

        combobox_abs_dis.currentTextChanged.connect(self.push_choice_x2)
        combobox_ord_dis.currentTextChanged.connect(self.push_choice_y2)

        # Button to trigger the plottings
        self.perform_start_button = QPushButton("Start")
        self.perform_start_button.clicked.connect(self.perform_plot_action)

        #################

        # Create Layout
        layout = QGridLayout()
        #layout.addWidget(, 0, 0)
        layout.addWidget(self.reset, 1, 0)

        ############
        layout.addWidget(self.graph1_txt, 0, 1, QtCore.Qt.AlignRight)
        layout.addWidget(combobox_abs_ref, 0, 2)
        layout.addWidget(self.labelx1, 1, 2)
        layout.addWidget(combobox_ord_ref, 0, 3)
        layout.addWidget(self.labely1, 1, 3)
        layout.addWidget(self.graph2_txt, 0, 4, QtCore.Qt.AlignRight)
        layout.addWidget(combobox_abs_dis, 0, 5)
        layout.addWidget(self.labelx2, 1, 5)
        layout.addWidget(combobox_ord_dis, 0, 6)
        layout.addWidget(self.labely2, 1, 6)
        layout.addWidget(self.perform_start_button)

        ###################

        self.centerBox.setLayout(layout)

    def bottomRight(self):
        '''creates a Groupbox containing the Full button, and later the graph called self.figure to visualize
         the reference and the distorded data '''

        self.bottomRightBox = QGroupBox()  # "Bottom Right"

        # Create Layout
        layout = QVBoxLayout()
        self.savebutton = QPushButton('Save')
        self.savebutton.setDisabled(True)
        self.savebutton.clicked.connect(self.save)
    
        layout.addWidget(self.savebutton)

        # Add Layout to GroupBox
        self.bottomRightBox.setLayout(layout)
    
    def save(self):
        self.pointers = [self.clicks_ref,self.clicks_dis]
        self.organizer.add_Linage(self.pointers,self.g,self.derivative,self.overlapping_windows)
        return None
        

    def Correlation_window(self):
        dynamic_window = QtWidgets.QMainWindow()  # Create a new instance of QMainWindow
        dynamic_window.setWindowTitle('Correlation window')
        dynamic_window.setGeometry(100, 100, 400, 200)  # Set the position and size

        central_widget = QWidget(dynamic_window)  # Create a central widget
        dynamic_window.setCentralWidget(central_widget)  # Set it as the central widget

        layout = QVBoxLayout(central_widget)  # Use a QVBoxLayout for simplicity
        for button in self.switchButtons.values():
            layout.addWidget(button)


        layout.addWidget(self.graph)

        return dynamic_window


    def topLeft(self):
        '''creates a GroupBox and plots agescale ( self.canvas_left)'''

        self.topLeftBox = QGroupBox()  # "Bottom Left top")

        # Create Layout
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas_left)

        # Add Layout to GroupBox
        self.topLeftBox.setLayout(layout)

    def topRight(self):
        '''creates a GroupBox and plots sedimentation_rate ( self.canvas_right)'''

        self.topRightBox = QGroupBox()  # "Bottom Right top")

        # Create Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas_right)

        # Add Layout to GroupBox
        self.topRightBox.setLayout(layout)


    # Checking if the clicks are consistant
    
    def define_boundaries_for_next_click(self,x):
        '''this function calculates the two boundaries for the next click that will be made on the other graph'''
        self.min, self.max = -np.inf, np.inf
        if len(self.clicks_ref)>=2 and len(self.clicks_dis)>=2:
            for elt in self.clicks_ref:
                if elt<x and elt>self.min:
                    self.min=elt
                elif elt>x and elt<self.max:
                    self.max= elt

    def elligible_click(self,event):
        '''this function tells if the click made verifies the boundary conditions'''
        x_event = event.xdata
        return self.min<  x_event and x_event <self.max

    # Draw the markers on graph on click
    def onclick(self, event):

        x_event=event.xdata

        if event.inaxes in [self.ax1]:  # upper graph = reference graph'
            if len(self.clicks_ref)<len(self.clicks_dis):
                assert event.inaxes in [self.ax1]
                assert  self.elligible_click(event)
            self.ax1.plot(x_event, event.ydata,
                          '1', color="b", markersize=20)
            self.graph.draw()
            self.clicks_ref.append(x_event)
            self.click(event, plotno=0)
            if len(self.clicks_ref)>len(self.clicks_dis):
                self.define_boundaries_for_next_click(x_event)
    

        if event.inaxes in [self.ax2]:  # lower graph = distorted graph
            if len(self.clicks_ref)>len(self.clicks_dis):
                assert event.inaxes in [self.ax2]
                assert  self.elligible_click(event)
            self.ax2.plot(x_event, event.ydata,
                          '2', color="b", markersize=20)
            self.graph.draw()
            self.clicks_dis.append(x_event)
            self.click(event, plotno=1)
            if len(self.clicks_ref)<len(self.clicks_dis):
                self.define_boundaries_for_next_click(x_event)           


    def click(self, event, plotno):
        """ the click functions creates and summarizes the x,y and plotno and most importantly calls Linage."""

        self._plotno = plotno
        

        if self._plotno == 0:  # reference
            self._x = event.xdata
            idx = self.find_closest(self.x_ref, self._x)[0]
            self._y = self.y_ref[idx]

        # when the click is made on the distorded we have to find the original value in self.x_dis  
        if self._plotno == 1:  # distorded graph
            self._x = self.g(event.xdata) # remember, there is two x coordinate for any click in distorded. One from new_x_dis and the corresponding x_dis
            idx = self.find_closest(self.x_dis, self._x)[0]
            self._y = self.y_dis[idx]

        self.linage()   # linage is called  (even when one clik is made)


    ##### Begining of Linage ######
    def linage(self):

        # Clicks are added into linage_points_prep. If they occured in the upper
        # plot, they are saved in linage_points_prep[0] and if the occured in
        # the lower plot, they are saved in linage_points_prep[1]
        # the list is initialized as a two-size zero list
        self.linage_points_prep[self._plotno] = Click(self._x, self._y, self._plotno)

        # If linage_points_prep has a click saved in both spots
        # (linage_points_prep[0] and linage_points_prep[1]), they are carried
        # over into linage_point_pairs where all the clicks are saved. Not
        # just the new ones.
        # if Linage does work till the end, then both values of linage_points_prep must be initialized again to zero. see end of the function
        if self.linage_points_prep[0] != 'No click yet' and self.linage_points_prep[1] != 'No click yet':
            if self.linage_point_pairs[0] == 'No pair added yet':
                self.linage_point_pairs = self.linage_point_pairs[1:]
            self.linage_point_pairs.append(self.linage_points_prep[:])  # adds the new pair of clicks in the format [click1, click2]

            if len(self.linage_point_pairs) > 1:

                # the x coordinates are extracted
                self.clicks_ref = [i[0]._x for i in self.linage_point_pairs]
                self.clicks_dis = [i[1]._x for i in self.linage_point_pairs] 

                sorted_clicks_dis , indices = sort_with_indices(self.clicks_dis) 
                sorted_clicks_ref = [self.clicks_ref[i] for i in indices]

                # f is a function that maps from the reference graph to the
                # the distorted graph by using the clicks.
                self.f = interpolate.interp1d(
                    sorted_clicks_dis,sorted_clicks_ref, fill_value= 'extrapolate')  #  f is just the age-scale
                # g is the reciprocal function provided the clicks order is kept the same
                self.g = interpolate.interp1d(
                     sorted_clicks_ref,sorted_clicks_dis, fill_value= 'extrapolate')

                self.new_x_dis = self.f(self.x_dis)

                # Plotting new graphs with linage
                # reploting main window, with distorted graph
                self.figure.clear(True)
                self.figure_left.clear(True)
                self.figure_right.clear(True)

                self.ax1 = self.figure.add_subplot(211)
                self.ax1.plot(self.x_ref, self.y_ref, color='g', linewidth=0.5)
                self.ax1.set(xlabel=self.abs_ref, ylabel=self.ord_ref)

                self.ax1.set_xlim([self.x_ref[0], self.x_ref[-1]])

                self.ax2 = self.figure.add_subplot(212)
                self.ax2.plot(self.new_x_dis, self.y_dis,
                              color='r', linewidth=0.5)
                self.ax2.set(xlabel=self.abs_dis,
                             ylabel=self.ord_dis + 'Really_distorded')
            
                self.ax2.legend()
                self.ax2.set_xlim([self.x_ref[0], self.x_ref[-1]])

                self.ax2.set_xticks(self.clicks_ref)
                self.ax2.set_xticklabels(np.round(self.clicks_dis))


            
                # The following loop iterates through all the saved clicks
                # and draws the lines accordingly.
                new_ref_function = interpolate.interp1d(self.x_ref, self.y_ref
                    , fill_value='extrapolate')
                new_dis_function = interpolate.interp1d(self.x_dis, self.y_dis
                    , fill_value='extrapolate')

                
                qrows = len(self.linage_point_pairs)
                if not self.linage_point_pairs == ['No pair added yet']:
                    for i in range(0,qrows):
                        con = ConnectionPatch(xyA=(self.clicks_ref[i],float(new_ref_function(self.clicks_ref[i])) ), xyB=(
                            self.clicks_ref[i], float(new_dis_function(self.g(self.clicks_ref[i])))), coordsA="data", coordsB="data", axesA=self.ax1, axesB=self.ax2, color='b')
                        self.ax2.add_artist(con)

                self.graph.draw()


                # Visualization of the linage derivation and the linage function

                self.derivative = [0]
                sorted_clicks_dis , indices = sort_with_indices(self.clicks_dis) 
                sorted_clicks_ref = [self.clicks_ref[i] for i in indices]
                for i in range(len(self.clicks_dis)-1):
                    self.derivative.append(
                        (sorted_clicks_ref[i]-sorted_clicks_ref[i+1])/(sorted_clicks_dis[i]-sorted_clicks_dis[i+1]))

                self.draw_canvas_right()
                self.draw_canvas_left_rate()
                for i in range(len(self.pushed_data)):
                    abs_ref, ord_ref, abs_dis, ord_dis,x_ref,y_ref,x_dis,y_dis = self.pushed_data[self.titles[i]]           
                    self.overlapping_windows[i].close()
                    self.overlapping_windows[i] = self.draw_graphs_overlapped(abs_ref, ord_ref, abs_dis, ord_dis,x_ref,y_ref,x_dis,y_dis)

                self.reset.setDisabled(False)
                self.savebutton.setDisabled(False)

            self.linage_points_prep = ['No click yet', 'No click yet']

    def find_closest(self, arr, val):
        """ finds the closest value on the given array from the occured click"""
        favor_left = 10**(-5)
        idx = (np.abs(arr - val)-favor_left).argmin() # in case the val is in the middle of two values of the array the left value is favored
        # the weight should not exceed the precision of the array 
        return idx, arr[idx]
    
    ##### End #####

    # Action du bouton reset


    def draw_canvas_right(self):
        ax = self.figure_right.add_subplot(111)

        sorted_clicks_dis , indices = sort_with_indices(self.clicks_dis) 
        sorted_clicks_ref = [self.clicks_ref[i] for i in indices]

        ax.plot(sorted_clicks_dis,sorted_clicks_ref, color =  'g', linewidth=0.7)
        ax.scatter(sorted_clicks_dis,sorted_clicks_ref,  color = 'g')
        ax.set(xlabel =  'Dis', ylabel = 'Ref')
        ax.set_title('Age scale')
        ax.legend()

        self.canvas_right.draw()

    def draw_canvas_left_rate(self):
        self.figure_left.clear(True)
        sorted_clicks_dis , indices = sort_with_indices(self.clicks_dis) 
        ax = self.figure_left.add_subplot(111)
        ax.step(sorted_clicks_dis, self.derivative, 'r', linewidth=0.7)
        ax.set_title('Sedimentation rate')

        self.canvas_left.draw()

    def draw_graphs_overlapped(self, abs_ref, ord_ref, abs_dis, ord_dis, x_ref, y_ref, x_dis, y_dis):
        overlapping_window = QtWidgets.QMainWindow()
        overlapping_window.setWindowTitle(f'Correlation between {ord_ref}-{abs_ref} and {ord_dis}-{abs_dis}')
        overlapping_window.setGeometry(100, 100, 800, 400)  # Adjusted size for better visibility

        central_widget = QWidget(overlapping_window)
        overlapping_window.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)


        self.figureoverlapped = Figure()
        self.graphoverlapped = FigureCanvas(self.figureoverlapped)
        layout.addWidget(self.graphoverlapped)

        axes = self.figureoverlapped.add_subplot(111)

        centered_ydis = y_dis - np.mean(y_dis)
        centered_yref = y_ref - np.mean(y_ref)

        axes.plot(x_ref, centered_yref, color="r", linewidth=0.5, label=f'{ord_ref}-{abs_ref}')
        axes.plot(self.f(x_dis), centered_ydis, color='g', linewidth=0.5, label=f'{ord_dis}-{abs_dis}')

        axes.set_xlim([min(x_ref[0], x_dis[0]), max(x_ref[-1], x_dis[-1])])
        axes.set_xlabel(abs_dis)

        axes.set_xticks(np.arange(0, max(x_ref[-1],6000), 1000))

        axes.legend()

        overlapping_window.showMinimized()

        return overlapping_window
        


    def reset_button_clicked(self):
        '''reset button : resets linage, go back to original data'''
        self.figure.clear(True)
        self.ax1 = self.figure.add_subplot(211)
        self.ax1.plot(self.x_ref, self.y_ref, color="g", linewidth=0.5)
        self.ax1.set(xlabel=self.abs_ref, ylabel=self.ord_ref)
        self.ax1.set_xlim([self.x_ref[0], self.x_ref[-1]])


        self.ax1.figure.canvas.mpl_connect(
            'button_press_event', self.onclick)
        
        print("RESETING")
        # Intialize variables that will be used later

        self.linage_point_pairs = ['No pair added yet']
        self.linage_points_prep = ['No click yet', 'No click yet']

        # we initialize the choices of the user to None. ´Thoses variables will be updated when the user choose what he wants to plot
        self.pushed_data = {}
        self.titles = []

        self.clicks_dis= []
        self.clicks_ref= []
        # we initiale the list containing the correlation and overlapping windows

        self.switchButtons = {}
        self.correlation_window = None
        self.overlapping_windows = []
    
        # we initialize the two interpolation functions: f and its inverse

        self.f = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')
        self.g = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')

        
        self.figure_left.clf()
        self.canvas_left.draw()
        self.figure_right.clf()
        self.canvas_right.draw()

        if (self.x_dis is not None) and (self.y_dis is not None) and (self.abs_dis is not None) and (self.ord_dis is not None):
            self.ax2 = self.figure.add_subplot(212)
            self.ax2.plot(self.x_dis, self.y_dis, color="r", linewidth=0.5)
            self.ax2.set(xlabel=self.abs_dis, ylabel=self.ord_dis)
            self.ax2.set_xlim([self.x_ref[0], self.x_ref[-1]])

            self.ax2.figure.canvas.mpl_connect(
                'button_press_event', self.onclick)


        self.show()


