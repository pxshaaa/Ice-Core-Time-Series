# Teddy Tonin

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QVBoxLayout,QHBoxLayout,QDesktopWidget,QWidget,QLineEdit,QFrame
from PyQt5 import  QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy import interpolate,integrate


class InterpolationWindow(QtWidgets.QMainWindow):
    def __init__(self, dataframe, organizer, parent=None): #organizer is a window object from the Organize_data file
        super().__init__()
        self.df = dataframe
        self.organizer = organizer
        self.interpolation_widget = Choicewidget(self.df,self.organizer)

        self.setWindowTitle('Resampling')
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2,
            self.width(),
            self.height()
        )

        # Set a fixed size for the window
        self.setFixedSize(self.size())

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.interpolation_widget)
        cancelok = QHBoxLayout()
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close_window)
        cancel.setFixedSize(50, 25)
        ok = QPushButton('OK')
        ok.clicked.connect(self.show_interpolation)
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
        
    def show_interpolation(self):
        if (self.interpolation_widget.scalename or (self.interpolation_widget.from_input and  self.interpolation_widget.to_input ))\
                and self.interpolation_widget.interpolationtype and self.interpolation_widget.functiontype:
            self.interpolation_widget.interpolate()
            self.interpolation_widget.saveNewSampling()
        


