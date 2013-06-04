#!/usr/bin/env python2
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
os.environ.setdefault("QT_API", "pyqt")
from pcef import QtCore, QtGui
from ui import python_editor_ui


class PythonEditorWindow(QtGui.QMainWindow, python_editor_ui.Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        # Add modes to the modes menu
        for k, v in self.editor.modes().iteritems():
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            self.menuModes.addAction(a)
        # Add panels to the panels menu
        for zones, panel_dic in self.editor.panels().iteritems():
            for k, v in panel_dic.iteritems():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                self.menuPanels.addAction(a)
        try:
            self.editor.openFile(__file__)
        except (OSError, IOError) as e:
            pass
        except AttributeError:
            pass
        print self.editor.style.dump()

    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        filePath = QtGui.QFileDialog.getOpenFileName(
            self, "Choose a file", os.path.expanduser("~"))
        if filePath:
            self.editor.openFile(filePath)


def main():
    app = QtGui.QApplication(sys.argv)
    win = PythonEditorWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()


