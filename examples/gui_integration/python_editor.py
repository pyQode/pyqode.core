#!/usr/bin/env python3
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
import pcef
if pcef.python3:
    from ui.python_editor_ui3 import Ui_MainWindow
    print("Using python3")
else:
    from ui.python_editor_ui import Ui_MainWindow
    print("Using python2")


class PythonEditorWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        # Add modes to the modes menu
        for k, v in self.editor.modes().items():
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            self.menuModes.addAction(a)
        # Add panels to the panels menu
        for zones, panel_dic in self.editor.panels().items():
            for k, v in panel_dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                self.menuPanels.addAction(a)
        # create action group for styles
        group = QtGui.QActionGroup(self)
        group.addAction(self.actionDark)
        group.addAction(self.actionLight)
        self.actionLight.setChecked(True)
        try:
            self.editor.openFile(__file__)
        except (OSError, IOError) as e:
            pass
        except AttributeError:
            pass

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


