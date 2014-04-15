# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Tue Apr 15 16:12:05 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(809, 605)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gw_overview = QtGui.QGraphicsView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gw_overview.sizePolicy().hasHeightForWidth())
        self.gw_overview.setSizePolicy(sizePolicy)
        self.gw_overview.setObjectName("gw_overview")
        self.horizontalLayout_2.addWidget(self.gw_overview)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 787, 176))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pb_prev = QtGui.QPushButton(self.centralwidget)
        self.pb_prev.setObjectName("pb_prev")
        self.horizontalLayout.addWidget(self.pb_prev)
        self.pb_next = QtGui.QPushButton(self.centralwidget)
        self.pb_next.setObjectName("pb_next")
        self.horizontalLayout.addWidget(self.pb_next)
        self.pb_debug = QtGui.QPushButton(self.centralwidget)
        self.pb_debug.setObjectName("pb_debug")
        self.horizontalLayout.addWidget(self.pb_debug)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 809, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_prev.setText(QtGui.QApplication.translate("MainWindow", "show previous audio file", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_next.setText(QtGui.QApplication.translate("MainWindow", "show next audio file", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_debug.setText(QtGui.QApplication.translate("MainWindow", "debug", None, QtGui.QApplication.UnicodeUTF8))

