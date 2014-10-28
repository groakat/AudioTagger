import sys
import os
import csv

import scipy.io.wavfile
import numpy as np
import datetime as dt
from collections import OrderedDict
import warnings

import qimage2ndarray as qim2np

from PySide import QtCore, QtGui

from sound4python import sound4python as S4P

from AudioTagger.gui_auto import Ui_MainWindow
import AudioTagger.classDialog as CD
import AudioTagger.modifyableRect as MR
import AudioTagger.colourMap as CM



class AudioTagger(QtGui.QMainWindow):
    
    def __init__(self, basefolder=None, labelfolder=None, labelTypes=None, test=False,
                 ignoreSettings=False):
        super(AudioTagger, self).__init__()
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if test:
            return

        # self.scrollEvent = ScrollAreaEventFilter(self.scrollbarSlideEvent)
        self.mouseEventFilter = MouseFilterObj(self)
        self.KeyboardFilter = KeyboardFilterObj(self)
        self.mouseInsideFilter = MouseInsideFilterObj(self.enterGV, self.leaveGV)
        self.mouseInOverview = False

        self.shortcuts = []

        self.horzScrollbarValue = 0
        self.vertScrollbarValue = 0

        if not ignoreSettings:
            self.loadFoldersLocal()
        else:
            self.basefolder = None
            self.labelfolder = None

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
        self.soundSpeed = 1
        self.soundSpeeds = [0.1, 0.2, 0.25, 0.5, 1, 2]


        self.audibleRange = True
        self.specNStepMod = 0.01    # horizontal resolution of spectogram 0.01
        self.specNWinMod = 0.03     # vertical resolution of spectogram 0.03

        self.scrollingWithoutUser = False

        self.activeLabel = None
        self.specHeight = 360
        self.specWidth = 6000
        self.contentChanged = False
        self.isDeletingRects = False
        self.yscale = 1

        self.bgImg = None
        self.tracker = None
        self.scrollView = self.ui.scrollView
        self.viewHeight = 0
        self.viewX = 0
        self.viewY = 0
        self.viewWidth = 0
        self.viewHeight = 0
        self.setupGraphicsView()

        # self.scrollView.horizontalScrollBar().installEventFilter(self.scrollEvent)
        # self.scrollView.verticalScrollBar().installEventFilter(self.scrollEvent)

        self.scrollView.horizontalScrollBar().valueChanged.connect(self.scrollbarSlideEvent)
        self.scrollView.verticalScrollBar().valueChanged.connect(self.scrollbarSlideEvent)
        # self.installEventFilter(self.KeyboardFilter)
        self.defineShortcuts()

        self.labelRects = []
        self.rectClasses = dict()
        self.labelRect = None
        self.labelTypes = OrderedDict()
        self.cm = CM.getColourMap()
        self.rectOrgX = None
        self.rectOrgY = None
        self.isRectangleOpen = False

        self.setupLabelMenu()
        if labelTypes is None:
            if not ignoreSettings:
                self.loadSettingsLocal()
            self.contentChanged = False
        else:
            self.labelTypes = labelTypes

        self.configureElements()
        self.connectElements()
        self.show()
        # self.ui.cb_labelType.addItems(self.labelTypes.keys())

        self.openFolder(self.basefolder, self.labelfolder, self.fileidx)

        self.tracker.deactivate()
        self.deactivateAllLabelRects()

    ######################## GUI STUFF ########################
    def updateViews(self):
        self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())
        self.setZoomBoundingBox()

    def resizeEvent(self, event):
        super(AudioTagger, self).resizeEvent(event)
        self.updateViews()

    # def resize(self, *size):
    #     super(AudioTagger, self).resize(*size)
    #     try:
    #         self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())
    #     except AttributeError:
    #         pass

    def closeEvent(self, event):
        canProceed = self.checkIfSavingNecessary()
        if canProceed:
            event.accept()
        else:
            event.ignore()

    def connectElements(self):
        ## GUI elements
        self.ui.pb_next.clicked.connect(self.loadNext)
        self.ui.pb_prev.clicked.connect(self.loadPrev)
        self.ui.pb_debug.clicked.connect(self.debug)
        self.ui.pb_save.clicked.connect(self.saveSceneRects)
        self.ui.pb_toggle.clicked.connect(self.toggleLabels)
        # self.ui.pb_edit.clicked.connect(self.toggleEdit)
        self.ui.pb_play.clicked.connect(self.playPauseSound)
        self.ui.pb_stop.clicked.connect(self.stopSound)
        self.ui.pb_seek.clicked.connect(self.activateSoundSeeking)
        self.ui.cb_file.activated.connect(self.selectFromFilelist)
        self.ui.cb_create.toggled.connect(self.toogleCreateMode)
        self.ui.cb_playbackSpeed.activated.connect(self.selectPlaybackSpeed)
        self.ui.cb_specType.activated.connect(self.selectSpectrogramMode)

        ## menu
        self.ui.actionOpen_folder.triggered.connect(self.openFolder)
        self.ui.actionClass_settings.triggered.connect(self.openClassSettings)
        self.ui.actionExport_settings.triggered.connect(self.exportSettings)

    def configureElements(self):
        self.scrollView.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored)
        # self.ui.gw_overview.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        # self.scrollView.setFixedHeight(self.specHeight + 30)

        w = self.specWidth
        h = self.specHeight
        self.sceneRect = QtCore.QRectF(0, 0, w,h)
        self.overviewScene.setSceneRect(self.sceneRect)

        self.ui.cb_playbackSpeed.insertItems(0, [str(x) for x in self.soundSpeeds])
        self.ui.cb_playbackSpeed.setCurrentIndex(self.soundSpeeds.index(self.soundSpeed))


    def setupGraphicsView(self):          
        self.ui.gw_overview.setFrameStyle(QtGui.QFrame.NoFrame)
        self.overviewScene = QtGui.QGraphicsScene(self)

        # self.overviewScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

        self.ui.gw_overview.setScene(self.overviewScene)
        self.ui.gw_overview.setMouseTracking(True)
        self.ui.gw_overview.setFixedHeight(100)


        self.ui.gw_overview.installEventFilter(self.mouseInsideFilter)

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

    ##### MOVEABLE RECT
    def setupLabelMenu(self):
        wa = QtGui.QWidgetAction(self)
        self.cle = MR.ContextLineEdit(wa, self)
        self.cle.setModel(self.labelTypes.keys())

        wa.setDefaultWidget(self.cle)

        self.menu = QtGui.QMenu(self)
        delAction = self.menu.addAction("delete")
        self.menu.addAction(wa)

        delAction.triggered.connect(self.deleteLabel)
        wa.triggered.connect(self.lineEditChanged)


    def deleteLabel(self):
        self.activeLabel = self.labelRects.index(self.lastLabelRectContext)
        self.deteleActiveLabel()

    def lineEditChanged(self):
        self.menu.hide()
        c = self.cle.text()

        self.lastLabelRectContext.setColor(self.labelTypes[c])
        self.lastLabelRectContext.setInfoString(c)
        self.rectClasses[self.lastLabelRectContext] = c
        self.contentChanged = True

    def registerLastLabelRectContext(self, labelRect):
        self.lastLabelRectContext = labelRect

    def deactivateAllLabelRects(self):
        for lr in self.labelRects:
            if lr:
                lr.deactivate()

    def activateAllLabelRects(self):
        for lr in self.labelRects:
            if lr:
                lr.activate()

    def toogleCreateMode(self, createOn):
        if createOn:
            self.deactivateAllLabelRects()
        else:
            self.activateAllLabelRects()

        self.toogleTo(None)

    def labelRectChangedSlot(self):
        self.contentChanged = True


    ##### SETTINGS
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

        if settings.value("fileIdx") is None:
            self.fileidx = 0
        else:
            self.fileidx = int(settings.value("fileIdx"))

        self.updateSettings([self.labelTypes, keySequences])


    def loadFoldersLocal(self):
        settings = QtCore.QSettings()
        self.basefolder = settings.value("basefolder")
        self.labelfolder = settings.value("labelfolder")


    def exportSettings(self):
        savePath = QtGui.QFileDialog().getSaveFileName(self,
                                                       "Filename to save settings",
                                                       ".",
                                                       "Setting files (*.ini)")
        saveSettings = QtCore.QSettings(savePath[0],
                                        QtCore.QSettings.IniFormat)

        settings = QtCore.QSettings()
        settings.setFallbacksEnabled(False) # remove extra keys in Mac

        for key in settings.allKeys():
            saveSettings.setValue(key,
                                  settings.value(key))




    def openClassSettings(self):
        cd = CD.ClassDialog(self, self.labelTypes, [x.key() for x in self.shortcuts])
        cd.settingsSig.connect(self.updateSettings)
        cd.show()

    def changeLabelIdx(self, i):
        print(i)
        self.ui.cb_labelType.setCurrentIndex(i)


    def addKeySequenceToShortcuts(self, keySequence, idx):
        func = lambda: self.changeLabelIdx(idx)
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
        self.cle.setModel(self.labelTypes.keys())

        # update keyboard shortcuts
        self.updateShortcuts(keySequences)


        self.saveSettingsLocal()

    def selectFromFilelist(self, idx):
        self.loadFileIdx(idx)

    def selectPlaybackSpeed(self, idx):
        self.changePlaybackSpeed(float(self.ui.cb_playbackSpeed.itemText(idx)))

    def selectSpectrogramMode(self, idx):
        canProceed = self.checkIfSavingNecessary()

        if not canProceed:
            if idx == 0:
                self.ui.cb_specType.setCurrentIndex(1)
            elif idx == 1:
                self.ui.cb_specType.setCurrentIndex(0)
            return

        if idx == 0:
            self.changeSpectrogramModeToAudible()
        elif idx == 1:
            self.changeSpectrogramModeToUltraSonic()

        self.resetView()
        self.updateViews()

    ################### SOUND STUFF #######################
    def updateSoundMarker(self):
        markerPos = self.soundSec * (1.0 / self.specNStepMod) # 100 # multiply by step-size in SpecGen()
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
            self.scrollingWithoutUser = True
            self.scrollView.centerOn(markerPos, self.viewCenter.y())#self.soundMarker)
            self.scrollingWithoutUser = False
            self.setZoomBoundingBox(updateCenter=False)

    def changePlaybackSpeed(self, speed):
        self.soundSpeed = speed
        self.s4p.changePlaybackSpeed(self.soundSpeed)

    def activateSoundSeeking(self):
        if not self.playing:
            self.seekingSound = True

    def updateSoundPosition(self):
        currentTime = dt.datetime.now()
        increment = (currentTime - self.lastMarkerUpdate).total_seconds()
        self.soundSec += increment  * self.soundSpeed
        self.lastMarkerUpdate = currentTime

        self.ui.lbl_audio_position.setText("position: {0}".format(self.soundSec))
        self.updateSoundMarker()

    def playSound(self):
        self.playing = True
        self.ui.pb_play.setText("pause")
        self.s4p.play()
        self.soundSec = self.s4p.seekSec

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
        sec = graphicsPos * self.specNStepMod
        self.s4p.seek(sec)
        self.soundSec = sec
        self.updateSoundMarker()
        self.seekingSound = False

    def loadSound(self, wavfile):
        self.s4p.loadWav(wavfile)
        self.s4p.changePlaybackSpeed(self.soundSpeed)


    ################### WAV FILE LOAD  ######################
    def resetView(self):
        self.clearSceneRects()
        self.loadSceneRects()
        self.updateSpecLabel()
        if self.specNStepMod == 0.01 and self.specNWinMod == 0.03:
            self.ui.cb_specType.setCurrentIndex(0)
        elif  self.specNStepMod == 0.001 and self.specNWinMod == 0.003:
            self.ui.cb_specType.setCurrentIndex(1)
        else:
            warnings.warn("loaded spectrogram does not fit in preprogrammed values of audible and ultrasonic range")

        self.zoom(1)

        self.activeLabel = None

        if self.playing:
            self.stopSound()

        self.soundSec = 0
        self.updateSoundMarker()

        self.loadSound(self.filelist[self.fileidx])
        self.setWindowTitle("Audio Tagger " + os.path.basename(self.filelist[self.fileidx]))

        self.scrollView.horizontalScrollBar().triggerAction(QtGui.QAbstractSlider.SliderAction.SliderToMinimum)

        self.ui.cb_file.setCurrentIndex(self.fileidx)

        print(self.filelist[self.fileidx])

    def loadFileIdx(self, idx):
        canProceed = self.checkIfSavingNecessary()
        if not canProceed:
            return

        if idx >= 0 and idx < len(self.filelist):
            self.fileidx = idx
            self.resetView()


        settings = QtCore.QSettings()
        settings.setValue("fileIdx", self.fileidx)
        self.setZoomBoundingBox()


    def loadNext(self):
        self.loadFileIdx(self.fileidx + 1)
        # canProceed = self.checkIfSavingNecessary()
        # if not canProceed:
        #     return
        #
        # if self.fileidx < len(self.filelist) - 1:
        #     self.fileidx += 1
        #     self.resetView()
        #
        # self.setZoomBoundingBox()

    def loadPrev(self):
        self.loadFileIdx(self.fileidx - 1)
        # canProceed = self.checkIfSavingNecessary()
        # if not canProceed:
        #     return
        #
        # if self.fileidx > 0:
        #     self.fileidx -= 1
        #     self.resetView()
        #
        # self.setZoomBoundingBox()

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


    def openFolder(self, wavFolder=None, labelFolder=None, fileIdx=None):
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

        self.ui.cb_file.clear()
        self.ui.cb_file.addItems(self.filelist)

        if fileIdx:
            self.loadFileIdx(fileIdx)
        else:
            self.loadFileIdx(0)


    ####################### SPECTROGRAM #############################
    def changeSpectrogramResolution(self, nstepMod, nWinMod):
        self.specNStepMod = nstepMod    # horizontal resolution of spectogram
        self.specNWinMod = nWinMod     # vertical resolution of spectogram

    def changeSpectrogramModeToAudible(self):
        self.changeSpectrogramResolution(0.01, 0.03)

    def changeSpectrogramModeToUltraSonic(self):
        self.changeSpectrogramResolution(0.001, 0.003)

    def SpecGen(self, filepath):

        sr, x = scipy.io.wavfile.read(filepath)
    
        ## Parameters
        nstep = int(sr * self.specNStepMod)
        nwin  = int(sr * self.specNWinMod)

        print nwin
        print sr
        print self.specNWinMod

        nfft = nwin

        # Get all windows of x with length n as a single array, using strides to avoid data duplication
        #shape = (nfft, len(range(nfft, len(x), nstep)))
        shape = (nfft, ((x.shape[0] - nfft - 1)/nstep)+1)
        strides = (x.itemsize, nstep*x.itemsize)
        x_wins = np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)
    
        # Apply hamming window
        x_wins_ham = np.hamming(x_wins.shape[0])[..., np.newaxis] * x_wins
    
        # compute fft
        fft_mat = np.fft.fft(x_wins_ham, n=nfft, axis=0)[:(nfft/2), :]
    
        # log magnitude
        fft_mat_lm = np.log(np.abs(fft_mat))
    
        return fft_mat_lm.T

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
    def leaveGV(self, gv):
        if gv is self.ui.gw_overview:
            self.mouseInOverview = False
            self.tracker.deactivate()

            if not  self.ui.cb_create.checkState() \
                    == QtCore.Qt.CheckState.Checked:
                self.activateAllLabelRects()

    def enterGV(self, gv):
        if gv is self.ui.gw_overview:
            self.mouseInOverview = True
            self.tracker.activate()
            self.deactivateAllLabelRects()

    def setZoomBoundingBox(self, updateCenter=True):
        self.viewX = self.scrollView.horizontalScrollBar().value()
        areaWidth = self.scrollView.width()
        self.viewWidth = float(areaWidth)

        self.viewY = self.scrollView.verticalScrollBar().value() * (1.0 / self.yscale)

        self.viewHeight = self.scrollView.height()
        if self.viewHeight > self.specHeight  * self.yscale:
            self.viewHeight = self.specHeight * self.yscale

        self.viewHeight *= (1.0 / self.yscale)
        if updateCenter:
            self.viewCenter =  self.scrollView.mapToScene(self.scrollView.viewport().rect().center())

        self.updateZoomBoundingBox()


    def moveScrollViewSceneRect(self, pos):
        self.scrollingWithoutUser = True
        self.scrollView.fitInView(self.tracker)
        self.scrollingWithoutUser = False

    def updateZoomBoundingBox(self):
        rect = QtCore.QRectF(self.viewX, self.viewY, self.viewWidth, self.viewHeight)
        if not self.tracker:
            penCol = QtGui.QColor()
            penCol.setRgb(255, 255, 255)
            # self.tracker = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
            self.tracker = MovableGraphicsRectItem(self.moveScrollViewSceneRect)
            self.tracker.setPen(penCol)
            self.overviewScene.addItem(self.tracker)


        self.tracker.setPos(0,0)
        self.tracker.setRect(rect)

        self.ui.gw_overview.update()
        self.overviewScene.update()


    def scrollbarSlideEvent(self, tracking):
        if self.scrollingWithoutUser:
            return

        self.horzScrollbarValue = self.scrollView.horizontalScrollBar().value()
        self.vertScrollbarValue = self.scrollView.verticalScrollBar().value()

        if tracking:
            self.setZoomBoundingBox()
        else:
            self.setZoomBoundingBox(updateCenter=False)



    def clickInScene(self, x, y):
        if self.seekingSound:
            self.mouseEventFilter.isRectangleOpen = False
            self.seekSound(x)

        if self.ui.cb_create.checkState() == QtCore.Qt.CheckState.Checked:
            if not self.mouseInOverview \
            or not self.tracker.active:
                self.openSceneRectangle(x, y)
                self.isRectangleOpen = True

        else:
            self.mouseEventFilter.isRectangleOpen = False
            self.toogleToItem(self.overviewScene.itemAt(x, y),
                              centerOnActiveLabel=False)

    def releaseInScene(self):
        self.closeSceneRectangle()
        self.isRectangleOpen = False


    def openSceneRectangle(self, x, y):
        if not self.labelTypes:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("You have not specified labels yet. Please do so in File -> Class Settings.")
            msgBox.exec_()
            return

        rect = QtCore.QRectF(x, y, 0, 0)
        if self.labelRect:
            self.overviewScene.removeItem(self.labelRect)

        penCol = self.labelTypes[self.ui.cb_labelType.currentText()]
        # self.labelRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))

        self.labelRect = MR.LabelRectItem(self.menu,
                                          self.registerLastLabelRectContext,
                                          self.ui.cb_labelType.currentText(),
                                          rectChangedCallback=self.labelRectChangedSlot)
        self.labelRect.deactivate()
        self.labelRect.setRect(x, y, 1, 1)
        self.labelRect.setColor(penCol)
        self.labelRect.setResizeBoxColor(QtGui.QColor(255,255,255,50))
        self.labelRect.setupInfoTextItem(fontSize=12)
        # self.labelRect.rectChangedSignal.connect(self.labelRectChangedSlot)
        self.overviewScene.addItem(self.labelRect)

        self.rectClasses[self.labelRect] = self.ui.cb_labelType.currentText()

        self.rectOrgX = x
        self.rectOrgY = y


    def closeSceneRectangle(self):
        self.labelRects.append(self.labelRect)
        self.labelRect = None
        self.contentChanged = True
        self.rectOrgX = None
        self.rectOrgY = None

    def resizeSceneRectangle(self, x, y):
        if self.labelRect:
            if x > self.rectOrgX:
                newX = self.rectOrgX
            else:
                newX = x

            if y > self.rectOrgY:
                newY = self.rectOrgY
            else:
                newY = y

            w = np.abs(x - self.rectOrgX)
            h = np.abs(y - self.rectOrgY)

            self.labelRect.setRect(newX,
                                   newY, w, h)

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

    def getBoxCoordinates(self, r):
        """
        Function which parses coordinates of bounding boxes in .json files to x1, x2, y1, and y2 objects.

        Takes account of different methods of drawing bounding boxes, so that coordinates are correct regardless of how bounding boxes are drawn.

        Also takes account of boxes that are accidently drawn outside of the spectrogram.

        """
        if r[2]>0 and r[3]>0:
            x1 = r[0]
            x2 = r[0] + r[2]
            y1 = r[1]
            y2 = r[1] + r[3]
        elif r[2]<0 and r[3]<0:
            x1 = r[0] + r[2]
            x2 = r[0]
            y1 = r[1] + r[3]
            y2 = r[1]
        elif r[2]>0 and r[3]<0:
            x1 = r[0]
            x2 = r[0] + r[2]
            y1 = r[1] + r[3]
            y2 = r[1]
        else:
            x1 = r[0] + r[2]
            x2 = r[0]
            y1 = r[1]
            y2 = r[1] + r[3]
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if y2 > self.specHeight:
            y2 = self.specHeight
        #Transform y coordinates
        #y1 = (y1 - SpecRows)#*-1
        #y2 = (y2 - SpecRows)#*-1


        return x1, x2, y1, y2

    def convertLabelRectsToRects(self):
        labels = []
        for labelRect in self.labelRects:
            if not labelRect:
                continue

            r = [labelRect.rect().x(),
                 labelRect.rect().y(),
                 labelRect.rect().width(),
                 labelRect.rect().height()]
            # rect = [r.x(), r.y(), r.width(), r.height()]
            c = self.rectClasses[labelRect]

            freqStep = float(self.s4p.wav[0]) / self.specHeight / 2.0
            # boundingBox = self.spec[rect[0]:rect[0] + rect[2],
            #                         rect[1]:rect[1] + rect[3]]

            x1, x2, y1, y2 = self.getBoxCoordinates(r)
            boundingBox = self.spec[x1:x2, y1:y2]
            # label head:
            # (wav)Filename    Label    LabelTimeStamp     Spec_NStep
            # Spec_NWin     Spec_x1     Spec_y1     Spec_x2     Spec_y2
            # LabelStartTime_Seconds    LabelEndTime_Seconds    MinimumFreq_Hz
            # MaximumFreq_Hz    MaxAmp    MinAmp    MeanAmp
            # AmpSD LabelArea_DataPoints
            label = [
                os.path.basename(self.filelist[self.fileidx]),  # filename
                self.rectClasses[labelRect],                    # Label
                dt.datetime.now().isoformat(),                  # LabelTimeStamp
                self.specNStepMod,                              # Spec_NStep
                self.specNWinMod,                               # Spec_NWin
                x1, y1, x2, y2,                                 # Spec_x1, y1, x2, y2
                x1 * self.specNStepMod,                         # LabelStartTime_Seconds
                x2 * self.specNStepMod,                         # LabelEndTime_Seconds
                y1 * freqStep,                                  # MinimumFreq_Hz
                y2 * freqStep,                                  # MaximumFreq_Hz
                np.max(boundingBox),                            # MaxAmp
                np.min(boundingBox),                            # MinAmp
                np.mean(boundingBox),                           # MeanAmp
                np.std(boundingBox),                            # AmpSD
                (x2 - x1) * (y2 - y1)                           # LabelArea_DataPoints
                ]

            labels += [label]

        return labels

    def convertRectsToLabelRects(self, labels):
        self.clearSceneRects()

        for l in labels:
            labelIsEmpty = True

            for item in l:
                labelIsEmpty = labelIsEmpty and item == ""

            if labelIsEmpty:
                continue

            rect = QtCore.QRectF(float(l[5]), float(l[6]),
                                 float(l[7]) - float(l[5]),
                                 float(l[8]) - float(l[6]))
            c = l[1]

            self.specNStepMod = float(l[3])
            self.specNWinMod = float(l[4])

            try:
                penCol = self.labelTypes[c]
            except KeyError:                
                msgBox = QtGui.QMessageBox()
                msgBox.setText("File contained undefined class")
                msgBox.setInformativeText("Class <b>{c}</b> found in saved data. No colour for this class defined. Using standard color. Define colour in top of the source code to fix this error message".format(c=c))
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                ret = msgBox.exec_()

                penCol = QtGui.QColor()
                penCol.setRgb(0, 0, 200)

            # labelRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))



            labelRect = MR.LabelRectItem(self.menu,
                                         self.registerLastLabelRectContext,
                                         c,
                                         rectChangedCallback=self.labelRectChangedSlot)
            labelRect.setRect(rect)
            labelRect.setColor(penCol)
            labelRect.setResizeBoxColor(QtGui.QColor(255,255,255,50))
            labelRect.setupInfoTextItem(fontSize=12)
            # labelRect.rectChangedSignal.connect(self.labelRectChangedSlot)
            self.overviewScene.addItem(labelRect)


            self.labelRects += [labelRect]
            self.rectClasses[labelRect] = c


    def saveSceneRects(self, fileAppendix="-sceneRect"):
        filename = self.createLabelFilename(fileAppendix, ending='.csv')
        
        if not os.path.exists(self.labelfolder):
            os.makedirs(self.labelfolder)

        labels = self.convertLabelRectsToRects()

        with open(filename, "w") as f:
            wr = csv.writer(f, dialect='excel')
            wr.writerow(["Filename", "Label", "LabelTimeStamp", "Spec_NStep", "Spec_NWin", "Spec_x1", "Spec_y1", "Spec_x2", "Spec_y2",
                        "LabelStartTime_Seconds", "LabelEndTime_Seconds", "MinimumFreq_Hz", "MaximumFreq_Hz",
                        "MaxAmp", "MinAmp", "MeanAmp", "AmpSD", "LabelArea_DataPoints"])
            for label in labels:

                wr.writerow(label)

        self.contentChanged = False

    def loadSceneRects(self, fileAppendix="-sceneRect"):
        filename = self.createLabelFilename(fileAppendix, ending='.csv')

        if os.path.exists(filename):
            with open(filename, "r") as f:
                # dialect = csv.Sniffer().sniff(f.read(1024))
                # f.seek(0)
                reader = csv.reader(f, dialect='excel')
                rects = []
                for line in reader:
                    rects += [line]
                # rects = json.load(f)
                self.convertRectsToLabelRects(rects[1:])

        self.contentChanged = False

        if self.ui.cb_create.checkState == QtCore.Qt.CheckState.Checked:
            self.deactivateAllLabelRects()


    def createLabelFilename(self, fileAppendix="-sceneRect", ending='.json'):
        currentWavFilename = self.filelist[self.fileidx]
        if currentWavFilename.endswith('.wav'):
            filename = currentWavFilename[:-4]#Everything other than last 4 characters, i.e. .wav
        else:
            raise RuntimeError("Program only works for wav files")

        # filename += fileAppendix + ".json"
        filename += fileAppendix + ending# ".csv"
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
        if activeLabel is None:
            return

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
            self.parent.releaseInScene()
            # self.isRectangleOpen = not self.isRectangleOpen

            # if self.isRectangleOpen:
        if event.type() == QtCore.QEvent.Type.GraphicsSceneMousePress:
            self.parent.clickInScene(int(event.scenePos().x()),
                                      int( event.scenePos().y()))
            # else:
            #     self.parent.closeSceneRectangle()

        if event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
            if self.parent.isRectangleOpen:
                if event.type() == QtCore.QEvent.GraphicsSceneMouseMove:
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



