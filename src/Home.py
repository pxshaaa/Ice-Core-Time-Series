# Linn Habberstad, Teddy Tonin and Pasha Alidadi

import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QFileDialog, QLabel, QVBoxLayout,QPushButton,QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView

import pandas as pd

from file import load_file_on_widget,load_file
from Plot import plot_widget
from Organize_data import WorkSheet
from linage import PlotGraph
from Interpolation import InterpolationWindow
from correlation import CorrelationPlotGraph
from histogram import HistogramPlotGraph
from stats_function import StatsPlotGraph



class CorrelationWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        button = QPushButton("Correlation")
        layout.addWidget(button)
        self.setLayout(layout)

class HistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        button = QPushButton("Histogram")
        layout.addWidget(button)
        self.setLayout(layout)

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        button = QPushButton("Stats")
        layout.addWidget(button)
        self.setLayout(layout)


class LinageWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        button = QPushButton("Linage")
        layout.addWidget(button)
        self.setLayout(layout)


class Home(QMainWindow):
    """Create a clean and neat background for the software"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initData()

        #Afficher l'image
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        label = QLabel(widget)

        current_directory = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(current_directory, 'bg.png')

        pixmap = QPixmap(image_path)
        screen_geometry = QDesktopWidget().screenGeometry()

        pixmap = pixmap.scaled(screen_geometry.width(),screen_geometry.height())
        layout.setContentsMargins(0, 0, 0, 0)

        label.setPixmap(pixmap)
        layout.addWidget(label)
        self.setCentralWidget(widget)

        # Afficher l'application en grand
        self.showFullScreen()

        # sets the title for the main window. That title will be defined once the file is chosen
        self.setWindowTitle("AnalySeries")

        # initializes the user guide 
        self.guide = None
        
        
    def initUI(self):

        # Displays the window 

        self.showMaximized()

        # creates a definitive menu for the window
        self.create_menu()

        self.setMouseTracking(True)
    
    def initData(self):

        # store the data as a dataframe once the file is chosen
        self.filepath = None
        self.filepaths = []# filepaths will be added to this list as user opens files

        self.dataframe = None
        self.dataframes = {} # dataframes will be added to this dictionary as user opens files. The key will be the filepath
        self.list_dataframes =[] # here they wil be stored as a list
        #self.merged_dataframes = None

    def set_correlation_widget(self):
        self.central_widget = CorrelationWidget()
        self.setCentralWidget(self.central_widget)

    def set_histogram_widget(self):
        self.central_widget = HistogramWidget()
        self.setCentralWidget(self.central_widget)

    def set_stats_widget(self):
        self.central_widget = StatsWidget()
        self.setCentralWidget(self.central_widget)
    
    def set_linage_widget(self):
        self.central_widget = LinageWidget()
        self.setCentralWidget(self.central_widget)


    def create_menu(self):

        menu = self.menuBar()

        # the purpose of this variable is to refresh the page where the user is when he opens another file
        # this is so that  he does not have to do it himself
        self.current_window = {'Display': False, 'Plot': False, 'Linage' : False, 'Correlation' : False, 'Histogram' : False, 'Stats' : False, 'Splinage': False}# the different menus he needs to refresh

        # Module File
        fileMenu = menu.addMenu("File")

                # new file
        newAction = QAction("New", self)# create an element "New" of a menu
        newAction.setShortcut("Ctrl+N")
        fileMenu.addAction(newAction)# add the "New" in the menu "File"
        newAction.triggered.connect(self.selectFile)
                # open file
        openAction = QAction("Open", self)# create an element "Open"
        openAction.setShortcut("Ctrl+O")
        fileMenu.addAction(openAction)        # connect the button "Open" with the selectfile method
        openAction.triggered.connect(self.selectFile) # in order to keep this code light we implemented selectfile method later
        
                # save File
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        #saveAction.triggered.connect(file_save(self)) # same here, the file_save method will be implemented
                                            # right after the menu is all set. Paste, and close_window too

        fileMenu.addSeparator()# add a seperation line in the menu

        # copy, paste, exit
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        fileMenu.addAction(copyAction)
        #pasteAction.triggered.connect(self.copy)

        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+P")
        fileMenu.addAction(pasteAction)
        #pasteAction.triggered.connect(self.paste)

        exitAction = QAction("Exit", self)
        fileMenu.addAction(exitAction)
        #exitAction.triggered.connect(close_window(self))

        #fileMenu.addSeparator()
        #self.WorksheetAction = QAction("Worksheet",self)
        #fileMenu.addAction(self.WorksheetAction)
        #self.WorksheetAction.setDisabled(True)
        #self.WorksheetAction.triggered.connect(self.show_worksheet)


        # Module Data
        
        dataMenu = menu.addMenu("Data")# add a data menu
        
        # Visualisation des données 
        
        dataAction = QAction('Display',self) # create a "Display" élement
        dataMenu.addAction(dataAction) # make "Dataframe" a submenu
        dataAction.triggered.connect(self.visualize_data) # connect dataframe to visualize_data
        self.current_window['Display'] = False
        
        # Graphique 
        
        plotAction = QAction('Plot',self) # # create a "Plot" élément
        dataMenu.addAction(plotAction) # make "Plot" a submenu

        plotAction.triggered.connect(self.plotgraph)
        self.current_window['Display'] = False


        # Module Math 
        mathMenu = menu.addMenu("Math")

        #Function New sampling
        newSamplingAction = QAction('New Sampling',self)
        mathMenu.addAction(newSamplingAction)
        newSamplingAction.triggered.connect(self.interpolationwindow)

        # Function Correlation 
        correlationAction = QAction('Correlation',self)
        mathMenu.addAction(correlationAction)
        correlationAction.triggered.connect(self.correlation_window)

        # Function Histogram 
        histogramAction = QAction('Histogram',self)
        mathMenu.addAction(histogramAction)
        histogramAction.triggered.connect(self.histogram_window)

        # Function Stats 
        statsAction = QAction('Stats',self)
        mathMenu.addAction(statsAction)
        statsAction.triggered.connect(self.stats_window)

        #Module Dating
        datingMenu = menu.addMenu("Dating")

                
        # Fonction Age scale 
        agescaleAction = QAction('Age Scale',self)
        datingMenu.addAction(agescaleAction)
        # Fonction Linage 
        linageAction = QAction('Linage',self)
        datingMenu.addAction(linageAction)
        linageAction.triggered.connect(self.linage_window)

        # Fonction Splinage
        splinageAction = QAction('Splinage',self)
        datingMenu.addAction(splinageAction)

        
        # Module Help
        helpMenu = menu.addMenu("Help")
        
        # Fonction User Guide 
        userguideAction = QAction('See User Guide',self)
        helpMenu.addAction(userguideAction)
        userguideAction.triggered.connect(self.userguide)
    

    def selectFile(self):
        filepath, _ = QFileDialog.getOpenFileName(
                self, "QFileDialog.getOpenFileName()", "", "All Files (*);;CSV Files (*.txt)")
        if filepath:
            if filepath not in self.filepaths: # if the file has not been opened already
                self.filepath = filepath
                self.filepaths.append(filepath)

                self.dataframe = load_file(filepath)
                self.dataframes[filepath]= self.dataframe
                self.list_dataframes.append(self.dataframe)

                self.merged_dataframes= pd.concat(self.list_dataframes, axis =0)
                
                self.reload_menu()
                print('new file added')
                #self.WorksheetAction.setDisabled(False)
                self.Worksheet = WorkSheet(self.dataframe)

    #def show_worksheet(self):
        #self.Worksheet.displayWorksheet()

    def visualize_data(self):
        data_on_widget= load_file_on_widget(self.dataframes,self.filepaths)
        self.setCentralWidget(data_on_widget)
        # updates the current position of the user
        self.current_window['Display'] = True
        self.current_window['Plot'] = False
        

    def linage_window(self):
        self.linage_widget = PlotGraph(self.merged_dataframes,self.Worksheet)
        self.setCentralWidget(self.linage_widget)

    def correlation_window(self):
        self.correlation_widget = CorrelationPlotGraph(self.filepaths,list(self.dataframes.values()))
        self.setCentralWidget(self.correlation_widget)

    def histogram_window(self):
        if self.filepaths and self.dataframes:
            self.histogram_widget = HistogramPlotGraph(self.filepaths, list(self.dataframes.values()))
            self.setCentralWidget(self.histogram_widget)

    def stats_window(self):
        # Initialize or refresh the PlotGraph widget with the current data
        if self.filepaths and self.dataframes:
            self.stats_widget = StatsPlotGraph(self.filepaths, list(self.dataframes.values()))
            self.setCentralWidget(self.stats_widget)
    
    def interpolationwindow(self):
 
        self. interpolationwindow = InterpolationWindow(self.merged_dataframes, self.Worksheet)



    def plotgraph(self):
        plotwidget = plot_widget(self.dataframes,self.filepaths)
        self.setCentralWidget(plotwidget)
        # updates the current position of the user
        self.current_window['Plot'] = True
        self.current_window['Display'] = False
        print(self.current_window)
        
    def userguide(self):
        self.setWindowTitle("UserGuide")
        self.showMaximized()

        self.setWindowTitle("UserGuide")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        webview = QWebEngineView()
        layout.addWidget(webview)
        
        pdf_path = '/Users/xavier/Downloads/lsce-main 3/HKUST_Assignment_Template.pdf'
        
        self.display_pdf(webview)

    def display_pdf(self, webview):
        html_content = f"""<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Notice d'utilisation</title>
