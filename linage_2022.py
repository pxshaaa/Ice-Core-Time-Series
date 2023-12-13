from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout, QVBoxLayout, QFileDialog, QApplication
import matplotlib
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from matplotlib.patches import ConnectionPatch
from scipy import interpolate
import math

from pylab import rcParams
#rcParams['figure.figsize'] = 6.4, 4.8


# Plotting graph with matplotlib
matplotlib.use('tkagg')


matplotlib.use('Qt5Agg')

# ALL OF LINAGE DONE HERE :
# LINAGE WINDOW, MATHS BEHIND IT, PLOTTING, INTERACTIVE PART.

# clicks are saved with their respective coordinates and the information whether
# they occured in the upper or lower plot in the linage_point_pairs and
# linage_points_prep matrices. Please note that the plot number is determined
# automatically further down below in the code.


def graph_data(df, x, y):
    x1, y1 = math.inf, math.inf
    i = 0
    while (x1 == math.inf or y1 == math.inf) and i < len(list(df.columns)):
        if list(df.columns)[i] == x:
            x1 = list(df.columns)[i]
        if list(df.columns)[i] == y:
            y1 = list(df.columns)[i]
        i += 1
    df.plot(x=x1, y=y1, kind='line')
    plt.show()



class Click:

    def __init__(self, x, y, plotno):
        self._x = x
        self._y = y
        self._plotno = plotno


