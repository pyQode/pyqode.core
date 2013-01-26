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
from PySide.QtGui import QApplication, QFileDialog
from PySide.QtGui import QMainWindow
from pcef import openFileInEditor
from pcef.panels.bookmark import QBookmarkPanel
from examples.ui import simple_editor_ui


class SimpleEditor(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # setup ui (the pcef QGenericEditor is created there using
        # the promoted widgets system)
        self.ui = simple_editor_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        editor = self.ui.genericEditor

        # open a file
        openFileInEditor(self.ui.genericEditor,
                         os.path.join(os.getcwd(), "examples", "generic_example.py"))

        # install a bookmark panel with a fixed set of markers
        p = QBookmarkPanel()
        editor.installPanel(p, editor.PANEL_ZONE_LEFT)

        # add a fold indicator around our class and the main
        editor.foldPanel.addIndicator(22, 47)
        editor.foldPanel.addIndicator(50, 56)

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