</head>

<body>
    <div class="titlepage">
        <div class="center">
            <h1>Notice d'utilisation</h1>
            <br>
            <br>
        </div>
    </div>

    <div class="newpage">
        <h2>Importer des fichiers</h2>
        <ol>
            <li>Placez le pointeur de la souris sur la partie "File" de la barre de menu. Habituellement, cette option est située dans le coin supérieur gauche de la fenêtre de l'application. Cliquez sur "File". Une liste déroulante ouvrira un menu avec différentes options.</li>
            <li>Repérez l'option "New" dans le menu. Glissez la souris sur l'option "New".</li>
            <li>Recherchez alors votre fichier, il faut qu'il soit compatible avec le logiciel c'est-à-dire en format .csv, .xls et .txt.</li>
            <li>Si vous souhaitez travailler sur plusieurs fichiers de données, vous pouvez répéter l'opération autant de fois que vous le souhaitez.</li>
        </ol>
    </div>

    <div class="section">
        <h2>Visualiser les données</h2>
        <ol>
            <li>Placez le pointeur de la souris sur la partie "Data" de la barre de menu. Cliquez sur "Data". Une liste déroulante ouvrira un menu avec différentes options.</li>
            <li>Repérez l'option "Display" dans le menu. Glissez la souris sur l'option "Display".</li>
            <li>Vous pouvez alors choisir les données que vous voulez visualiser avec le menu déroulant Choose File.</li>
        </ol>
    </div>

    <div class="section">
        <h2>Tracer des graphiques</h2>
        <ol>
            <li>Placez le pointeur de la souris sur la partie "Data" de la barre de menu. Cliquez sur "Data". Une liste déroulante ouvrira un menu avec différentes options.</li>
            <li>Repérez l'option "Plot" dans le menu. Glissez la souris sur l'option "Plot".</li>
            <li>Vous pouvez alors choisir les données que vous voulez utiliser avec le menu déroulant Choose File.</li>
            <li>Vous pouvez alors choisir deux colonnes de ce fichier pour les axes x et y afin de tracer votre graphique.</li>
        </ol>
    </div>

    <div class="section">
        <h2>Recaler des séries temporelles</h2>
        <ol>
            <li>Placez le pointeur de la souris sur la partie "Math" de la barre de menu. Cliquez sur "Math". Une liste déroulante ouvrira un menu avec différentes options.</li>
            <li>Repérez l'option "Linage" dans le menu. Glissez la souris sur l'option "Linage". La page vous permettant d'effectuer un recalage temporel des séries de données va s'ouvrir.</li>
            <li>Dans le menu déroulant First Graph, vous choisissez l'abscisse et l'ordonnée du graphique de référence. Dans le menu déroulant Second Graph, vous choisissez l'abscisse et l'ordonnée du graphique à recaler.</li>
            <li>Vous pouvez ensuite en cliquant une fois sur les données de chaque graphique afin de recaler les séries en sachant que pour qu'un recalage s'effectue, il faut au moins deux liaisons. La représentation de Age Scale et de Sedimation Rate changera au fur et à mesure de votre recalage.</li>
            <li>Pour remplacer la visualisation de l'indicateur Sedimation Rate par les graphiques recalés, vous pouvez cliquer sur Show Graphs Overlapped. Pour réafficher l'indicateur Sedimation Rate, vous pouvez cliquer sur Show Sedimation Rate.</li>
            <li>Pour mettre en grand écran les graphiques pendant le recalage, vous pouvez appuyer sur Full en bas à gauche de l'écran. Pour revenir à la normale, vous pouvez appuyer sur Nofull aussi en bas à gauche de l'écran.</li>
            <li>Pour annuler les clics, vous pouvez appuyer sur reset.</li>
        </ol>
    </div>

    <div class="section">
        <h2>Ajout d'une nouvelle fonction</h2>
        <p>Rendre le logiciel open-source était au cœur de notre projet, voici des instructions détaillées sur la manière d'ajouter de nouvelles fonctions aux séries temporelles.</p>
    </div>

