import sys
import os

import scipy.io.wavfile
import scipy.misc as spmisc
import numpy as np
import pylab as plt
import json

import qimage2ndarray as qim2np

from PySide import QtCore, QtGui

from AudioTagger.gui import Ui_MainWindow

#
# audiofolder = "C:\Users\ucfaalf\Dropbox\EngD\Projects\Acoustic analysis\Python\Amalgamated_Code\Snd_files"
# labelfolder = "C:\Users\ucfaalf\Dropbox\EngD\Projects\Acoustic analysis\Python\Amalgamated_Code\Snd_files_label"


audiofolder = "/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files/"
labelfolder = "/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files_label"

labelTypes = ["bat",
              "bird",
              "plane"]

labelColours = []

penCol = QtGui.QColor()
penCol.setRgb(0, 0, 200)
labelColours += [penCol]

penCol = QtGui.QColor()
penCol.setRgb(200, 0, 200)
labelColours += [penCol]

penCol = QtGui.QColor()
penCol.setRgb(0, 200, 200)
labelColours += [penCol]


class TestClass(QtGui.QMainWindow):
    
    def __init__(self, basefolder, labelfolder):      
        super(TestClass, self).__init__()
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scrollEvent = ScrollAreaEventFilter(self)
        self.mouseEventFilter = MouseFilterObj(self)

        self.horzScrollbarValue = 0

        self.basefolder = basefolder
        self.labelfolder = labelfolder
        self.filelist = self.getListOfWavefiles(self.basefolder)
        self.fileidx = 0

        self.activeLabel = None
        self.specHeight = 360
        self.contentChanged = False
        self.isDeletingRects = False

        self.bgImg = None
        self.cropRect = None
        self.scrollView = self.ui.scrollView
        self.setupGraphicsView()

        self.scrollView.horizontalScrollBar().installEventFilter(self.scrollEvent)

        self.labelRects = []
        self.rectClasses = dict()
        self.labelRect = None
        self.configureElements()
        self.connectElements()
        self.show()

    def resizeEvent(self, event):
        super(TestClass, self).resizeEvent(event)        
        self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())

    def connectElements(self):
        self.ui.pb_next.clicked.connect(self.loadNext)
        self.ui.pb_prev.clicked.connect(self.loadPrev)
        self.ui.pb_debug.clicked.connect(self.debug)
        self.ui.pb_save.clicked.connect(self.saveSceneRects)
        self.ui.pb_load.clicked.connect(self.loadSceneRects)
        self.ui.pb_toggle.clicked.connect(self.toggleLabels)
        self.ui.pb_delete.clicked.connect(self.deteleActiveLabel)

    def configureElements(self):
        self.scrollView.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored)
        self.scrollView.setFixedHeight(self.specHeight + 30)
        self.ui.cb_labelType.addItems(labelTypes)

    def setupGraphicsView(self):
        w = 6000
        h = self.specHeight
        self.sceneRect = QtCore.QRectF(0, 0, w,h)
          
        self.ui.gw_overview.setFrameStyle(QtGui.QFrame.NoFrame)
        self.overviewScene = QtGui.QGraphicsScene(self)

        self.overviewScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.overviewScene.setSceneRect(self.sceneRect)

        self.ui.gw_overview.setScene(self.overviewScene)
        self.scrollView.setScene(self.overviewScene)
        self.scrollView.setMouseTracking(True)

        self.overviewScene.installEventFilter(self.mouseEventFilter)


    def loadNext(self):
        canProceed = self.checkIfSavingNecessary()
        if not canProceed:
            return

        self.clearSceneRects()
        if self.fileidx < len(self.filelist) - 1:
            self.fileidx += 1
            self.updateSpecLabel()

        self.loadSceneRects()

    def loadPrev(self): 
        canProceed = self.checkIfSavingNecessary()
        if not canProceed:
            return

        self.clearSceneRects()
        if self.fileidx > 1:
            self.fileidx -= 1
            self.updateSpecLabel()

        self.loadSceneRects()

    def updateSpecLabel(self):
        self.spec = self.SpecGen(self.filelist[self.fileidx])
        self.updateLabelWithSpectrogram(self.spec)


    def getListOfWavefiles(self, folder):
        fileList = []
        for root, dirs, files in os.walk(folder):
            for f in sorted(files):
                if f.endswith(".wav"):
                    fileList += [os.path.join(root, f)]
                    
        return fileList

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
        clrSpec = np.uint8(plt.cm.jet(spec / np.max(spec)) * 255)#T change color, alter plt.cm.jet to plt.cm.#alternative code#
        clrSpec = np.rot90(clrSpec, 1)
        # clrSpec = spmisc.imresize(clrSpec, 0.25)
        qi = qim2np.array2qimage(clrSpec)#converting from numpy array to qt image
        self.setBackgroundImage(qi)

    def setBackgroundImage(self, qi):
        px = QtGui.QPixmap().fromImage(qi)   
        if self.bgImg:
            self.overviewScene.removeItem(self.bgImg)

        self.bgImg = QtGui.QGraphicsPixmapItem(px)
        self.overviewScene.addItem(self.bgImg)
        self.bgImg.setZValue(-100)
        self.bgImg.setPos(0,0)   

        self.ui.gw_overview.ensureVisible(self.bgImg)
        self.ui.gw_overview.fitInView(self.overviewScene.itemsBoundingRect())

    def debug(self):
        self.isDeletingRects = not self.isDeletingRects
        print self.isDeletingRects

    def getZoomBoundingBox(self):
        left = self.scrollView.horizontalScrollBar().value()
        areaWidth = self.scrollView.width()
        right = float(areaWidth)
        self.addRectToOverview(left, right)

    def addRectToOverview(self, left, right):
        rect = QtCore.QRectF(left, 0, right, self.specHeight)
        if not self.cropRect:
            penCol = QtGui.QColor()
            penCol.setRgb(0, 0, 0)
            self.cropRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
        else:
            self.cropRect.setRect(rect)

        self.ui.gw_overview.update()
        self.overviewScene.update()


    def scrollbarSlideEvent(self):
        if self.horzScrollbarValue != \
        self.scrollView.horizontalScrollBar().value():
            self.horzScrollbarValue = \
                self.scrollView.horizontalScrollBar().value()

            self.getZoomBoundingBox()

    def clickInScene(self, x, y):
        if not self.ui.cb_create.checkState():
            self.mouseEventFilter.isRectangleOpen = False
            self.toogleToItem( self.overviewScene.itemAt(x, y))
        else:
            self.openSceneRectangle(x, y)

    def openSceneRectangle(self, x, y):
        rect = QtCore.QRectF(x, y, 0, 0)
        if self.labelRect:
            self.overviewScene.removeItem(self.labelRect)

        penCol = labelColours[self.ui.cb_labelType.currentIndex()]
        self.labelRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
        self.rectClasses[self.labelRect] = self.ui.cb_labelType.currentIndex()


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

    def clearSceneRects(self):        
        if self.labelRect:
            self.overviewScene.removeItem(self.labelRect)

        self.mouseEventFilter.isRectangleOpen = False

        for labelRect in self.labelRects:
            self.overviewScene.removeItem(labelRect)

        self.labelRects = []
        self.contentChanged = True

    def convertLabelRectsToRects(self):
        labels = []
        for labelRect in self.labelRects:
            r = labelRect.rect()
            rect = [r.x(), r.y(), r.width(), r.height()]
            c = labelTypes[self.rectClasses[labelRect]]
            labels += [[rect, c]]

        return labels

    def convertRectsToLabelRects(self, labels):
        self.clearSceneRects()

        for r, c in labels:
            rect = QtCore.QRectF(*r)

            try:
                classIdx = labelTypes.index(c)
                penCol = labelColours[classIdx]
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
            self.rectClasses[labelRect] = labelTypes.index(c)


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
            filename = currentWavFilename[:-4]
        else:
            raise RuntimeError("Program only works for wav files")

        filename += fileAppendix + ".json"
        filename = os.path.basename(filename)
        filename = os.path.join(self.labelfolder, filename)

        return filename


    def toggleLabels(self):
        if self.activeLabel is None:
            activeLabel = 0
        else:
            activeLabel = (self.activeLabel + 1) % len(self.labelRects)

        self.toogleTo(activeLabel)


    def toogleTo(self, activeLabel):
        if self.activeLabel is not None:
            penCol = labelColours[self.rectClasses[self.labelRects[self.activeLabel]]]
            pen = QtGui.QPen(penCol)
            self.labelRects[self.activeLabel].setPen(pen)

        self.activeLabel = activeLabel

        print "toggling to", self.activeLabel, len(self.labelRects)
        penCol = QtGui.QColor()
        penCol.setRgb(200, 0, 0)
        pen = QtGui.QPen(penCol)
        self.labelRects[self.activeLabel].setPen(pen)

        self.scrollView.centerOn(self.labelRects[self.activeLabel])


    def toogleToItem(self, item):
        itemIdx = self.labelRects.index(item)
        self.toogleTo(itemIdx)

    def deteleActiveLabel(self):
        labelRect = self.labelRects.pop(self.activeLabel)
        self.overviewScene.removeItem(labelRect)        

        if self.activeLabel >= len(self.labelRects):
            self.activeLabel = len(self.labelRects) - 1

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


class ScrollAreaEventFilter(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent
        
    def eventFilter(self, obj, event):
        if type(event) == QtCore.QDynamicPropertyChangeEvent \
        or event.type() == QtCore.QEvent.Type.MouseMove:
            self.parent.scrollbarSlideEvent()


class MouseFilterObj(QtCore.QObject):
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

            
        # if (event.type() == QtCore.QEvent.Leave):
        #     self.parent.setCropCenter(None, None, increment=self.increment)
            
        # if (event.type() == QtCore.QEvent.GraphicsSceneWheel):
        #     self.increment -= event.delta()
            
        return False



if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    
    w = TestClass(basefolder=audiofolder, labelfolder=labelfolder)
    
    sys.exit(app.exec_())

#C:\Users\ucfaalf\Anaconda;C:\Users\ucfaalf\Anaconda\Scripts