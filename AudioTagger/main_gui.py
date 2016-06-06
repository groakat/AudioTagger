# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Wed Aug 20 16:40:42 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

# from PySide import QtCore, QtGui


from PySide import QtCore, QtGui, QtSvg

import os

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(876, 584)
        self.centralwidget = QtGui.QWidget(MainWindow)

        self.create_graphic_views()
        self.create_elements()
        self.create_layouts()
        self.fill_layouts()




        # MENU

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = MainWindow.menuBar()# QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 876, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_folder = QtGui.QAction(MainWindow)
        self.actionOpen_folder.setObjectName("actionOpen_folder")
        self.actionClass_settings = QtGui.QAction(MainWindow)
        self.actionClass_settings.setObjectName("actionClass_settings")
        self.actionExport_settings = QtGui.QAction(MainWindow)
        self.actionExport_settings.setObjectName("actionExport_settings")
        self.actionImport_settings = QtGui.QAction(MainWindow)
        self.actionImport_settings.setObjectName("actionImport_settings")
        self.menuFile.addAction(self.actionOpen_folder)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClass_settings)
        self.menuFile.addAction(self.actionExport_settings)
        self.menuFile.addAction(self.actionImport_settings)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)




    def create_graphic_views(self):
        self.gw_overview = QtGui.QGraphicsView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gw_overview.sizePolicy().hasHeightForWidth())
        self.gw_overview.setSizePolicy(sizePolicy)
        self.gw_overview.setObjectName("gw_overview")

        self.scrollView = QtGui.QGraphicsView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollView.sizePolicy().hasHeightForWidth())
        self.scrollView.setSizePolicy(sizePolicy)
        self.scrollView.setObjectName("scrollView")


    def create_elements(self):
        self.iconFolder = SVGButton.getIconFolder()

        self.pb_prev = SVGButton(self.centralwidget)
        self.pb_prev.load(self.iconFolder + '/fa-backward.svg')
        self.pb_prev.setToolTip("Load previous file")

        self.pb_next = SVGButton(self.centralwidget)
        self.pb_next.load(self.iconFolder + '/fa-forward.svg')
        self.pb_next.setToolTip("Load next file")

        self.pb_save = SVGButton(self.centralwidget)
        self.pb_save.load(self.iconFolder + '/fa-save.svg')
        self.pb_save.setToolTip("Save annotaions")

        self.pb_toggle = SVGButton(self.centralwidget)
        self.pb_toggle.load(self.iconFolder + '/fa-chevron-right.svg')
        self.pb_toggle.setToolTip("Toggle through annotaions")

        self.pb_toggle_back = SVGButton(self.centralwidget)
        self.pb_toggle_back.load(self.iconFolder + '/fa-chevron-left.svg')
        self.pb_toggle_back.setToolTip("Toggle backwards through annotaions")

        # self.pb_edit = QtGui.QPushButton(self.centralwidget)
        # self.pb_edit.setObjectName("pb_edit")


        self.pb_toggle_create = SVGButton(self.centralwidget)
        self.pb_toggle_create.load(self.iconFolder + '/fa-toggle-on.svg')
        self.pb_toggle_create.setToolTip("Click to modify annotations")

        self.lbl_spec_modify = QtGui.QLabel(self.centralwidget)
        self.lbl_spec_create = QtGui.QLabel(self.centralwidget)


        # self.cb_create = QtGui.QCheckBox(self.centralwidget)
        # self.cb_create.setChecked(True)
        # self.cb_create.setObjectName("cb_create")

        self.lbl_audio = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_audio.sizePolicy().hasHeightForWidth())
        self.lbl_audio.setSizePolicy(sizePolicy)
        self.lbl_audio.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_audio.setObjectName("lbl_audio")

        self.pb_play = SVGButton(self.centralwidget)
        self.pb_play.load(self.iconFolder + '/fa-play.svg')
        self.pb_play.setToolTip("Play sound")

        self.pb_stop = SVGButton(self.centralwidget)
        self.pb_stop.load(self.iconFolder + '/fa-stop.svg')
        self.pb_stop.setToolTip("Stop and reset sound")

        self.pb_seek = SVGButton(self.centralwidget)
        self.pb_seek.load(self.iconFolder + '/fa-map-signs.svg')
        self.pb_seek.setToolTip("Seek")

        self.lbl_audio_position = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_audio_position.sizePolicy().hasHeightForWidth())
        self.lbl_audio_position.setSizePolicy(sizePolicy)
        self.lbl_audio_position.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_audio_position.setObjectName("lbl_audio_position")
        self.lbl_audio_position.setVisible(False)

        self.lbl_followSound = QtGui.QLabel(self.centralwidget)
        self.cb_followSound = QtGui.QCheckBox(self.centralwidget)
        self.cb_followSound.setObjectName("cb_followSound")

        # self.lbl_zoom = QtGui.QLabel(self.centralwidget)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.lbl_zoom.sizePolicy().hasHeightForWidth())
        # self.lbl_zoom.setSizePolicy(sizePolicy)
        # self.lbl_zoom.setObjectName("lbl_zoom")

        self.lbl_playbackSpeed = QtGui.QLabel(self.centralwidget)
        self.cb_playbackSpeed = QtGui.QComboBox(self.centralwidget)
        self.cb_playbackSpeed.setObjectName("cb_playbackSpeed")

        self.lbl_specType = QtGui.QLabel(self.centralwidget)
        self.cb_specType = QtGui.QComboBox(self.centralwidget)
        self.cb_specType.setObjectName("cb_specType")
        self.cb_specType.addItem("")
        self.cb_specType.addItem("")

        self.lbl_labelType = QtGui.QLabel(self.centralwidget)
        self.cb_labelType = QtGui.QComboBox(self.centralwidget)
        self.cb_labelType.setObjectName("cb_labelType")

        self.cb_file = QtGui.QComboBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cb_file.sizePolicy().hasHeightForWidth())
        self.cb_file.setSizePolicy(sizePolicy)
        self.cb_file.setObjectName("cb_file")

        # self.info_viewer = QtGui.QLabel(self.centralwidget)
        # self.info_viewer = QtGui.QTextEdit(self.centralwidget)
        self.info_viewer = SmallEdit(self.centralwidget)

        # self.info_viewer.setMinimumSize(100, 10)
        # self.info_viewer.setFixedSize(100, 100)
        # self.info_viewer.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)


    def create_layouts(self):
        self.structure_layout = QtGui.QVBoxLayout(self.centralwidget)

        self.control_info_widget = QtGui.QWidget(self.centralwidget)
        self.control_info_splitter = QtGui.QHBoxLayout(self.control_info_widget)
        self.control_info_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

        self.file_control_widget = QtGui.QWidget(self.centralwidget)
        self.file_control_layout = QtGui.QVBoxLayout(self.file_control_widget)
        self.file_control_layout.setContentsMargins(0,0,0,0)
        self.file_control_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

        self.sound_spec_widget = QtGui.QWidget(self.centralwidget)
        self.sound_spec_layout = QtGui.QHBoxLayout(self.sound_spec_widget)
        self.sound_spec_layout.setContentsMargins(0,0,0,0)

        self.sound_parts_widget = QtGui.QWidget(self.centralwidget)
        self.sound_parts_layout = QtGui.QVBoxLayout(self.sound_parts_widget)
        self.sound_parts_layout.setSpacing(10)
        self.sound_parts_layout.setContentsMargins(0,0,0,0)

        self.sound_settings_widget = QtGui.QWidget(self.centralwidget)
        self.sound_settings_layout = QtGui.QFormLayout(self.sound_settings_widget)
        self.sound_settings_layout.setContentsMargins(0,0,0,0)

        self.spec_parts_widget = QtGui.QWidget(self.centralwidget)
        self.spec_parts_layout = QtGui.QVBoxLayout(self.spec_parts_widget)
        self.spec_parts_layout.setContentsMargins(0,0,0,0)

        self.sound_controls_widget = QtGui.QWidget(self.centralwidget)
        self.sound_controls_layout = QtGui.QHBoxLayout(self.sound_controls_widget)
        self.sound_controls_layout.setSpacing(10)
        self.sound_controls_layout.setContentsMargins(0,0,0,0)

        self.spec_interact_widget = QtGui.QWidget(self.centralwidget)
        self.spec_interact_layout = QtGui.QHBoxLayout(self.spec_interact_widget)
        self.spec_interact_layout.setSpacing(10)
        self.spec_interact_layout.setContentsMargins(0,0,0,0)

        self.spec_settings_widget = QtGui.QWidget(self.centralwidget)
        self.spec_settings_layout = QtGui.QFormLayout(self.spec_settings_widget)
        self.spec_settings_layout.setSpacing(10)
        self.spec_settings_layout.setContentsMargins(0,0,0,0)


        self.create_modify_widget = QtGui.QWidget(self.centralwidget)
        self.create_modify_layout = QtGui.QHBoxLayout(self.create_modify_widget)
        self.create_modify_layout.setSpacing(5)
        self.create_modify_layout.setContentsMargins(0,0,0,0)


    def fill_layouts(self):
        self.structure_layout.addWidget(self.gw_overview)
        self.structure_layout.addWidget(self.scrollView)
        self.structure_layout.addWidget(self.control_info_widget)

        self.control_info_splitter.addWidget(self.file_control_widget)
        self.control_info_splitter.addWidget(self.info_viewer)

        self.file_control_layout.addWidget(self.sound_spec_widget)
        self.file_control_layout.addWidget(self.cb_file)

        self.sound_spec_layout.addWidget(self.sound_parts_widget)
        self.sound_spec_layout.addWidget(self.spec_parts_widget)

        self.sound_parts_layout.addWidget(self.sound_controls_widget)
        self.sound_parts_layout.addWidget(self.sound_settings_widget)

        self.sound_controls_layout.addStretch(0)
        self.sound_controls_layout.addWidget(self.pb_prev)
        self.sound_controls_layout.addWidget(self.pb_stop)
        self.sound_controls_layout.addWidget(self.pb_play)
        self.sound_controls_layout.addWidget(self.pb_next)
        self.sound_controls_layout.addSpacing(15)
        self.sound_controls_layout.addWidget(self.pb_seek)
        self.sound_controls_layout.addStretch(0)

        self.sound_settings_layout.addRow(self.lbl_followSound, self.cb_followSound)
        self.sound_settings_layout.addRow(self.lbl_playbackSpeed, self.cb_playbackSpeed)

        self.spec_parts_layout.addWidget(self.spec_interact_widget)
        self.spec_parts_layout.addWidget(self.spec_settings_widget)

        self.spec_interact_layout.addStretch(0)
        # self.spec_interact_layout.addWidget(self.cb_create)
        self.spec_interact_layout.addWidget(self.create_modify_widget)
        self.spec_interact_layout.addWidget(self.pb_toggle_back)
        self.spec_interact_layout.addWidget(self.pb_toggle)
        self.spec_interact_layout.addWidget(self.pb_save)
        self.spec_interact_layout.addStretch(0)

        self.spec_settings_layout.addRow(self.lbl_labelType, self.cb_labelType)
        self.spec_settings_layout.addRow(self.lbl_specType, self.cb_specType)

        self.create_modify_layout.addWidget(self.lbl_spec_modify)
        self.create_modify_layout.addWidget(self.pb_toggle_create)
        self.create_modify_layout.addWidget(self.lbl_spec_create)

        self.centralwidget.setLayout(self.structure_layout)



    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_prev.setText(QtGui.QApplication.translate("MainWindow", "show previous audio file", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_next.setText(QtGui.QApplication.translate("MainWindow", "show next audio file", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_save.setText(QtGui.QApplication.translate("MainWindow", "save", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_toggle.setText(QtGui.QApplication.translate("MainWindow", "toggle", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_edit.setText(QtGui.QApplication.translate("MainWindow", "edit", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_debug.setText(QtGui.QApplication.translate("MainWindow", "debug", None, QtGui.QApplication.UnicodeUTF8))
        # self.cb_create.setText(QtGui.QApplication.translate("MainWindow", "create", None, QtGui.QApplication.UnicodeUTF8))
        # self.lbl_audio.setText(QtGui.QApplication.translate("MainWindow", "audio: ", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_play.setText(QtGui.QApplication.translate("MainWindow", "play", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_stop.setText(QtGui.QApplication.translate("MainWindow", "stop", None, QtGui.QApplication.UnicodeUTF8))
        # self.pb_seek.setText(QtGui.QApplication.translate("MainWindow", "seek", None, QtGui.QApplication.UnicodeUTF8))
        # self.lbl_audio_position.setText(QtGui.QApplication.translate("MainWindow", "position:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_followSound.setText(QtGui.QApplication.translate("MainWindow", "follow sound", None, QtGui.QApplication.UnicodeUTF8))
        # self.lbl_zoom.setText(QtGui.QApplication.translate("MainWindow", " Vertical zoom: 1x", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_playbackSpeed.setText(QtGui.QApplication.translate("MainWindow", "playback speed:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_specType.setText(QtGui.QApplication.translate("MainWindow", "spectrogram range", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_labelType.setText(QtGui.QApplication.translate("MainWindow", "active label", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_specType.setItemText(0, QtGui.QApplication.translate("MainWindow", "audible", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_specType.setItemText(1, QtGui.QApplication.translate("MainWindow", "ultra sonic", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_spec_create.setText(QtGui.QApplication.translate("MainWindow", "create", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_spec_modify.setText(QtGui.QApplication.translate("MainWindow", "modify", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_folder.setText(QtGui.QApplication.translate("MainWindow", "Open folder", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClass_settings.setText(QtGui.QApplication.translate("MainWindow", "Class settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport_settings.setText(QtGui.QApplication.translate("MainWindow", "export settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport_settings.setText(QtGui.QApplication.translate("MainWindow", "import settings", None, QtGui.QApplication.UnicodeUTF8))


class SmallEdit(QtGui.QTextEdit):
    def __init__(self, *args, **kwargs):
        super(SmallEdit, self).__init__(*args, **kwargs)

    def sizeHint(self):
        return (10,10)


class SVGButton(QtGui.QPushButton):
    def __init__(self, svgPath=None, *args, **kwargs):
        super(SVGButton, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        self.icon = None

        self.centralWidget = QtGui.QWidget(self)
        self.setFlat(True)
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(20, 20)

        if svgPath is not None:
            self.load(svgPath)


    def load(self, svgPath):
        if self.icon is None:
            self.icon = QtSvg.QSvgWidget(svgPath, self.centralWidget)
            self.icon.setFixedSize(self.size())
        else:
            self.icon.load(svgPath)

        self.layoutBase = QtGui.QHBoxLayout(self)
        self.layoutBase.setSpacing(0)
        self.layoutBase.setContentsMargins(0,0,0,0)
        self.layoutBase.addWidget(self.icon)

    def resizeEvent(self, event):
        super(SVGButton, self).resizeEvent(event)

        if self.icon is not None:
            self.icon.setFixedSize(self.size())

    @staticmethod
    def getIconFolder():
        iconFolder = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            os.path.pardir,
                            'icons')

        return iconFolder