</body>
<ol start="5">
    <li>Ajout de votre fonction dans la barre de menu
        <ol type="a">
            <li>Ouvrez votre éditeur de code et recherchez le fichier "Home.py".</li>
            <li>Localisez la méthode "create_menu(self)" dans le fichier Home.py. Cette méthode est responsable de la création de la barre de menu.</li>
            <li>À l'endroit approprié dans la méthode "create_menu(self)", insérez le code suivant pour ajouter votre fonction au menu :</li>
        </ol>
        <pre>
NewfunctionAction = QAction('Newfunction', self)
mathMenu.addAction(NewfunctionAction)
NewfunctionAction.triggered.connect(self.newfunction)
        </pre>
        <p>Assurez-vous de remplacer "Newfunction" par le nom de votre fonction. Notez que "newfunction" est une méthode de la classe Home que vous définirez à la fin du code.</p>
    </li>
    <li>Lier l'action de votre fonction au menu
        <ol type="a">
            <li>À la fin du fichier Home.py, vous allez implémenter une méthode pour la fonction que vous souhaitez ajouter.</li>
            <li>Pour maintenir un code simple et clair, nous recommandons de coder votre nouvelle fonction dans un fichier séparé et d'importer uniquement les fonctions pertinentes dans cette méthode située à la fin de Home.py.</li>
            <li>Vos fonctions nécessiteront les attributs self.filepaths et self.dataframes, qui contiennent les informations suivantes :</li>
            <ol type="i">
                <li>Attribut self.filepaths :
                    <ul>
                        <li>Liste contenant les chemins des fichiers ouverts précédemment.</li>
                    </ul>
                </li>
                <li>Attribut self.dataframes :
                    <ul>
                        <li>Dictionnaire contenant les données des carottes sous forme de dataframe.</li>
                        <li>Chaque chemin de fichier (présent dans self.filepaths) est associé à son dataframe correspondant dans le dictionnaire.</li>
                    </ul>
                </li>
            </ol>
        </ol>
        <p>Lorsqu'un nouveau fichier est ouvert, les attributs self.filepath, self.filepaths et self.dataframes sont mis à jour comme suit :</p>
        <pre>
self.filepath = filepath
self.filepaths.append(filepath)

self.dataframe = load_file(filepath)
self.dataframes[filepath] = self.dataframe
        </pre>
        <p>Assurez-vous de prendre en compte ces attributs lors de la définition de votre nouvelle fonction.</p>
    </li>
    <li>Sauvegardez et exécutez votre programme
        <ol type="a">
            <li>Enregistrez les modifications apportées au fichier Home.py.</li>
            <li>Exécutez votre programme pour vérifier le fonctionnement de la nouvelle fonctionnalité ajoutée.</li>
        </ol>
    </li>
</ol>


</html>


        """

        webview.setHtml(html_content)
    
    def reload_menu(self):
        if self.current_window['Plot']==True:
                self.plotgraph()
        if self.current_window['Display']==True:
                self.visualize_data()

