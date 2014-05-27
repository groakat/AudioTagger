__author__ = 'peter'

import sys
from PySide import QtCore, QtGui
from AudioTagger.classDialog_auto import Ui_Dialog
import copy

class ClassDialog(QtGui.QDialog):

    def __init__(self, parent, classSettings=None):
        super(ClassDialog, self).__init__(parent)
        # Usual setup stuff. Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.connectSignals()


        self.labelSetCnt = 0
        self.creatingNewLabelSet = False
        self.classUIs = []

        self.classSettings = []
        if classSettings is None:
            self.createNewLabelSet()
        else:

            for k, c in classSettings.items():
                self.classSettings += [[k, c]]
                self.createNewLabelSet(k, c)

        self.show()


    def connectSignals(self):
        self.ui.buttonBox.accepted.connect(self.sendSettings)
        applyButton = self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply)
        applyButton.clicked.connect(self.sendSettings)


    def setLabelColor(self, label, color):
        colourStyle = "background-color: {0}".format(color.name())
        label.setStyleSheet(colourStyle)

    def createNewLabelSet(self, className=None, classColor=None):
        self.creatingNewLabelSet = True
        if className is None:
            className = ""

        if classColor is None:
            classColor = QtGui.QColor()
            classColor.setRgb(255, 0, 127)

        label = QtGui.QLabel("Class {0}".format(self.labelSetCnt), self)
        edit = QtGui.QLineEdit(self)
        edit.setText(className)

        colourLbl = QtGui.QLabel("       ".format(self.labelSetCnt), self)
        self.setLabelColor(colourLbl, classColor)

        button = QtGui.QPushButton(self)
        button.setText("select colour")


        self.ui.gridLayout.addWidget(label, self.labelSetCnt, 0, 1, 1)
        self.ui.gridLayout.addWidget(edit, self.labelSetCnt, 1, 1, 1)
        self.ui.gridLayout.addWidget(colourLbl, self.labelSetCnt, 2, 1, 1)
        self.ui.gridLayout.addWidget(button, self.labelSetCnt, 3, 1, 1)

        idx = int(self.labelSetCnt)
        btnCon = lambda: self.buttonTest(idx)
        button.clicked.connect(btnCon)

        leCon = lambda: self.lineEditFinished(idx)
        edit.editingFinished.connect(leCon)

        self.classUIs += [[label, edit, colourLbl, button]]

        if len(self.classSettings) <= self.labelSetCnt:
            self.classSettings += [[className, classColor]]

        self.labelSetCnt += 1
        self.creatingNewLabelSet = False


    def buttonTest(self, idx):
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
        print self.classSettings

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    w = ClassDialog(None)

    sys.exit(app.exec_())



        # QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        # QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)