# special GraphicsRectItem that is aware of its position and does something if the position is changed
class MovableGraphicsRectItem(QtGui.QGraphicsRectItem):
    """ from http://stackoverflow.com/a/24757931/2156909
    """

    def __init__(self, callback=None):
        super(MovableGraphicsRectItem, self).__init__()
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAcceptHoverEvents(True)
        self.active = False

        self.callback = callback

    def hoverEnterEvent(self, event):
        self.active = True

    def hoverLeaveEvent(self, event):
        self.active = False


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange and self.callback:
            self.callback(value)

        return super(MovableGraphicsRectItem, self).itemChange(change, value)

    def activate(self):
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def deactivate(self):
        self.setFlags(not QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setCursor(QtCore.Qt.ArrowCursor)

def main(ignoreSettings=False):
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
    w = AudioTagger(basefolder=None, labelfolder=None, labelTypes=None,
                    ignoreSettings=False)

    sys.exit(app.exec_())


class MouseInsideFilterObj(QtCore.QObject):#And this one
    def __init__(self, enterCallback, leaveCallback):
        QtCore.QObject.__init__(self)

        self.enterCallback = enterCallback
        self.leaveCallback = leaveCallback

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.Enter:
            self.enterCallback(obj)

        if event.type() == QtCore.QEvent.Type.Leave:
            self.leaveCallback(obj)

        return False


if __name__ == "__main__":
    main()