class PlotGraph(QtWidgets.QWidget):
    def __init__(self, filepath=None, x1=None, y1=None, abs1=None, ord1=None, x2=None, y2=None, abs2=None, ord2=None, parent=None):
        """x1 & x2 are the x coordinates of the first and second graph ; y1 & y2 the y-coordinates and abs & ord are the labels of those coordinates"""
        super().__init__(parent)

        self.setMouseTracking(True)
        self.file = filepath
        self.df = read_data(filepath)
        self.coord = None
        self.x1, self.x2, self.y1, self.y2, self.abs1, self.abs2, self.ord1, self.ord2 = x1, x2, y1, y2, abs1, abs2, ord1, ord2

        # f3 is an interpolation function that translates the x-coordinates of
        # the normalized abscissa back into the displayed x-coordinates.
        # After the each linage, f3 is modified but with this configuration,
        # it just returns the input value. This makes sense before the first
        # linage, the abscissa is not normalized yet.
        self.f3 = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')

        if self.x2 is not None:
            if self.y2 is not None:
                self.prepare_linage()

        # TODO take over changes from lisa stuff
        self.setGeometry(0, 0, 1500, 1000)

        self.figure = Figure()
        self.figure.canvas.set_window_title('Linage')
        self.figure.tight_layout()  # pad=3.0)

        # Visualize graph
        self.graph = FigureCanvas(self.figure)

        # we want to get the coordinates of the clicks for the linage
        # just for name initialization
        self.clicx, self.clicy = 0, 0

        # Create graph1 (upper graph)
        self.prepare_figure()

        # Get x & y on graph
        self.ax1.figure.canvas.mpl_connect(
            'button_press_event', lambda event: self.onclick)

        self.figure_left = plt.figure(tight_layout=True)
        self.canvas_left = FigureCanvas(self.figure_left)

        self.figure_right = plt.figure(tight_layout=True)
        self.canvas_right = FigureCanvas(self.figure_right)
        self.figure_right.tight_layout(pad=100.0)

        self.topLeft()
        self.topRight()
        self.center()
        self.bottomRight()

        # To difine the grid in which the differents boxes of the windows will be
        # showed, it is defined the following grid.
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
        self.mainLayout = QGridLayout()

        for i, (row, col, row_span, col_span) in enumerate(grid):
            self.mainLayout.addWidget(label[i], row, col, row_span, col_span)

        self.setLayout(self.mainLayout)

        self.setWindowTitle("AnalySeries - Linage")
        QApplication.setStyle("Fusion")
        # QApplication: : setStyle("macintosh")

        # draw both graphs on the same plot
        self.figure_adjust_size()
        self.graph.draw()

        self.show()

    # prepare_linage only gets triggered if data has been chosen.

    def prepare_figure(self):
        if (self.x1 is not None) and (self.y1 is not None):  # we only plot when we have every data
            self.ax1 = self.figure.add_subplot(211)
            self.ax1.plot(self.x1, self.y1, 'tab:red', linewidth=0.5)

            # limits of the graph
            # lim & first finds the 1st & last data which is not "nan"
            lim1 = last_nan(self.x1)
            first1 = first_nan(self.x1)
            self.ax1.set_xlim([first1, lim1])
            if (self.abs1 is not None) and (self.ord1 is not None):  # labels only added if they exist
                self.ax1.set(xlabel=self.abs1, ylabel=self.ord1)

        # Create graph2 (lower graph)
        if (self.x2 is not None) and (self.y2 is not None):
            self.ax2 = self.figure.add_subplot(212)
            self.ax2.plot(self.x2, self.y2, color="b", linewidth=0.5)

            # limits of the graph
            lim2 = last_nan(self.x2)
            first2 = first_nan(self.x2)
            self.ax2.set_xlim([first2, lim2])
            if(self.abs2 is not None) and (self.ord2 is not None):
                self.ax2.set(xlabel=self.abs2, ylabel=self.ord2)

    def change_all(self):
        if self.x2 is not None:
            if self.y2 is not None:
                self.prepare_linage()

        self.clicx, self.clicy = 0, 0

        self.figure.clear(True)

        self.prepare_figure()

        self.figure_adjust_size()

        plt.close()

        self.figure_left.clear(True)
        self.figure_right.clear(True)
        self.reset_button_clicked()

    def align(self, vec_dis, len_vec_ref):
        """ Takes an ascending vector, keeps the min and max and stretches the
        length of the vector to the desired length """
        return np.linspace(vec_dis[0], vec_dis[-1], num=len_vec_ref, endpoint=True)

    # Prepare the variable to do the linage function

    def prepare_linage(self):
        source_file = pd.read_csv(self.file, sep='\t')
        self.x_ref = source_file[self.abs1].to_numpy()
        self.x_dis = source_file[self.abs2].to_numpy()
        self.y_ref = source_file[self.ord1].to_numpy()
        self.y_dis = source_file[self.ord2].to_numpy()
        self.x_ref = self.x_ref[~np.isnan(self.x_ref)]
        self.x_dis = self.x_dis[~np.isnan(self.x_dis)]
        self.y_ref = self.y_ref[~np.isnan(self.y_ref)]
        self.y_dis = self.y_dis[~np.isnan(self.y_dis)]
        self.len_ref = np.min([len(self.x_ref), len(self.y_ref)])
        self.len_dis = np.min([len(self.x_dis), len(self.y_dis)])
        self.x_ref = self.x_ref[:self.len_ref]
        self.y_ref = self.y_ref[:self.len_ref]
        self.x_dis = self.x_dis[:self.len_dis]
        self.y_dis = self.y_dis[:self.len_dis]

        # This determines the number of labels of the X-Axes of the refustable
        # plot (arbitrary, chosen for aesthetic and clarity)
        self.plot_label_no = 6

    # Place markers on graph on click
    def onclick(self, event):
        if event.inaxes in [self.ax1]:  # upper graph = reference graph
            self.ax1.plot(event.xdata, event.ydata,
                          '|', color="black", markersize=15)
            self.graph.draw()
            self.click(x=event.xdata, plotno=0)

        if event.inaxes in [self.ax2]:  # lower graph = distorted graph
            self.ax2.plot(event.xdata, event.ydata,
                          '|', color="black", markersize=15)
            self.graph.draw()

            # Call Linage functions
            self.click(x=event.xdata, plotno=1)

    ##### Begining of Linage ######

    def click(self, x, plotno):
        """ the click functions determines the x value and the y value is
        determined automatically using the given x value with the _index."""
        self._plotno = plotno
        if self._plotno == 1:  # lower
            self._x = self.find_closest(self.x_dis, self.f3(x))
            self._index = np.nonzero(self.x_dis == self._x)[0]
            self._y = self.y_dis[self._index][0]

        if self._plotno == 0:  # upper
            self._x = self.find_closest(self.x_ref, x)
            self._index = np.nonzero(self.x_ref == self._x)[0]
            self._y = self.y_ref[self._index][0]
        self.linage()

    def linage(self):

        # Clicks are added into linage_points_prep. If they occured in the upper
        # plot, they are saved in linage_points_prep[0] and if the occured in
        # the lower plot, they are saved in linage_points_prep[1]
        self.linage_points_prep[self._plotno] = Click(
            self._x, self._y, self._plotno)

        # If linage_points_prep has a click saved in both spots
        # (linage_points_prep[0] and linage_points_prep[1]), they are carried
        # over into linage_point_pairs where all the clicks are saved. Not
        # just the new ones.
        if self.linage_points_prep[0] != 0 and self.linage_points_prep[1] != 0:
            if self.linage_point_pairs[0] == [0, 0]:
                self.linage_point_pairs = self.linage_point_pairs[1:len(
                    self.linage_point_pairs)]
            self.manage_linage_point_lists()

            if len(self.linage_point_pairs) > 1:

                # the x coordinates are extracted
                self.clicks_ref = [i[0]._x for i in self.linage_point_pairs]
                self.clicks_dis = [i[1]._x for i in self.linage_point_pairs]

                # f1 is a function that maps from the reference graph to the
                # the distorted graph by using the clicks.
                self.f1 = interpolate.interp1d(
                    self.clicks_ref, self.clicks_dis, fill_value='extrapolate')

                # creates the new abscissa with the right length
                self.x_new = self.f1(self.align(self.x_ref, len(self.x_dis)))

                y_new = np.zeros(len(self.x_new))
                y_new[:] = np.nan

                # creates a constantly +1 inceasing vector with the length of x_new
                self.x_new_steps = np.array(range(len(self.x_new)))

                # f2 is a function that maps from x_new to x_new_steps and
                # thus mapping from the new abscissa to a relative abscissa
                self.f2 = interpolate.interp1d(
                    self.x_new, self.x_new_steps, fill_value='extrapolate')

                # f3 does the opposite of f2 and thus just enabling going reverse
                # from the relative abscissa that python uses to the actual
                # abscissa that is displayed
                self.f3 = interpolate.interp1d(
                    self.x_new_steps, self.x_new, fill_value='extrapolate')
                self.x_new_relative = self.f2(self.x_dis)

                # Plotting new graphs with linage
                # reploting main window, with distorted graph
                self.figure.clear(True)

                self.ax1 = self.figure.add_subplot(211)
                self.ax1.plot(self.x_ref, self.y_ref, color="r", linewidth=0.5)
                self.ax1.set(xlabel=self.abs1, ylabel=self.ord1)
                self.ax1.set_xlim([self.x_ref[0], self.x_ref[-1]])

                self.ax2 = self.figure.add_subplot(212)
                self.ax2.plot(self.x_new_relative, self.y_dis,
                              color='b', linewidth=0.5)
                self.ax2.set(xlabel=self.abs2, ylabel=self.ord2)
                self.ax2.set_xlim([0, len(self.x_new)-1])
                self.ax2.set_xticks(self.evenly_spaced(
                    range(len(self.x_new)), self.plot_label_no))
                self.ax2.set_xticklabels(
                    np.round(self.evenly_spaced(self.x_new, self.plot_label_no), 1))

                # The following loop iterates through all the saved clicks
                # and draws the lines accordingly.
                qrows = len(self.linage_point_pairs)
                for i in range(0, qrows):

                    relative_x_in_dis = self.find_closest(
                        self.x_new_relative, self.f2(self.linage_point_pairs[i][1]._x))
                    con = ConnectionPatch(xyA=(self.linage_point_pairs[i][0]._x, self.linage_point_pairs[i][0]._y), xyB=(
                        relative_x_in_dis, self.linage_point_pairs[i][1]._y), coordsA="data", coordsB="data", axesA=self.ax1, axesB=self.ax2, color="black")
                    self.ax2.add_artist(con)

                self.figure_adjust_size()

                self.graph.draw()

                # Plotting both the curves simultaneously
                # first we recenter the data so that it has a mean of 0
                avg_ydis = sum(self.y_dis)/len(self.y_dis)
                self.centered_ydis = self.y_dis - avg_ydis

                avg_yref = sum(self.y_ref)/len(self.y_ref)
                self.centered_yref = self.y_ref - avg_yref

                # Visualization of the linage derivation and the linage function

                self.derivative = [0]
                for i in range(len(self.clicks_dis)-1):
                    self.derivative.append(
                        (self.clicks_ref[i]-self.clicks_ref[i+1])/(self.clicks_dis[i]-self.clicks_dis[i+1]))

                self.draw_canvas_right()
                print('self.other_graph.text() : ', self.other_graph.text())
                if self.other_graph.text() == "Show graphs overlapped":
                    self.draw_canvas_left_rate()
                else:
                    self.draw_canvas_left_overlapped()

                self.reset.setDisabled(False)
                self.other_graph.setDisabled(False)

    def figure_adjust_size(self):
        if self.fullScreenButton.text() == "Full":
            self.figure.subplots_adjust(top=0.99)
            self.figure.subplots_adjust(bottom=0.135)
            self.figure.subplots_adjust(right=0.995)
            self.figure.subplots_adjust(left=0.08)
            self.figure.subplots_adjust(hspace=0.32)
        else:
            self.figure.subplots_adjust(top=0.95)
            self.figure.subplots_adjust(bottom=0.1)
            self.figure.subplots_adjust(right=0.995)
            self.figure.subplots_adjust(left=0.06)
            self.figure.subplots_adjust(hspace=0.2)

    def find_closest(self, arr, val):
        """ finds the closest value on the given array from the occured click"""
        idx = np.abs(arr - val).argmin()
        return arr[idx]

    def manage_linage_point_lists(self):
        """ manages linage_point_pairs and linage_points_prep to make sure that
        they can be used fruitfully by the linage function"""
        self.linage_point_pairs.append(self.linage_points_prep[:])

        # the points in the list are sorted ascendingly to make sure that there
        # is no bug with intersecting lines
        qrow = len(self.linage_point_pairs)
        qcol = len(self.linage_point_pairs[0])
        for col in range(qcol):
            temp = sorted([i[col] for i in self.linage_point_pairs],
                          key=lambda x: x._x, reverse=False)
            for row in range(qrow):
                self.linage_point_pairs[row][col] = temp[row]

        self.linage_points_prep[0] = 0
        self.linage_points_prep[1] = 0

    def evenly_spaced(self, arr, num_steps):
        """creates a relative abscissa"""
        idx = np.round(np.linspace(0, len(arr) - 1, num_steps)).astype(int)
        return np.array(arr)[idx]

    ##### End #####

    # Action du bouton reset

    def other_graph_clicked(self):
        if self.sender().text() == "Show graphs overlapped":
            self.other_graph.setText("Show Sedimentation rate")
            self.draw_canvas_left_overlapped()
        else:
            self.other_graph.setText("Show graphs overlapped")
            self.draw_canvas_left_rate()

    def draw_canvas_right(self):
        self.figure_right.clf()
        ax = self.figure_right.add_subplot(111)
        ax.plot(self.clicks_dis, self.clicks_ref, 'g', linewidth=0.7)
        ax.set_title('Age scale')

        self.canvas_right.draw()

    def draw_canvas_left_rate(self):
        self.figure_left.clf()
        ax = self.figure_left.add_subplot(111)
        ax.step(self.clicks_dis, self.derivative, 'g', linewidth=0.7)
        ax.set_title('Sedimentation rate')

        self.canvas_left.draw()

    def draw_canvas_left_overlapped(self):
        self.figure_left.clf()
        axes = self.figure_left.add_subplot(111)
        axes.plot(self.x_ref, self.centered_yref, color="r", linewidth=0.5)
        axes.set(xlabel=self.abs1, ylabel=self.ord1)
        axes.set_xlim([self.x_ref[0], self.x_ref[-1]])

        axes2 = axes.twiny()
        axes2.plot(self.x_new_relative, self.centered_ydis,
                   color='b', linewidth=0.5)
        axes2.set(xlabel=self.abs2, ylabel=self.ord2)
        axes2.set_xlim([0, len(self.x_new)-1])
        axes2.set_xticks(self.evenly_spaced(
            range(len(self.x_new)), self.plot_label_no))
        axes2.set_xticklabels(
            np.round(self.evenly_spaced(self.x_new, self.plot_label_no), 1))

        plt.yticks([])

        self.canvas_left.draw()

    def reset_button_clicked(self):
        '''reset button : resets linage, go back to original data'''
        self.figure.clear(True)
        self.ax1 = self.figure.add_subplot(211)
        self.ax1.plot(self.x1, self.y1, color="r", linewidth=0.5)
        self.ax1.set(xlabel=self.abs1, ylabel=self.ord1)
        lim1 = last_nan(self.x1)
        first1 = first_nan(self.x1)
        self.ax1.set_xlim([first1, lim1])

        self.data_x_post_lin, self.data_x_post_lin = self.x2, self.y2
        self.ax1.figure.canvas.mpl_connect(
            'button_press_event', self.onclick)
        print("RESET")
        self.linage_point_pairs = [[0, 0]]
        self.linage_points_prep = [0, 0]
        self.f3 = interpolate.interp1d(
            [1, 2], [1, 2], fill_value='extrapolate')

        self.figure_left.clf()
        self.canvas_left.draw()
        self.figure_right.clf()
        self.canvas_right.draw()

        if (self.x2 is not None) and (self.y2 is not None) and (self.abs2 is not None) and (self.ord2 is not None):
            self.ax2 = self.figure.add_subplot(212)
            self.ax2.plot(self.x2, self.y2, color="b", linewidth=0.5)
            self.ax2.set(xlabel=self.abs2, ylabel=self.ord2)
            lim2 = last_nan(self.x2)
            first2 = first_nan(self.x2)
            self.ax2.set_xlim([first2, lim2])

            self.ax2.figure.canvas.mpl_connect(
                'button_press_event', self.onclick)

        self.graph.draw()
        self.show()

    def center(self):
        '''
        Function that creates  the central - horizontal bar where the buttons to reset the plots,
        to change the plot of the overlapped graphs with the plot of the rate and the Comboboxes
        to change the axis of the graphs.
        '''

        self.centerBox = QGroupBox()

        self.other_graph = QPushButton('Show graphs overlapped')
        self.other_graph.setDisabled(True)
        self.other_graph.clicked.connect(self.other_graph_clicked)

        self.reset = QPushButton('Reset')
        self.reset.setDisabled(True)
        self.reset.clicked.connect(self.reset_button_clicked)

        ####################

        self.labelx1 = QLabel("x-data: {}".format(self.abs1))
        self.labely1 = QLabel("y-data: {}".format(self.ord1))

        self.labelx2 = QLabel(str(self.abs2))
        self.labely2 = QLabel(str(self.ord2))

        self.graph1_txt = QLabel("First graph: ")
        self.graph2_txt = QLabel("Second graph: ")

        # Menu to change x & y data for the first graph
        combobox_abs1 = QComboBox()
        combobox_abs1.addItem("Change")
        combobox_abs1.addItems(self.df.columns)

        combobox_ord1 = QComboBox()
        combobox_ord1.addItem('Change')
        combobox_ord1.addItems(self.df.columns)

        combobox_abs1.currentTextChanged.connect(self.push_choice_x1)
        combobox_ord1.currentTextChanged.connect(self.push_choice_y1)

        # Menu to choose x & y data for the second graph
        combobox_abs2 = QComboBox()
        combobox_abs2.addItem('Choose')
        combobox_abs2.addItems(self.df.columns)

        combobox_ord2 = QComboBox()
        combobox_ord2.addItem('Choose')
        combobox_ord2.addItems(self.df.columns)

        combobox_abs2.currentTextChanged.connect(self.push_choice_x2)
        combobox_ord2.currentTextChanged.connect(self.push_choice_y2)

        #################

        # Create Layout
        layout = QGridLayout()
        layout.addWidget(self.other_graph, 0, 0)
        layout.addWidget(self.reset, 1, 0)

        ############
        layout.addWidget(self.graph1_txt, 0, 1, QtCore.Qt.AlignRight)
        layout.addWidget(combobox_abs1, 0, 2)
        layout.addWidget(self.labelx1, 1, 2)
        layout.addWidget(combobox_ord1, 0, 3)
        layout.addWidget(self.labely1, 1, 3)
        layout.addWidget(self.graph2_txt, 0, 4, QtCore.Qt.AlignRight)
        layout.addWidget(combobox_abs2, 0, 5)
        layout.addWidget(self.labelx2, 1, 5)
        layout.addWidget(combobox_ord2, 0, 6)
        layout.addWidget(self.labely2, 1, 6)
        ###################

        self.centerBox.setLayout(layout)

    def push_choice_x1(self, index):
        self.abs1 = index
        xx = math.inf
        i = 0
        while (xx == math.inf) and i < len(list(self.df.columns)):
            if list(self.df.columns)[i] == index:
                xx = list(self.df.columns)[i]
            i += 1
        self.x1 = list(self.df[xx])
        self.labelx1.setText("x-data: {}".format(index))
        if self.y1 is not None:
            self.graphe1()

    def push_choice_y1(self, index):
        self.ord1 = index
        yy = math.inf
        i = 0
        while (yy == math.inf) and i < len(list(self.df.columns)):
            if list(self.df.columns)[i] == index:
                yy = list(self.df.columns)[i]
            i += 1
        self.y1 = list(self.df[yy])
        self.labely1.setText("y-data: {}".format(index))
        if self.abs1 is not None:
            self.graphe1()

    def push_choice_x2(self, index):
        self.abs2 = index
        xx = math.inf
        i = 0
        while (xx == math.inf) and i < len(list(self.df.columns)):
            if list(self.df.columns)[i] == index:
                xx = list(self.df.columns)[i]
            i += 1
        self.x2 = list(self.df[xx])
        self.labelx2.setText("x-data: {}".format(index))
        if self.ord2 is not None:
            self.graphe2()

    def push_choice_y2(self, index):
        self.ord2 = index
        yy = math.inf
        i = 0
        while (yy == math.inf) and i < len(list(self.df.columns)):
            if list(self.df.columns)[i] == index:
                yy = list(self.df.columns)[i]
            i += 1
        self.y2 = list(self.df[yy])
        self.labely2.setText("y-data: {}".format(index))
        if self.abs2 is not None:
            self.graphe2()

    def graphe1(self):
        if self.abs1 is not None:
            if self.ord1 is not None:
                self.change_all()

    def graphe2(self):
        if self.abs2 is not None:
            if self.ord2 is not None:
                self.change_all()

    def bottomRight(self):

        self.bottomRightBox = QGroupBox()  # "Bottom Right")

        # Create Full Screen Button
        self.fullScreenButton = QPushButton("Full")
        self.fullScreenButton.setMaximumWidth(100)
        self.fullScreenButton.setMaximumHeight(20)
        self.fullScreenButton.clicked.connect(self.swichFullScreen)

        # Create Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph)
        layout.addWidget(self.fullScreenButton)

        # Add Layout to GroupBox
        self.bottomRightBox.setLayout(layout)

    def topLeft(self):

        self.topLeftBox = QGroupBox()  # "Bottom Left top")

        # Create Layout
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas_left)

        # Add Layout to GroupBox
        self.topLeftBox.setLayout(layout)

    def topRight(self):

        self.topRightBox = QGroupBox()  # "Bottom Right top")

        # Create Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas_right)

        # Add Layout to GroupBox
        self.topRightBox.setLayout(layout)

    def swichFullScreen(self):
        if self.sender().text() == "Full":
            self.topLeftBox.hide()
            self.topRightBox.hide()
            self.centerBox.hide()
            self.bottomRightBox.hide()
            # As the Widget self.bottomRightBox will utilize all the Window size, the
            # size of it is redifinid as it start in (0,0) and utilize a total space
            # of (9,4) cases.
            self.mainLayout.addWidget(self.bottomRightBox, 0, 0, 9, 4)
            self.fullScreenButton.setText("NoFull")
            self.figure_adjust_size()
            self.bottomRightBox.show()

        else:
            self.bottomRightBox.hide()
            self.topLeftBox.show()
            self.topRightBox.show()
            self.centerBox.show()
            # As the Widget self.bottomRightBox will utilize the original size, the
            # size of it is redifinid as it start in (9,0) and utilize a total space
            # of (1,4) cases.
            self.mainLayout.addWidget(self.bottomRightBox, 9, 0, 1, 4)
            self.fullScreenButton.setText("Full")
            self.figure_adjust_size()
            self.bottomRightBox.show()


# in order to get the last number of the array (to plot), without all the "nan" data
def last_nan(x):
    last = x[0]
    for i in range(len(x)):
        if not math.isnan(x[i]):
            last = x[i]
    return last


def first_nan(x):
    i = 0
    while math.isnan(x[i]):
        i += 1
    return x[i]