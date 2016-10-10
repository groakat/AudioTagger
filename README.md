AudioTagger
============

A simple program to tag wav files by drawing bounding boxes on the spectrogram.


## Quick Install

On most systems it should work to

Install Miniconda Python 2.7 distribution (http://conda.pydata.org/miniconda.html). Then type in the terminal:

    conda config --add channels https://conda.binstar.org/groakat
    conda install audiotagger-dependencies
    pip install -U https://github.com/groakat/AudioTagger/archive/master.zip

Now you can start the `AudioTagger` by opening a terminal and simply typing

    AudioTagger
    
If this does not work, please proceed reading the remainder of the README. Otherwise you are done. :)

### Using the github client
On Windows and maybe Mac OSX `git` might not be installed. Then the easiest is to install the github client and synchronize thsi repository.

Once it the repository is synchronized, open a terminal and type

    cd C:\path\to\github\AudioTagger

By replacing `C:\path\to\github\AudioTagger` with the path where the github client saved the AudioTagger repository. The folder you are looking for has a `setup/py` file. Now type

    python setup.py develop
    
You should now be able to open the AudioTagger by simply typing `AudioTagger` in the terminal. (You might have to iopen a new terminal for it to work.

## Dependencies

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




##Detailed Install Instructions

You need to

* download anaconda
* install the dependencies
* install the AudioTagger

### Downloading Anaconda

On any system, install anaconda 64bit (if possible, otherwise use 32bit and install the dependencies by hand). If you have the Enthought distro remove it.
Click the boxes that say 

1. Add to system path and variables
2. Register anaconda as the system Python 2.7

### Installing dependencies

If you have **Windows 64 bit** (all newer versions) or **OSX**, follow the instructions in the section "Installing dependencies using Conda (Windows 64bit or OSX)" and then continue with "Installing github and audioTagger".

If you have **Windows 32 bit** or **Linux**, follow the instructions in the section "Installing dependencies manually (Linux, Windows 32bit)" and then continue with "Installing github and audioTagger". 

#### Installing dependencies using Conda (Windows 64bit or OSX)

If you have **Windows 64 bit** (all newer versions) or **OSX**, you can install all dependencies within anaconda by following the following steps (then continue with the github part below):

Open a command window (Click the start button and type cmd) 
In the command window type

    conda config --add channels https://conda.binstar.org/groakat
    conda install audiotagger-dependencies
    
#### Installing dependencies manually (Linux, Windows 32bit)

If you have an 32bit version of windows, you have currently to follow this steps and install the dependencies manually:

Open a command window (Click the start button and type cmd) 
In the command window type 
    
    conda install PySide
    
followed by

    pip install https://github.com/groakat/sound4python/archive/master.zip
    
(please follow the instructions on https://github.com/groakat/sound4python to install `sox` as well.)

and finally do

    pip install https://github.com/groakat/qimage2ndarray/archive/master.zip

### Installing 

#### stable install (standard)

Open a terminal and type:

    pip install git+https://github.com/groakat/AudioTagger.git

#### github and audioTagger

Download GitHub for windows (https://windows.github.com/) or Max OSX (https://mac.github.com)
After signing in hit plus in top left to add repository
Click clone
Select groakat/AudioTagger and specify a folder on your computer to save it to e.g. `C:\Users\localadmin\projects\`. 

Now open a terminal (Windows: hit [start-key] and type `cmd` [return]) and navigate to the path you have downloaded the `AudioTagger` to using GitHub, e.g. `cd C:\Users\localadmin\projects\AudioTagger`. Now you can install the `AudioTagger` by typing

    python setup.py develop
    
To run the `AudioTagger`, open a terminal (Windows: hit [start-key] and type `cmd` [return]), and navigate to the `audioTagger.py` file. E.g. `cd C:\Users\localadmin\projects\AudioTagger\AudioTagger` and run:

    ipython audioTagger.py
    
You will then be asked for the folder containing your wav files and a folder to save you output annotations in.
