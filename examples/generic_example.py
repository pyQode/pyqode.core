#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
""" PCEF generic editor demo """
import os
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
from pcef.panels.misc import QUserMarkersPanel

from examples.ui import simple_editor_ui


class SimpleEditor(QMainWindow):
    """
    A simple editor window that can open/save files.

    The ui has been designed in Qt Designer and use the promoted widgets system
    to instantiate a QGenericEditor. (self.ui.genericEditor)
    """
    def __init__(self):
        QMainWindow.__init__(self)
        # setup ui (the pcef QGenericEditor is created there using
        # the promoted widgets system)
        self.ui = simple_editor_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        editor = self.ui.genericEditor

        # open this file
        if __name__ == "__main__":
            openFileInEditor(self.ui.genericEditor, __file__)
        else:
            openFileInEditor(self.ui.genericEditor,
                             os.path.join(os.getcwd(), "examples",
                             "generic_example.py"))

        # install panel where user can add its own markers
        p = QUserMarkersPanel()
        editor.installPanel(p, editor.PANEL_ZONE_LEFT)

        # add a fold indicator around our class and the main
        editor.foldPanel.addIndicator(92, 98)

        # add styles actions
        allStyles = styles.getAllStyles()
        self.styleActionGroup = QActionGroup(self)
        for i, style in enumerate(allStyles):
            action = QAction(unicode(style), self.ui.menuStyle)
            action.setCheckable(True)
            action.setChecked(i == 0)
            self.styleActionGroup.addAction(action)
            self.ui.menuStyle.addAction(action)
        self.styleActionGroup.triggered.connect(
            self.on_styleActionGroup_triggered)

    def on_styleActionGroup_triggered(self, action):
        self.ui.genericEditor.currentStyle = styles.getStyle(action.text())

    @Slot()
    def on_actionSave_triggered(self):
        saveFileFromEditor(self.ui.genericEditor)

    @Slot()
    def on_actionSave_as_triggered(self):
        filename = QFileDialog.getSaveFileName(self)[0]
        if filename != "":
            saveFileFromEditor(self.ui.genericEditor, filename)

    @Slot()
    def on_actionOpen_triggered(self):
        filename = QFileDialog.getOpenFileName(self)[0]
        if filename != "":
            openFileInEditor(self.ui.genericEditor, filename)


def main(app=None):
    """ Application entry point """
    if app is None:
        app = QApplication(sys.argv)
    window = SimpleEditor()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
