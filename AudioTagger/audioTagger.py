import sys
import os

import scipy.io.wavfile
import scipy.misc as spmisc
import numpy as np
import pylab as plt
import json
import datetime as dt
from collections import OrderedDict

import qimage2ndarray as qim2np

from PySide import QtCore, QtGui

from sound4python import sound4python as S4P

from AudioTagger.gui_auto import Ui_MainWindow
import AudioTagger.classDialog as CD
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
import AudioTagger.colourMap as CM

# audiofolder = "/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files/"
# labelfolder = "/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files_label"



class AudioTagger(QtGui.QMainWindow):
    
    def __init__(self, basefolder=None, labelfolder=None, labelTypes=None):
        super(AudioTagger, self).__init__()
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scrollEvent = ScrollAreaEventFilter(self.scrollbarSlideEvent)
        self.mouseEventFilter = MouseFilterObj(self)
        self.KeyboardFilter = KeyboardFilterObj(self)
        self.shortcuts = []

        self.horzScrollbarValue = 0
        self.vertScrollbarValue = 0

        self.loadFoldersLocal()

        if basefolder:
            self.basefolder = basefolder

        if labelfolder:
            self.labelfolder = labelfolder


        self.fileidx = 0
        # self.filelist = self.getListOfWavefiles(self.basefolder)

        self.s4p = S4P.Sound4Python()
        self.soundSec = 0
        self.lastMarkerUpdate = None
        self.soundMarker = None
        self.seekingSound = False
        self.playing = False
        self.soundTimer = QtCore.QTimer()
        self.soundTimer.timeout.connect(self.updateSoundPosition)

        self.activeLabel = None
        self.specHeight = 360
        self.specWidth = 6000
        self.contentChanged = False
        self.isDeletingRects = False
        self.yscale = 1

        self.bgImg = None
        self.cropRect = None
        self.scrollView = self.ui.scrollView
        self.viewHeight = 0
        self.viewX = 0
        self.viewY = 0
        self.viewWidth = 0
        self.viewHeight = 0
        self.setupGraphicsView()

        self.scrollView.horizontalScrollBar().installEventFilter(self.scrollEvent)
        self.scrollView.verticalScrollBar().installEventFilter(self.scrollEvent)
        # self.installEventFilter(self.KeyboardFilter)
        self.defineShortcuts()

        self.labelRects = []
        self.rectClasses = dict()
        self.labelRect = None
        self.labelTypes = OrderedDict()
        self.cm = CM.getColourMap()

        if labelTypes is None:
            self.loadSettingsLocal()
            self.contentChanged = False
        else:
            self.labelTypes = labelTypes

        self.configureElements()
        self.connectElements()
        self.show()
        # self.ui.cb_labelType.addItems(self.labelTypes.keys())

        self.openFolder(self.basefolder, self.labelfolder)

    ######################## GUI STUFF ########################
    def resizeEvent(self, event):
        super(AudioTagger, self).resizeEvent(event)
        self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())
        self.setZoomBoundingBox()

    # def resize(self, *size):
    #     super(AudioTagger, self).resize(*size)
    #     try:
    #         self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())
    #     except AttributeError:
    #         pass
    #
    # def closeEvent(self, event):
    #     canProceed = self.checkIfSavingNecessary()
    #     if canProceed:
    #         event.accept()
    #     else:
    #         event.ignore()

    def connectElements(self):
        self.ui.pb_next.clicked.connect(self.loadNext)
        self.ui.pb_prev.clicked.connect(self.loadPrev)
        self.ui.pb_debug.clicked.connect(self.debug)
        self.ui.pb_save.clicked.connect(self.saveSceneRects)
        self.ui.pb_toggle.clicked.connect(self.toggleLabels)
        self.ui.pb_delete.clicked.connect(self.deteleActiveLabel)
        self.ui.actionOpen_folder.triggered.connect(self.openFolder)
        self.ui.actionClass_settings.triggered.connect(self.openClassSettings)
        self.ui.pb_play.clicked.connect(self.playPauseSound)
        self.ui.pb_stop.clicked.connect(self.stopSound)
        self.ui.pb_seek.clicked.connect(self.activateSoundSeeking)

    def configureElements(self):
        self.scrollView.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored)
        # self.ui.gw_overview.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        # self.scrollView.setFixedHeight(self.specHeight + 30)

        w = self.specWidth
        h = self.specHeight
        self.sceneRect = QtCore.QRectF(0, 0, w,h)
        self.overviewScene.setSceneRect(self.sceneRect)


    def setupGraphicsView(self):          
        self.ui.gw_overview.setFrameStyle(QtGui.QFrame.NoFrame)
        self.overviewScene = QtGui.QGraphicsScene(self)

        # self.overviewScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

        self.ui.gw_overview.setScene(self.overviewScene)
        self.ui.gw_overview.setMouseTracking(True)
        self.ui.gw_overview.setFixedHeight(100)

        self.scrollView.setScene(self.overviewScene)
        self.scrollView.setMouseTracking(True)

        self.overviewScene.installEventFilter(self.mouseEventFilter)

    def zoom(self, yscale):
        self.yscale *= yscale
        self.scrollView.scale(1, yscale)

        self.ui.lbl_zoom.setText("Vertical zoom: {0:.1f}x".format(self.yscale))
        self.setZoomBoundingBox()

    def selectLabel0(self):
        self.ui.cb_labelType.setCurrentIndex(0)

    def selectLabel1(self):
        self.ui.cb_labelType.setCurrentIndex(1)

    def selectLabel2(self):
        self.ui.cb_labelType.setCurrentIndex(2)

    def defineShortcuts(self):        
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), 
                        self, self.loadNext)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), 
                        self, self.loadPrev)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Tab), 
                        self, self.toggleLabels)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S), 
                        self, self.saveSceneRects)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), 
                        self, self.deteleActiveLabel)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), 
                        self, self.abortSceneRectangle)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space),
                        self, self.playPauseSound)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S),
                        self, self.activateSoundSeeking)

        zoomIn = lambda: None is self.zoom(2.0)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Plus),
                        self, zoomIn)
        zoomOut = lambda: None is self.zoom(0.5)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Minus),
                        self, zoomOut)


    def saveSettingsLocal(self):
        print "saveSettingsLocal"
        labelTypes = []
        while True:
            try:
                k, c = self.labelTypes.popitem(last=False)
                labelTypes += [[k, c]]
            except KeyError:
                break

        for k, c in labelTypes:
            self.labelTypes[k] = c

        keySequences = []
        for shortcut in self.shortcuts:
            keySequences += [shortcut.key()]


        settings = QtCore.QSettings()
        settings.setValue("labelTypes", labelTypes)
        settings.setValue("keySequences", keySequences)


    def saveFoldersLocal(self):
        settings = QtCore.QSettings()
        settings.setValue("basefolder", self.basefolder)
        settings.setValue("labelfolder", self.labelfolder)



    def loadSettingsLocal(self):
        settings = QtCore.QSettings()
        lt = settings.value("labelTypes")
        if lt is None:
            # no settings found
            return

        self.labelTypes = OrderedDict()
        for k, i in lt:
            self.labelTypes[k] = i


        keySequences = settings.value("keySequences")
        self.updateSettings([self.labelTypes, keySequences])


    def loadFoldersLocal(self):
        settings = QtCore.QSettings()
        self.basefolder = settings.value("basefolder")
        self.labelfolder = settings.value("labelfolder")


    def openClassSettings(self):
        cd = CD.ClassDialog(self, self.labelTypes, [x.key() for x in self.shortcuts])
        cd.settingsSig.connect(self.updateSettings)
        cd.show()

    def changeIdx(self, i):
        print(i)
        self.ui.cb_labelType.setCurrentIndex(i)


    def addKeySequenceToShortcuts(self, keySequence, idx):
        func = lambda: self.changeIdx(idx)
        self.shortcuts += [QtGui.QShortcut(keySequence, self, func)]

    def updateShortcuts(self, keySequences):
        for idx, keySequence in enumerate(keySequences):
            if idx < len(self.shortcuts) - 1:
                self.shortcuts[idx].setKey(keySequence)
            else:
                self.addKeySequenceToShortcuts(keySequence, idx)

            self.shortcuts[idx].setEnabled(True)

        # disable all shortcuts that do not have corresponding class
        if len(keySequences) < len(self.shortcuts):
            for i in range(len(keySequences), len(self.shortcuts)):
                self.shortcuts[i].setEnabled(False)


    def updateSettings(self, settings):
        self.labelTypes = settings[0]
        keySequences = settings[1]

        cc = self.contentChanged
        # update all label colours by forcing a redraw
        self.convertRectsToLabelRects(self.convertLabelRectsToRects())
        self.contentChanged = cc

        for i in range(self.ui.cb_labelType.count()):
            self.ui.cb_labelType.removeItem(0)

        self.ui.cb_labelType.addItems(self.labelTypes.keys())

        # update keyboard shortcuts
        self.updateShortcuts(keySequences)


        self.saveSettingsLocal()

    ################### SOUND STUFF #######################
    def updateSoundMarker(self):
        markerPos = self.soundSec * 100 # multiply by step-size in SpecGen()
        line = QtCore.QLineF(markerPos, 0, markerPos, self.specHeight)
        if not self.soundMarker:
            penCol = QtGui.QColor()
            penCol.setRgb(255, 0, 0)
            self.soundMarker = self.overviewScene.addLine(line, QtGui.QPen(penCol))
        else:
            self.soundMarker.setLine(line)

        self.ui.gw_overview.update()
        self.overviewScene.update()

        if self.ui.cb_followSound.isChecked():
            self.scrollView.centerOn(markerPos, self.viewCenter.y())#self.soundMarker)
            self.setZoomBoundingBox(updateCenter=False)

    def activateSoundSeeking(self):
        if not self.playing:
            self.seekingSound = True

    def updateSoundPosition(self):
        currentTime = dt.datetime.now()
        increment = (currentTime - self.lastMarkerUpdate).total_seconds()
        self.soundSec += increment
        self.lastMarkerUpdate = currentTime

        self.ui.lbl_audio_position.setText("position: {0}".format(self.soundSec))
        self.updateSoundMarker()

    def playSound(self):
        self.playing = True
        self.ui.pb_play.setText("pause")
        self.s4p.play()
        self.soundSec = self.s4p.sec

        self.lastMarkerUpdate = dt.datetime.now()
        self.soundTimer.start(100)

    def pauseSound(self):
        self.playing = False
        self.ui.pb_play.setText("play")
        self.s4p.pause()
        self.soundTimer.stop()

    def playPauseSound(self):
        if self.playing:
            self.pauseSound()
        else:
            self.playSound()

    def stopSound(self):
        self.playing = False
        self.ui.pb_play.setText("play")
        self.s4p.stop()
        self.soundTimer.stop()

    def seekSound(self, graphicsPos):
        sec = graphicsPos / 100.0
        self.s4p.seek(sec)
        self.soundSec = sec
        self.updateSoundMarker()
        self.seekingSound = False

    def loadSound(self, wavfile):
        self.s4p.loadWav(wavfile)


    ################### WAV FILE LOAD  ######################
    def resetView(self):
        self.clearSceneRects()
        self.updateSpecLabel()
        self.loadSceneRects()
        self.zoom(1)

        self.activeLabel = None

        if self.playing:
            self.stopSound()

        self.soundSec = 0
        self.updateSoundMarker()

        self.loadSound(self.filelist[self.fileidx])
        self.setWindowTitle("Audio Tagger " + os.path.basename(self.filelist[self.fileidx]))

        self.scrollView.horizontalScrollBar().triggerAction(QtGui.QAbstractSlider.SliderAction.SliderToMinimum)

        print(self.filelist[self.fileidx])


    def loadNext(self):
        canProceed = self.checkIfSavingNecessary()
        if not canProceed:
            return

        if self.fileidx < len(self.filelist) - 1:
            self.fileidx += 1
            self.resetView()

        self.setZoomBoundingBox()

    def loadPrev(self): 
        canProceed = self.checkIfSavingNecessary()
        if not canProceed:
            return

        if self.fileidx > 0:
            self.fileidx -= 1
            self.resetView()

        self.setZoomBoundingBox()

    def updateSpecLabel(self):
        self.spec = self.SpecGen(self.filelist[self.fileidx])
        self.updateLabelWithSpectrogram(self.spec)
        self.specHeight = self.spec.shape[1]
        self.specWidth = self.spec.shape[0]
        self.configureElements()


    def getListOfWavefiles(self, folder):
        fileList = []
        for root, dirs, files in os.walk(folder):
            for f in sorted(files):
                if f.endswith(".wav"):
                    fileList += [os.path.join(root, f)]
                    
        return fileList


    def openFolder(self, wavFolder=None, labelFolder=None):
        if wavFolder is None:
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.Directory)
            wavFolder = dialog.getExistingDirectory(self,
                        "Open Folder with wav files",
                        "/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/")

        self.filelist = self.getListOfWavefiles(wavFolder)
        self.basefolder = wavFolder

        if labelFolder is None:
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.Directory)
            labelFolder = dialog.getExistingDirectory(self,
                        "Open Folder with label files",
                        os.path.split(wavFolder)[0])

        self.labelfolder = labelFolder

        if len(self.filelist) == 0:
            return

        self.saveFoldersLocal()

        self.fileidx = -1
        self.loadNext()


    ####################### SPECTROGRAM #############################
    def SpecGen(self, filepath):
        sr,x = scipy.io.wavfile.read(filepath)

        ## Parameters: 10ms step, 30ms window
        nstep = int(sr * 0.01)
        nwin  = int(sr * 0.03)
        nfft = nwin

        window = np.hamming(nwin)

        ## will take windows x[n1:n2].  generate
        ## and loop over n2 such that all frames
        ## fit within the waveform
        nn = range(nwin, len(x), nstep)

        X = np.zeros( (len(nn), nfft/2) )

        for i,n in enumerate(nn):
            xseg = x[n-nwin:n]
            z = np.fft.fft(window * xseg, nfft)
            X[i,:] = np.log(np.abs(z[:nfft/2]))
        
        return X

    def updateLabelWithSpectrogram(self, spec):
        # clrSpec = np.uint8(plt.cm.binary(spec / np.max(spec)) * 255)#To change color, alter plt.cm.jet to plt.cm.#alternative code#
        clrSpec = np.uint8(self.cm(spec / 18.0) * 255)#To change color, alter plt.cm.jet to plt.cm.#alternative code#
        clrSpec = np.rot90(clrSpec, 1)
        # clrSpec = spmisc.imresize(clrSpec, 0.25)
        qi = qim2np.array2qimage(clrSpec)#converting from numpy array to qt image
        self.setBackgroundImage(qi)

    def setBackgroundImage(self, qi):
        px = QtGui.QPixmap().fromImage(qi)   
        if self.bgImg:
            self.overviewScene.removeItem(self.bgImg)

        self.bgImg = QtGui.QGraphicsPixmapItem(px)#Change Qt array to a Qt graphic
        self.overviewScene.addItem(self.bgImg)
        self.bgImg.setZValue(-100)#Ensure spectrogram graphic is displayed as background
        self.bgImg.setPos(0,0)   

        self.ui.gw_overview.ensureVisible(self.bgImg)
        self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())

    def debug(self):
        self.isDeletingRects = not self.isDeletingRects
        print self.isDeletingRects


    #################### VISUALZATION/ INTERACTION (GRAPHICVIEWS) #######################
    def setZoomBoundingBox(self, updateCenter=True):
        self.viewX = self.scrollView.horizontalScrollBar().value()
        areaWidth = self.scrollView.width()
        self.viewWidth = float(areaWidth)

        self.viewY = self.scrollView.verticalScrollBar().value() * (1.0 / self.yscale)

        self.viewHeight = self.scrollView.height()
        if self.viewHeight > self.specHeight:
            self.viewHeight = self.specHeight

        self.viewHeight *= (1.0 / self.yscale)
        if updateCenter:
            self.viewCenter =  self.scrollView.mapToScene(self.scrollView.viewport().rect().center())

        self.updateZoomBoundingBox()

    def updateZoomBoundingBox(self):
        rect = QtCore.QRectF(self.viewX, self.viewY, self.viewWidth, self.viewHeight)
        if not self.cropRect:
            penCol = QtGui.QColor()
            penCol.setRgb(255, 255, 255)
            self.cropRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
        else:
            self.cropRect.setRect(rect)

        self.ui.gw_overview.update()
        self.overviewScene.update()


    def scrollbarSlideEvent(self):
        self.horzScrollbarValue = self.scrollView.horizontalScrollBar().value()
        self.vertScrollbarValue = self.scrollView.verticalScrollBar().value()

        self.setZoomBoundingBox()



    def clickInScene(self, x, y):
        if self.seekingSound:
            self.mouseEventFilter.isRectangleOpen = False
            self.seekSound(x)

        if not self.ui.cb_create.checkState():
            self.mouseEventFilter.isRectangleOpen = False
            self.toogleToItem(self.overviewScene.itemAt(x, y), 
                              centerOnActiveLabel=False)
        else:
            self.openSceneRectangle(x, y)

    def openSceneRectangle(self, x, y):
        rect = QtCore.QRectF(x, y, 0, 0)
        if self.labelRect:
            self.overviewScene.removeItem(self.labelRect)

        penCol = self.labelTypes[self.ui.cb_labelType.currentText()]
        self.labelRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
        self.rectClasses[self.labelRect] = self.ui.cb_labelType.currentText()


    def closeSceneRectangle(self):
        self.labelRects.append(self.labelRect)
        self.labelRect = None
        self.contentChanged = True

    def resizeSceneRectangle(self, x, y):
        if self.labelRect:
            orgX = self.labelRect.rect().x()
            orgY = self.labelRect.rect().y()
            w = x - orgX
            h = y - orgY
            self.labelRect.setRect(orgX,
                                   orgY, w, h)

    def abortSceneRectangle(self):
        self.overviewScene.removeItem(self.labelRect)
        self.labelRect = None
        self.mouseEventFilter.isRectangleOpen = False

    def clearSceneRects(self):        
        if self.labelRect:
            self.overviewScene.removeItem(self.labelRect)

        self.mouseEventFilter.isRectangleOpen = False

        for labelRect in self.labelRects:
            self.overviewScene.removeItem(labelRect)

        self.labelRects = []
        self.contentChanged = True


    ################### LABELS (SAVE/LOAD/NAVIGATION) #########################
    def convertLabelRectsToRects(self):
        labels = []
        for labelRect in self.labelRects:
            r = labelRect.rect()
            rect = [r.x(), r.y(), r.width(), r.height()]
            c = self.rectClasses[labelRect]
            labels += [[rect, c]]

        return labels

    def convertRectsToLabelRects(self, labels):
        self.clearSceneRects()

        for r, c in labels:
            rect = QtCore.QRectF(*r)#Ask Peter again what the * means

            try:
                penCol = self.labelTypes[c]
            except ValueError:                
                msgBox = QtGui.QMessageBox()
                msgBox.setText("File contained undefined class")
                msgBox.setInformativeText("Class <b>{c}</b> found in saved data. No colour for this class defined. Using standard color. Define colour in top of the source code to fix this error message".format(c=c))
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                ret = msgBox.exec_()

                penCol = QtGui.QColor()
                penCol.setRgb(0, 0, 200)

            labelRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
            self.labelRects += [labelRect]
            self.rectClasses[labelRect] = c


    def saveSceneRects(self, fileAppendix="-sceneRect"):
        filename = self.createLabelFilename(fileAppendix)
        
        if not os.path.exists(self.labelfolder):
            os.makedirs(self.labelfolder)

        with open(filename, "w") as f:
            rects = self.convertLabelRectsToRects()
            json.dump(rects, f)

        self.contentChanged = False

    def loadSceneRects(self, fileAppendix="-sceneRect"):
        filename = self.createLabelFilename(fileAppendix)

        if os.path.exists(filename):
            with open(filename, "r") as f:
                rects = json.load(f)
                self.convertRectsToLabelRects(rects)

        self.contentChanged = False

    def createLabelFilename(self, fileAppendix="-sceneRect"):        
        currentWavFilename = self.filelist[self.fileidx]
        if currentWavFilename.endswith('.wav'):
            filename = currentWavFilename[:-4]#Everything other than last 4 characters, i.e. .wav
        else:
            raise RuntimeError("Program only works for wav files")

        filename += fileAppendix + ".json"
        filename = os.path.basename(filename)
        filename = os.path.join(self.labelfolder, filename)

        return filename


    def toggleLabels(self):
        if self.activeLabel is None: #iF nothing is selected, highlight the [0] index label when toggle button pressed
            activeLabel = 0
        else:
            activeLabel = (self.activeLabel + 1) % len(self.labelRects) #Move label index by 1 with every toggle button press

        self.toogleTo(activeLabel)


    def toogleTo(self, activeLabel, centerOnActiveLabel=True):
        if self.activeLabel is not None:
            penCol = self.labelTypes[self.rectClasses[self.labelRects[self.activeLabel]]]
            pen = QtGui.QPen(penCol)
            self.labelRects[self.activeLabel].setPen(pen)

        self.activeLabel = activeLabel

        print "toggling to", self.activeLabel, len(self.labelRects)
        penCol = QtGui.QColor()
        penCol.setRgb(255, 255, 255)
        pen = QtGui.QPen(penCol)
        self.labelRects[self.activeLabel].setPen(pen)

        if centerOnActiveLabel:
            self.scrollView.centerOn(self.labelRects[self.activeLabel])
            self.setZoomBoundingBox()


    def toogleToItem(self, item, centerOnActiveLabel=True):
        itemIdx = self.labelRects.index(item)
        self.toogleTo(itemIdx, centerOnActiveLabel)

    def deteleActiveLabel(self):
        if self.activeLabel is None:
            return

        labelRect = self.labelRects.pop(self.activeLabel)
        self.overviewScene.removeItem(labelRect)        

        self.activeLabel = None

        self.contentChanged = True

    def checkIfSavingNecessary(self):
        if self.contentChanged:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Save |
                                      QtGui.QMessageBox.Discard |
                                      QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Save)
            ret = msgBox.exec_()

            if ret == QtGui.QMessageBox.Save:
                self.saveSceneRects()
                return True
            elif ret == QtGui.QMessageBox.Discard:
                return True
            elif ret == QtGui.QMessageBox.Cancel:
                return False
            else:
                return True
                # should never be reached
        else:
            return True