class Choicewidget(QtWidgets.QWidget):

    def __init__(self, dataframe, organizer, parent=None):
        super().__init__(parent)

        self.df = dataframe
        self.organizer = organizer
        self.scalename = False

        self.choiceAbsToSample = QComboBox()
        self.choiceAbsToSample.addItem('Choose abcissa')
        self.choiceAbsToSample.addItems(self.df.columns)
        self.choiceAbsToSample.currentTextChanged.connect(self.push_choice_abs)

        self.choiceOrdToSample = QComboBox()
        self.choiceOrdToSample.setEnabled(False)
        self.choiceOrdToSample.addItem('Choose ordinate')
        self.choiceOrdToSample.addItems(self.df.columns)
        self.choiceOrdToSample.currentTextChanged.connect(self.push_choice_ord)

        
        scalechoice = QHBoxLayout()
        self.evenlysampled = QPushButton('evenly sampled')
        self.evenlysampled.setFixedSize(self.evenlysampled.sizeHint())
        self.evenlysampled.clicked.connect(self.switchToEvenlySampled)
        self.evenlysampled_stylesheet = self.evenlysampled.styleSheet()
        self.evenlysampled.setStyleSheet('background-color: blue; color: white;')
        self.usingscaleof = QPushButton('using scale of')
        self.usingscaleof.setFixedSize(self.usingscaleof.sizeHint())
        self.usingscaleof.clicked.connect(self.switchToUsingScaleOf) 
        self.usingscaleof_stylesheet = self.usingscaleof.styleSheet()
        scalechoice.addWidget(self.evenlysampled)
        scalechoice.addWidget(self.usingscaleof)
        self.scalechoice = 'evenlysampled'
  

        interpolationlayout = QHBoxLayout()
        Interpolationtype = QComboBox()
        Interpolationtype.addItems(['','Simple interpolation','Integration'])
        Interpolationtype.currentTextChanged.connect(self.push_choice_interpolation_type)
        interpolationlayout.addWidget(QLabel("Interpolation Type:"))
        interpolationlayout.addWidget(Interpolationtype)


        functionlayout = QHBoxLayout()
        Functiontype = QComboBox()
        Functiontype.addItems(['','Staircase','Linear','Cubic spline'])
        Functiontype.currentTextChanged.connect(self.push_choice_function_type)
        functionlayout.addWidget(QLabel("Function type:"))
        functionlayout.addWidget(Functiontype)

        densitylayout = QHBoxLayout()
        self.adddensity = QPushButton()
        self.adddensity.setFixedSize(25,25)
        self.adddensity.clicked.connect(self.addDensity)
        densitylayout.addWidget(self.adddensity)
        densitylayout.addWidget(QLabel("density series"))


        # Window layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(QLabel("Choose data to resample"))
        layout.addWidget (self.choiceAbsToSample)
        layout.addWidget (self.choiceOrdToSample)
        layout.addLayout(scalechoice)
        layout.addWidget(self.boxforevenlysampled())
        layout.addLayout(interpolationlayout)
        layout.addLayout(functionlayout)
        layout.addLayout(densitylayout)
    

    def switchToEvenlySampled(self):
        self.updateScaleChoiceWidget(self.boxforevenlysampled())   
        self.usingscaleof.setStyleSheet(self.usingscaleof_stylesheet)
        self.evenlysampled.setStyleSheet('background-color: blue; color: white;')
        self.scalechoice = 'evenlysampled'
    
    def switchToUsingScaleOf(self):
        self.updateScaleChoiceWidget(self.boxforusingscaleof())
        self.evenlysampled.setStyleSheet(self.evenlysampled_stylesheet)
        self.usingscaleof.setStyleSheet('background-color: blue; color: white;')
        self.scalechoice = 'usingscaleof'

    def boxforevenlysampled(self):   
        self.box_frame = QFrame()
        self.box_frame.setFrameShape(QFrame.Box)
        self.box_layout = QVBoxLayout(self.box_frame)

        #from
        from_layout = QHBoxLayout()
        from_label = QLabel("from")
        font = QFont()
        font.setBold(True)
        from_label.setFont(font)
        from_layout.addWidget(from_label)
        from_input_edit = QLineEdit()
        self.from_input = from_input_edit.text()
        from_input_edit.textChanged.connect(self.update_from_input)
        from_input_edit.setFixedWidth(60)
        from_layout.addWidget(from_input_edit)

        #to
        to_layout = QHBoxLayout()
        to_label = QLabel("to  ")
        font = QFont()
        font.setBold(True)
        to_label.setFont(font)
        to_layout.addWidget(to_label)
        self.to_input_edit = QLineEdit()
        self.to_input = self.to_input_edit.text()
        self.to_input_edit.textChanged.connect(self.update_to_input)
        self.to_input_edit.setFixedWidth(60)
        
        increase_button = QPushButton("►")
        increase_button.setFixedWidth(20)
        decrease_button = QPushButton("◄")
        decrease_button.setFixedWidth(20)

        increase_button.clicked.connect(self.increase_number)
        decrease_button.clicked.connect(self.decrease_number)

        to_layout.addWidget(decrease_button)
        to_layout.addWidget(increase_button)
        to_layout.addWidget(self.to_input_edit)
        

        #step
        step_layout = QHBoxLayout()
        step_label = QLabel("step")
        font = QFont()
        font.setBold(True)
        step_label.setFont(font)
        step_layout.addWidget(step_label)
        self.step_input = "10"
        step_input_edit = QLineEdit()
        step_input_edit.setText(self.step_input)
        step_input_edit.setFixedWidth(60)
        step_input_edit.textChanged.connect(self.update_step_input)
        step_layout.addWidget(step_input_edit)

        #count the number of points
        self.counting_label = QLabel('')
        #display current values of the abscissa
        self.extremes_label = QLabel('')       

        self.box_layout.addWidget(self.extremes_label)
        self.box_layout.addLayout(from_layout)
        self.box_layout.addLayout(to_layout)
        self.box_layout.addLayout(step_layout)
        self.box_layout.addWidget(self.counting_label)

        return self.box_frame
    
    def increase_number(self):
        input = int(self.to_input)
        step = int(self.step_input)
        input+=step
        self.to_input = str(input)
        self.to_input_edit.setText(self.to_input)
       
    
    def decrease_number(self):
        input = int(self.to_input)
        step = int(self.step_input)
        input-=step
        self.to_input = str(input)
        self.to_input_edit.setText(self.to_input)
        

    def count(self):
        if len(self.from_input)>0 and len(self.to_input)>0:
            self.counting_label.setText(f"This new series will have {1+(float(self.to_input)-float(self.from_input))//float(self.step_input)} points")
        
    def update_step_input(self, new_text):
        # Update self.step_input when the text is changed by the user
        self.step_input = new_text
        self.count()
    
    def update_from_input(self,new_text):
        self.from_input = new_text
        self.count()

    def update_to_input(self,new_text):
        self.to_input = new_text
        self.count() 
    

    def push_choice_abs(self,index):
        self.abs = index
        self.choiceOrdToSample.setEnabled(True)

    
    def push_choice_ord(self,index):
        self.ord =  index

        dfXY= self.df.dropna(subset=[self.abs, self.ord], how='any')
        self.x = dfXY[self.abs].to_numpy()
        self.y = dfXY[self.ord].to_numpy()
        self.current_min = str(self.x[0])
        self.current_max = str(self.x[-1])
        self.extremes_label.setText(f'Extremes values of the current sampling   Min ={self.current_min} Max = {self.current_max} ')
    

    def boxforusingscaleof(self):

        box_frame = QFrame()
        box_frame.setFrameShape(QFrame.Box)
        self.box_layout = QVBoxLayout(box_frame)

        # choose new x-scale
        choiceAbs = QComboBox()
        choiceAbs.addItem('Choose')
        choiceAbs.addItems(self.df.columns)
        choiceAbs.currentTextChanged.connect(self.push_choice_scale)

 
        self.box_layout.addWidget(QLabel('Choose new scale'))
        self.box_layout.addWidget(choiceAbs)
        

        return box_frame
    
    def push_choice_scale(self,index):

        self.scalename = index #the name of the column used for the sampling
        self.newscale = self.df[index]
        self.newscale = self.newscale[~np.isnan(self.newscale)]

    def updateScaleChoiceWidget(self, newWidget):
        layout = self.layout()
        
        item = layout.itemAt(layout.count() - 4)  # Assuming the scale choice widget is the 4-to-last item
        if item:
            oldWidget = item.widget()
            layout.replaceWidget(oldWidget, newWidget)
            oldWidget.deleteLater()

    def push_choice_interpolation_type(self,index):
        self.interpolationtype = index
    
    def push_choice_function_type(self,index):
        self.functiontype = index

    def addDensity(self):
        self.adddensity.setStyleSheet('background-color: blue; color: white;')


