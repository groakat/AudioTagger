__author__ = 'peter'

import sys
import warnings
from collections import OrderedDict

from qimage2ndarray.qt_driver import QtDriver

qt = QtDriver()

QtCore = qt.QtCore
QtGui = qt.QtGui

from AudioTagger.classDialog_auto import Ui_Dialog
import copy

class ClassDialog(QtGui.QDialog):
    settingsSig = QtCore.Signal(list)

    def __init__(self, parent, classSettings=None, keySequences=None):
        super(ClassDialog, self).__init__(parent)
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.connectSignals()


        self.labelSetCnt = 0
        self.creatingNewLabelSet = False
        self.classUIs = []

        self.classSettings = []
        if classSettings is not None:
            classSettings = copy.copy(classSettings)
            while(True):
                try:
                    k, c = classSettings.popitem(last=False)
                    self.classSettings += [[k, c]]
                    self.createNewLabelSet(k, c)
                except KeyError:
                    break

        if keySequences:
            for i, edit in enumerate(zip(*self.classUIs)[4]):
                if i < len(keySequences):
                    edit.setKeySequence(keySequences[i])
                else:
                    break

        self.createNewLabelSet()

    def getSettings(self):
        self.show()


    def connectSignals(self):
        self.ui.buttonBox.accepted.connect(self.sendSettings)
        applyButton = self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply)
        applyButton.clicked.connect(self.sendSettings)


    def setLabelColor(self, label, color):
        colourStyle = "background-color: {0}".format(color.name())
        label.setStyleSheet(colourStyle)

    def createNewLabelSet(self, className=None, classColor=None, keyName=None):
        self.creatingNewLabelSet = True
        if className is None:
            className = ""

        if classColor is None:
            classColor = QtGui.QColor()
            classColor.setRgb(255, 0, 127)

        if keyName is None:
            keyName = self.labelSetCnt

        label = QtGui.QLabel("Class {0}".format(self.labelSetCnt), self)
        edit = QtGui.QLineEdit(self)
        edit.setText(className)

        colourLbl = QtGui.QLabel("       ".format(self.labelSetCnt), self)
        self.setLabelColor(colourLbl, classColor)

        button = QtGui.QPushButton(self)
        button.setText("select colour")

        klabel = QtGui.QLabel("Keyboard shortcut: ", self)
        keySeq = QtGui.QKeySequence(int(QtCore.Qt.Key_0) + self.labelSetCnt)
        keyEdit =  KeySequenceEdit(keySeq, self)
        # edit.setText(className)

        self.ui.gridLayout.addWidget(label, self.labelSetCnt, 0, 1, 1)
        self.ui.gridLayout.addWidget(edit, self.labelSetCnt, 1, 1, 1)
        self.ui.gridLayout.addWidget(colourLbl, self.labelSetCnt, 2, 1, 1)
        self.ui.gridLayout.addWidget(button, self.labelSetCnt, 3, 1, 1)
        self.ui.gridLayout.addWidget(klabel, self.labelSetCnt, 4, 1, 1)
        self.ui.gridLayout.addWidget(keyEdit, self.labelSetCnt, 5, 1, 1)

        idx = int(self.labelSetCnt)
        btnCon = lambda: self.selectColor(idx)
        button.clicked.connect(btnCon)

        leCon = lambda: self.lineEditFinished(idx)
        edit.editingFinished.connect(leCon)

        self.classUIs += [[label, edit, colourLbl, button, keyEdit]]

        if len(self.classSettings) <= self.labelSetCnt:
            self.classSettings += [[className, classColor]]

        self.labelSetCnt += 1
        self.creatingNewLabelSet = False


    def selectColor(self, idx):
        color = QtGui.QColorDialog.getColor()
        self.setLabelColor(self.classUIs[idx][2], color)
        self.classSettings[idx][1] = color

    def lineEditFinished(self, idx):
        self.classSettings[idx][0] = self.classUIs[idx][1].text()

        if idx < len(self.classUIs) -1:
            return

        if self.classUIs[idx][1].text() != "":
            if not self.creatingNewLabelSet:
                self.createNewLabelSet()

    def sendSettings(self):
        classSettings = OrderedDict()
        for k ,c in self.classSettings:
            if k != '':
                classSettings[k] = c

        keySequences  = []
        for cLbl, e, cLbl, b, keyEdit in self.classUIs:
            keySequences += [keyEdit.keySequence]

        # print("classSettings", classSettings)
        # print("keySequences", keySequences)
        self.settingsSig.emit([classSettings, keySequences])


class KeySequenceEdit(QtGui.QLineEdit):
    """
    This class is mainly inspired by
    http://stackoverflow.com/a/6665017

    """

    def __init__(self, keySequence, *args):
        super(KeySequenceEdit, self).__init__(*args)

        self.keySequence = keySequence
        self.setKeySequence(keySequence)

    def setKeySequence(self, keySequence):
        self.keySequence = keySequence
        self.setText(self.keySequence.toString(QtGui.QKeySequence.NativeText))


    def keyPressEvent(self, e):
        if e.type() == QtCore.QEvent.KeyPress:
            key = e.key()

            if key == QtCore.Qt.Key_unknown:
                warnings.warn("Unknown key from a macro probably")
                return

            # the user have clicked just and only the special keys Ctrl, Shift, Alt, Meta.
            if(key == QtCore.Qt.Key_Control or
               key == QtCore.Qt.Key_Shift or
               key == QtCore.Qt.Key_Alt or
               key == QtCore.Qt.Key_Meta):
                print("Single click of special key: Ctrl, Shift, Alt or Meta")
                print("New KeySequence:", QtGui.QKeySequence(key).toString(QtGui.QKeySequence.NativeText))
                return

            # check for a combination of user clicks
            modifiers = e.modifiers()
            keyText = e.text()
            # if the keyText is empty than it's a special key like F1, F5, ...
            print("Pressed Key:", keyText)

            if modifiers & QtCore.Qt.ShiftModifier:
                key += QtCore.Qt.SHIFT
            if modifiers & QtCore.Qt.ControlModifier:
                key += QtCore.Qt.CTRL
            if modifiers & QtCore.Qt.AltModifier:
                key += QtCore.Qt.ALT
            if modifiers & QtCore.Qt.MetaModifier:
                key += QtCore.Qt.META

            print("New KeySequence:", QtGui.QKeySequence(key).toString(QtGui.QKeySequence.NativeText))

            self.setKeySequence(QtGui.QKeySequence(key))



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    w = ClassDialog(None)

    sys.exit(app.exec_())
