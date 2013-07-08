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
from pcef.qt import QtCore, QtGui
usePyQt4 = os.environ['QT_API'] == "PyQt"
usePySide = os.environ['QT_API'] == "PySide"
if sys.version_info[0] == 3:
    if usePyQt4:
        from ui.simple_editor_ui3_pyqt import Ui_MainWindow
    elif usePySide:
        from ui.simple_editor_ui3_pyside import Ui_MainWindow
else:
    if usePyQt4:
        from ui.simple_editor_ui_pyqt import Ui_MainWindow
    elif usePySide:
        from ui.simple_editor_ui_pyside import Ui_MainWindow
print(os.environ["QT_API"])
print("Python {}".format(sys.version_info[0]))


class SimpleEditorWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.editor.dirtyChanged.connect(self.actionSave.setEnabled)
        self.actionSave.triggered.connect(self.editor.saveToFile)
        # edit menu
        self.menubar.addMenu(self.editor.contextMenu)
        # Add modes to the modes menu
        for k, v in self.editor.modes().items():
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.onModeCheckStateChanged)
            a.mode = v
            self.menuModes.addAction(a)
        # Add panels to the panels menu
        for zones, panel_dic in self.editor.panels().items():
            for k, v in panel_dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                a.setCheckable(True)
                a.setChecked(True)
                a.changed.connect(self.onPanelCheckStateChanged)
                a.panel = v
                self.menuPanels.addAction(a)
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

    def onPanelCheckStateChanged(self):
        action = self.sender()
        action.panel.enabled = action.isChecked()

    def onModeCheckStateChanged(self):
        action = self.sender()
        action.mode.enabled = action.isChecked()


def main():
    app = QtGui.QApplication(sys.argv)
    win = SimpleEditorWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()