# the code for the actual interpolation
    
    def interpolate(self):

        #show the interpolation
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('Interpolation window')

        central_widget = QWidget(self.window)  # Create a central widget
        self.window.setCentralWidget(central_widget)  # Set it as the central widget

        self.figure = Figure()
        self.figure.tight_layout()
        self.graph = FigureCanvas(self.figure)

        self.windowlayout = QVBoxLayout(central_widget)  # Use a QVBoxLayout for simplicity

        self.ax1 = self.figure.add_subplot(211)
        line1, = self.ax1.plot(self.x, self.y, color='g', linewidth=0.5)
        self.ax1.set(xlabel=self.abs, ylabel=self.ord)
       

        if self.interpolationtype == 'Simple interpolation':
            self.simpleinterpolation()
        else:
            self.integration()

        mask = (float(self.from_input) <= self.x) & (self.x <= float(self.to_input))
        self.ax1.set_title(f'Previous Sampling, number of points = {len(self.x[mask])}', loc='right')
        self.ax1.set_xlim([float(self.from_input),float(self.to_input)])

        if self.functiontype == 'Linear':
            line2, = self.ax2.plot(self.new_x, self.new_y, color='r', linewidth=0.5)
            
        if self.functiontype == 'Staircase':
            line2, = self.ax2.plot(self.new_x, self.new_y, color='r',drawstyle ='steps', linewidth=0.5)
            
        if self.functiontype == 'Cubic spline':
            cubicspline = interpolate.CubicSpline(self.new_x,self.new_y)
            x_smooth = np.arange(min(self.new_x),max(self.new_x),float(self.step_input)/10)
            line2, =self.ax2.plot(x_smooth,cubicspline(x_smooth), color = 'r')

        self.ax2.set_xlim([float(self.from_input),float(self.to_input)])
        self.ax2.set_title(f'New Sampling, number of points = {len(self.new_x)}, step = {float(self.step_input)}', loc='right')
            
        self.windowlayout.addWidget(self.graph)
        self.graph.draw()
        self.window.show()



    def simpleinterpolation(self):

        self.ax2 = self.figure.add_subplot(212)
        f = interpolate.interp1d(self.x, self.y)
        if self.scalechoice == 'evenlysampled':
            self.new_x = np.arange(float(self.from_input), float(self.to_input), float(self.step_input))
            self.new_y = f(self.new_x)
        if self.scalechoice == 'usingscaleof':
            self.new_x = self.newscale.to_numpy()
            self.new_y = f(self.new_x)
            self.from_input = self.new_x[0]
            self.to_input = self.new_x[-1]


    def integration(self):

        self.ax2 = self.figure.add_subplot(212)
        if self.scalechoice == 'evenlysampled':
            self.new_x = np.arange(float(self.from_input), float(self.to_input), float(self.step_input))
        if self.scalechoice == 'usingscaleof':
            self.new_x = self.newscale.to_numpy()
            self.from_input = self.new_x[0]
            self.to_input = self.new_x[-1]


        self.intervalles = np.zeros(len(self.new_x)+1)
        self.intervalles[0]=self.new_x[0]
        self.intervalles[-1]= self.new_x[-1]
        for i in range(1,len(self.new_x)):
            self.intervalles[i] = 0.5*(self.new_x[i-1]+self.new_x[i])
        
        '''
        if self.functiontype == 'Linear':
            self.f = interpolate.interp1d(self.x, self.y)

        if self.functiontype == 'Staircase':
            self.f = np.piecewise(self.x, [self.x <= xi for xi in self.x], self.y)
        if self.interpolationtype == 'Integration':
            self.f =interpolate.CubicSpline(self.x,self.y)
        '''
        self.f = interpolate.interp1d(self.x, self.y)
        #compute the new ordinate
        self.new_y = np.zeros_like(self.new_x)
        for i in range(len(self.new_x)):
            step = self.intervalles[i+1]-self.intervalles[i]
            result,_ = integrate.quad(self.f,self.intervalles[i],self.intervalles[i+1])
            self.new_y[i] = result/step
    
    def saveNewSampling(self):
        if self.scalechoice == 'evenlysampled':
            title = f'{self.scalechoice} {self.abs} - {self.ord}, step = {self.step_input}, {self.interpolationtype}, {self.functiontype}'
        else:
            title = f'{self.scalechoice} {self.abs} - {self.ord}, using scale of  = {self.scalename}, {self.interpolationtype}, {self.functiontype}'
        
        self.organizer.add_NewSampling(title,self.window,self.new_x,self.new_y)
        
        






    

        

        