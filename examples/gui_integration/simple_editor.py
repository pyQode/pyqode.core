#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Integrates the generic editor using the pcef qt designer plugin.
"""
import os
import sys
import pcef.core
from pcef.qt import QtCore, QtGui
from ui import loadUi


class SimpleEditorWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        loadUi("simple_editor.ui", self, rcFilename="simple_editor.qrc")
        self.editor.dirtyChanged.connect(self.actionSave.setEnabled)
        self.actionSave.triggered.connect(self.editor.saveToFile)
        if QtGui.QIcon.hasThemeIcon("document-save"):
            self.actionSave.setIcon(QtGui.QIcon.fromTheme("document-save"))
        if QtGui.QIcon.hasThemeIcon("document-open"):
            self.actionOpen.setIcon(QtGui.QIcon.fromTheme("document-open"))
        # edit menu
        mnu = QtGui.QMenu("Edit", self.menubar)
        mnu.addActions(self.editor.actions())
        self.menubar.addMenu(mnu)
        self.setupModesMenu()
        self.setupPanelsMenu()
        self.setupStylesMenu()
        try:
            self.editor.openFile(__file__)
        except (OSError, IOError) as e:
            pass
        except AttributeError:
            pass

    def setupStylesMenu(self):
        group = QtGui.QActionGroup(self)
        currentStyle = self.editor.style.value("pygmentsStyle")
        group.triggered.connect(self.onStyleTriggered)
        for style in sorted(pcef.core.PYGMENTS_STYLES):
            a = QtGui.QAction(self.menuStyles)
            a.setText(style)
            a.setCheckable(True)
            if style == currentStyle:
                a.setChecked(True)
            group.addAction(a)
            self.menuStyles.addAction(a)

    def setupModesMenu(self):
        # Add modes to the modes menu
        for k, v in self.editor.modes().items():
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.onModeCheckStateChanged)
            a.mode = v
            self.menuModes.addAction(a)

    def setupPanelsMenu(self):
        for zones, panel_dic in self.editor.panels().items():
            for k, v in panel_dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                a.setCheckable(True)
                a.setChecked(True)
                a.changed.connect(self.onPanelCheckStateChanged)
                a.panel = v
                self.menuPanels.addAction(a)

    @QtCore.Slot(QtGui.QAction)
    def onStyleTriggered(self, action):
        self.editor.style.setValue("pygmentsStyle", action.text())

    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        filePath = QtGui.QFileDialog.getOpenFileName(
            self, "Choose a file", os.path.expanduser("~"))
        if os.environ['QT_API'] == 'PySide':
            if filePath[0]:
                self.editor.openFile(filePath[0])
        else:
            if filePath:
                self.editor.openFile(filePath)

    def onPanelCheckStateChanged(self):
        action = self.sender()
        action.panel.enabled = action.isChecked()

    def onModeCheckStateChanged(self):
        action = self.sender()
        action.mode.enabled = action.isChecked()


def main():
    try:
        import faulthandler
        faulthandler.enable()
    except ImportError:
        pass

    app = QtGui.QApplication(sys.argv)
    win = SimpleEditorWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()


