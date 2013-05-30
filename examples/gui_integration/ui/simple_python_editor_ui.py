# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simple_python_editor.ui'
#
# Created: Thu May 30 23:47:41 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(751, 484)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setMargin(1)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.genericEditor = PythonEditor(self.centralwidget)
        self.genericEditor.setObjectName(_fromUtf8("genericEditor"))
        self.gridLayout.addWidget(self.genericEditor, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 751, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        self.menuStyle = QtGui.QMenu(self.menuSettings)
        self.menuStyle.setObjectName(_fromUtf8("menuStyle"))
        self.menuPanels = QtGui.QMenu(self.menuSettings)
        self.menuPanels.setObjectName(_fromUtf8("menuPanels"))
        self.menuModes = QtGui.QMenu(self.menuSettings)
        self.menuModes.setObjectName(_fromUtf8("menuModes"))
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/example_icons/rc/folder.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon)
        self.actionOpen.setIconVisibleInMenu(True)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/example_icons/rc/document-save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave.setIconVisibleInMenu(True)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionSave_as = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/example_icons/rc/document-save-as.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as.setIcon(icon2)
        self.actionSave_as.setIconVisibleInMenu(True)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))
        self.actionWhiteStyle = QtGui.QAction(MainWindow)
        self.actionWhiteStyle.setCheckable(True)
        self.actionWhiteStyle.setChecked(True)
        self.actionWhiteStyle.setObjectName(_fromUtf8("actionWhiteStyle"))
        self.actionDarkStyle = QtGui.QAction(MainWindow)
        self.actionDarkStyle.setCheckable(True)
        self.actionDarkStyle.setObjectName(_fromUtf8("actionDarkStyle"))
        self.actionPanel = QtGui.QAction(MainWindow)
        self.actionPanel.setObjectName(_fromUtf8("actionPanel"))
        self.actionModes_2 = QtGui.QAction(MainWindow)
        self.actionModes_2.setObjectName(_fromUtf8("actionModes_2"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuSettings.addAction(self.menuStyle.menuAction())
        self.menuSettings.addAction(self.menuPanels.menuAction())
        self.menuSettings.addAction(self.menuModes.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSave_as)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings", None))
        self.menuStyle.setTitle(_translate("MainWindow", "Style", None))
        self.menuPanels.setTitle(_translate("MainWindow", "Panels", None))
        self.menuModes.setTitle(_translate("MainWindow", "Modes", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S", None))
        self.actionSave_as.setText(_translate("MainWindow", "Save as", None))
        self.actionSave_as.setShortcut(_translate("MainWindow", "Ctrl+Shift+S", None))
        self.actionWhiteStyle.setText(_translate("MainWindow", "White", None))
        self.actionDarkStyle.setText(_translate("MainWindow", "Dark", None))
        self.actionPanel.setText(_translate("MainWindow", "Panel", None))
        self.actionModes_2.setText(_translate("MainWindow", "Modes", None))

from pcef.editors.python import PythonEditor
import examples_rc
