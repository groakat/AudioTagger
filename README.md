AudioTagger
============

A simple program to tag wav files by drawing bounding boxes on the spectrogram.


Dependencies
#############

The program should run with an anaconda installation plus the following dependencies:


My fork of `sound4python` https://github.com/groakat/sound4python (please follow the readme of this project to install sox):

    pip install https://github.com/groakat/sound4python/archive/master.zip


My fork of `qimage2ndarray`:

    pip install https://github.com/groakat/qimage2ndarray/archive/master.zip

_____________________________________

General dependencies (if not anaconda is used as python distro):

    pip install numpy
    pip install scipy
    pip install PySide




##Detailed Windows Install Instructions

Install anaconda 32bit or 64bit depending on your machine (if you have the Enthought distro remove it)
Click the boxes that say 

1. Add to system path and variables
2. Register anaconda as the system Python 2.7

### Installing dependencies using Conda

If you have windows 64 bit (all newer versions), you can install all dependencies within anaconda by following the following steps (then continue with the github part below):

Open a command window (Click the start button and type cmd) 
In the command window type

    conda config --add channels https://conda.binstar.org/groakat
    conda install audiotagger-dependencies
    
### Installing dependencies manually

If you have an 32bit version of windows, you have currently to follow this steps and install the dependencies manually:

Open a command window (Click the start button and type cmd) 
In the command window type 
    
    conda install PySide
    
followed by

    pip install https://github.com/groakat/sound4python/archive/master.zip
    
(please follow the instructions on https://github.com/groakat/sound4python to install `sox` as well.)

and finally do

    pip install https://github.com/groakat/qimage2ndarray/archive/master.zip

### Installing github and audioTagger

Download GitHub for windows (https://windows.github.com/)
After signing in hit plus in top left to add repository
Click clone
Select groakat/AudioTagger and specify a folder on your computer to save it to e.g. C:\Users\localadmin\projects\

Back at the command window type

    ipython locate profile default

This will return a folder name something like:
C:\Users\user_name\.ipython\profile_default
Open the startup folder inside it e.g. C:\Users\user_name\.ipython\profile_default\startup

Create a new document inside that folder called audio_tagger.py
Open audio_tagger.py in notepad and paste the following two lines of code and save and exit:

    import sys
    sys.path.append(r"PATH_TO_DOWNLOADED_FOLDER")

where PATH_TO_DOWNLOADED_FOLDER is the path to the code you cloned the project from github (the folder containing setup.py)
e.g. sys.path.append(r"PATH_TO_DOWNLOADED_FOLDER") becomes sys.path.append(r"C:\Users\localadmin\projects\AudioTagger")

Now everthing is installed. To run the program in the command window change to the folder the project is in
e.g. cd C:\Users\localadmin\projects\AudioTagger
then run it using ipython

    ipython audioTagger.py
You will then be asked for the folder containing your wav files and a folder to save you output annotations in.
