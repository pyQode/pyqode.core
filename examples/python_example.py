#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
""" PCEF generic editor demo """
import sys

from PySide.QtCore import Slot
from PySide.QtGui import QAction
from PySide.QtGui import QActionGroup
from PySide.QtGui import QApplication
from PySide.QtGui import QFileDialog
from PySide.QtGui import QMainWindow

from pcef import openFileInEditor
from pcef import saveFileFromEditor
from pcef import styles
from examples.ui import simple_python_editor_ui


class GenericPythonEditor(QMainWindow):
    """
    A simple editor window that can open/save files.

    The ui has been designed in Qt Designer and use the promoted widgets system
    to instantiate a GenericEditor. (self.ui.genericEditor)
    """

    def __init__(self):
        QMainWindow.__init__(self)
        # setup ui (the pcef PythonEditor is created in the Ui_MainWindow using
        # the promoted widgets system)
        self.ui = simple_python_editor_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PCEF - Python Editor Example")

        # open this file
        if __name__ == "__main__":
            openFileInEditor(self.ui.genericEditor, __file__)

        # add styles actions
        allStyles = styles.getAllStyles()
        allStyles.sort()
        self.styleActionGroup = QActionGroup(self)
        for style in allStyles:
            action = QAction(unicode(style), self.ui.menuStyle)
            action.setCheckable(True)
            action.setChecked(style == "Default")
            self.styleActionGroup.addAction(action)
            self.ui.menuStyle.addAction(action)
            self.styleActionGroup.triggered.connect(
                self.on_styleActionGroup_triggered)

        # add panels actions
        allPanels = self.ui.genericEditor.panels()
        allPanels.sort()
        self.panels_actions = []
        for panel in allPanels:
            action = QAction(unicode(panel), self.ui.menuPanels)
            action.setCheckable(True)
            action.setChecked(panel.enabled)
            self.ui.menuPanels.addAction(action)
            self.panels_actions.append(action)
            action.triggered.connect(self.onPanelActionTriggered)

        # add panels actions
        allModes = self.ui.genericEditor.modes()
        allModes.sort()
        self.modes_actions = []
        for mode in allModes:
            action = QAction(unicode(mode), self.ui.menuModes)
            action.setCheckable(True)
            action.setChecked(mode.enabled)
            self.ui.menuModes.addAction(action)
            self.modes_actions.append(action)
            action.triggered.connect(self.onModeActionTriggered)

    def onModeActionTriggered(self):
        """ Enables/Disables a mode """
        modes = self.ui.genericEditor.modes()
        modes.sort()
        for mode, action in zip(modes, self.modes_actions):
            mode.enabled = action.isChecked()

    def onPanelActionTriggered(self):
        """ Enables/Disables a Panel """
        panels = self.ui.genericEditor.panels()
        panels.sort()
        for panel, action in zip(panels, self.panels_actions):
            panel.enabled = action.isChecked()

    def on_styleActionGroup_triggered(self, action):
        """ Change current editor style """
        self.ui.genericEditor.currentStyle = styles.getStyle(action.text())
        stylesheet = ""
        if action.text() == "Dark":
            try:
                import qdarkstyle
                stylesheet = qdarkstyle.load_stylesheet()
            except ImportError:
                print("Failed to use the qdarkstyle. "
                      "Please execute <pip install qdarkstyle> to fully use "
                      "this theme.")
        QApplication.instance().setStyleSheet(stylesheet)

    @Slot()
    def on_actionSave_triggered(self):
        """ Save the current file """
        saveFileFromEditor(self.ui.genericEditor)

    @Slot()
    def on_actionSave_as_triggered(self):
        """ Save the current file as"""
        filename = QFileDialog.getSaveFileName(self)[0]
        if filename != "":
            saveFileFromEditor(self.ui.genericEditor, filename)

    @Slot()
    def on_actionOpen_triggered(self):
        """ Open a new file in the editor """
        filename = QFileDialog.getOpenFileName(
            self, "Choose a python script", "", "Python script (*.py)")[0]
        if filename != "":
            openFileInEditor(self.ui.genericEditor, filename)


def main():
    """ Application entry point """
    app = QApplication(sys.argv)
    window = GenericPythonEditor()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
