# LSCE

# LSCE project
The Laboratoire des Sciences du Climat et de l'Environnement (LSCE) at the Paris Saclay University is at the forefront of paleoclimatology research, dedicated to understanding ancient climates to better inform our current and future environmental strategies. This vital work helps us comprehend the intricacies of climate change and its impacts. One of the key methodologies employed by LSCE is the science of ice cores. By analyzing ice cores, scientists can interpret climate signals embedded within them. These cores, extracted from polar regions and glaciers, act as time capsules, preserving valuable data about Earth's past atmospheric conditions. The analysis of these cores provides insights into the composition of the atmosphere, temperature trends, and even the occurrence of volcanic eruptions over millennia. In their pursuit of cutting-edge research, LSCE employs a 20-year-old application designed to automate the analysis of ice cores. Recognizing the importance of technological advancement, the laboratory is now aiming to modernize this application. The integration of contemporary data science techniques and tools is expected to enhance the efficiency and accuracy of their ice core analysis, which is the aim of this project.

## Membres de l'équipe

- Teddy Tonin : teddy.tonin@student-cs.fr
- Pasha Alidadi : pasha.alidadi@student-cs.fr
- Linn Habberstad : linn.habberstad@student-cs.fr

## Organisation du du code 

- ``main.py`` Runs the app

The functions that manages the UI

- ``file.py`` Uploads data on the app
- ``home.py`` Create the main window of the app
- ``organize_data.py`` Create a worksheet to save the data
- ``plot.py`` Make plots

The math functions 


- ``linage.py`` Contains the implementation of the linage functionality. 
- ``correlation.py`` 
- ``stats_function.py``
- ``interpolation.py`` 
- ``prepare_linage.py`` 
- ``data.py`` Preprocessing

A folder named 'docs' contains the final report which serves as the documentation of our sowtare. The pitch explains well how the python files interact
- ``Pitch.pdf``
- ``Final Report Climatologie.pdf``

A folder 'Tests' contains some ice cores to test the software. the variables in these files are explained in the report
- ``ODPpacifLR04exemples.txt``  
- ``EDCicecore.txt`` 



## Launch the Software 

Follow these steps:

Install the required libraries:

    pip install -Ur requirements.txt

Go into the directory src. To do that you run:

    cd src

Run``main.py``