class ScrollAreaEventFilter(QtCore.QObject):#Ask Peter why these are seperate classes?
    def __init__(self, callback):
        QtCore.QObject.__init__(self)
        self.callback = callback
        
    def eventFilter(self, obj, event):
        if type(event) == QtCore.QDynamicPropertyChangeEvent \
        or event.type() == QtCore.QEvent.Type.MouseMove:
            self.callback()


class MouseFilterObj(QtCore.QObject):#And this one
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.isRectangleOpen = False
        
    def eventFilter(self, obj, event):
        # print event.type()

        if event.type() == QtCore.QEvent.Type.GraphicsSceneMouseRelease:
            self.isRectangleOpen = not self.isRectangleOpen

            if self.isRectangleOpen:
                self.parent.clickInScene(int(event.scenePos().x()), 
                                          int( event.scenePos().y()))
            else:
                self.parent.closeSceneRectangle()

        if event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
            if self.isRectangleOpen:
                if (event.type() == QtCore.QEvent.GraphicsSceneMouseMove):
                    self.parent.resizeSceneRectangle(int(event.scenePos().x()), 
                                                    int( event.scenePos().y()))

        return False

class KeyboardFilterObj(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent
        
    def eventFilter(self, obj, event):
        # print event.type()
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key_Tab:
                self.parent.toggleLabels()
            elif event.key() == QtCore.Qt.Key_Left:
                self.parent.loadPrev()
            elif event.key() == QtCore.Qt.Key_Right:
                self.parent.loadNext()

            else:
                print event.key()


if __name__ == "__main__":
    labelTypes = OrderedDict()

    penCol = QtGui.QColor()
    penCol.setRgb(96, 96, 96)
    labelTypes["bat"] = penCol

    penCol = QtGui.QColor()
    penCol.setRgb(51, 51, 255)
    labelTypes["bird"] = penCol

    penCol = QtGui.QColor()
    penCol.setRgb(255, 0, 127)
    labelTypes["plane"] = penCol

    penCol = QtGui.QColor()
    penCol.setRgb(255, 0, 255)
    labelTypes["car"] = penCol

    audiofolder = "C:\Users\ucfaalf\Dropbox\EngD\Projects\Acoustic analysis\Python\Amalgamated_Code\Snd_files"
    labelfolder = "C:\Users\ucfaalf\Dropbox\EngD\Projects\Acoustic analysis\Python\Amalgamated_Code\Snd_files_label"


    app = QtGui.QApplication(sys.argv)

    app.setOrganizationName("UCL")
    app.setOrganizationDomain("https://github.com/groakat/AudioTagger")
    app.setApplicationName("audioTagger")

    # w = AudioTagger(basefolder=audiofolder, labelfolder=labelfolder, labelTypes=labelTypes)
    # w = AudioTagger(basefolder=audiofolder, labelfolder=labelfolder, labelTypes=None)
    w = AudioTagger(basefolder=None, labelfolder=None, labelTypes=None)
    
    sys.exit(app.exec_())

#C:\Users\ucfaalf\Anaconda;C:\Users\ucfaalf\Anaconda\Scripts