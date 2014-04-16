import sys
import os

import scipy.io.wavfile
import scipy.misc as spmisc
import numpy as np
import pylab as plt

import qimage2ndarray as qim2np

from PySide import QtCore, QtGui

from AudioTagger.gui import Ui_MainWindow


basefolder = "C:\Users\ucfaalf\Dropbox\EngD\Projects\Acoustic analysis\Python\Amalgamated_Code\Snd_files"


class TestClass(QtGui.QMainWindow):
    
    def __init__(self, basefolder):      
        super(TestClass, self).__init__()
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scrollEvent = ScrollAreaEventFilter(self)
        self.horzScrollbarValue = 0

        self.basefolder = basefolder
        self.filelist = self.getListOfWavefiles(self.basefolder)
        self.fileidx = 0

        self.specHeight = 360

        self.bgImg = None
        self.cropRect = None
        self.scrollView = self.ui.scrollView#QtGui.QGraphicsView()
        self.setupGraphicsView()

        self.scrollView.horizontalScrollBar().installEventFilter(self.scrollEvent)

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

    def configureElements(self):
        # self.ui.scrollArea.setWidget(self.scrollView)
        self.scrollView.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored)
        self.scrollView.setFixedHeight(self.specHeight + 30)

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


    def loadNext(self):
        if self.fileidx < len(self.filelist) - 1:
            self.fileidx += 1
            self.updateSpecLabel()

    def loadPrev(self): 
        if self.fileidx > 1:
            self.fileidx -= 1
            self.updateSpecLabel()

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
        clrSpec = np.uint8(plt.cm.jet(spec / np.max(spec)) * 255)
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

        # self.scrollView.ensureVisible(0, 0, 100, 500)


        # self.scrollLabel.setPixmap(px)
        # self.scrollLabel.adjustSize()
        # self.scrollLabel.setScaledContents(True)

    def debug(self):
        print self.scrollView.horizontalScrollBar().value()
        print self.scrollView.horizontalScrollBar().pageStep()
        self.getZoomBoundingBox()

    def getZoomBoundingBox(self):
        left = self.scrollView.horizontalScrollBar().value()
        areaWidth = self.scrollView.width()
        right = float(areaWidth)
        print "left:", left, "right:", right
        self.addRectToOverview(left, right)

    def addRectToOverview(self, left, right):
        rect = QtCore.QRectF(left, 0, right, self.specHeight)
        if not self.cropRect:
            penCol = QtGui.QColor()
            penCol.setRgb(0, 0, 0)
            self.cropRect = self.overviewScene.addRect(rect, QtGui.QPen(penCol))
        else:
            self.cropRect.setRect(rect)

    def scrollbarSlideEvent(self):
        if self.horzScrollbarValue != \
        self.scrollView.horizontalScrollBar().value():
            self.horzScrollbarValue = \
                self.scrollView.horizontalScrollBar().value()

            self.getZoomBoundingBox()


class ScrollAreaEventFilter(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent
        
    def eventFilter(self, obj, event):
        if type(event) == QtCore.QDynamicPropertyChangeEvent:
            self.parent.scrollbarSlideEvent()




if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    
    w = TestClass(basefolder=basefolder)
    
    sys.exit(app.exec_())

#C:\Users\ucfaalf\Anaconda;C:\Users\ucfaalf\Anaconda\Scripts