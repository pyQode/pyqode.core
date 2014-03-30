#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import sys

from PyQt4 import QtCore, QtGui

from pyqode.core import modes
from pyqode.core import panels
from pyqode.core import style
from pyqode.core.editor import Panel
from pyqode.core.modes import PygmentsSyntaxHighlighter

from ui.simple_editor_ui import Ui_MainWindow


class SimpleEditorWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # add panels
        self.editor.install_panel(panels.LineNumberPanel(),
                                  Panel.Position.LEFT)
        self.editor.install_panel(panels.SearchAndReplacePanel(),
                                  Panel.Position.BOTTOM)
        # add moes
        self.editor.install_mode(modes.AutoCompleteMode())
        self.editor.install_mode(modes.CaseConverterMode())
        self.editor.install_mode(modes.FileWatcherMode())
        self.editor.install_mode(modes.CaretLineHighlighterMode())
        self.editor.install_mode(modes.RightMarginMode())
        self.editor.install_mode(modes.PygmentsSyntaxHighlighter(
            self.editor.document()))
        self.editor.install_mode(modes.ZoomMode())
        self.editor.install_mode(modes.CodeCompletionMode())
        self.editor.install_mode(modes.AutoIndentMode())
        self.editor.install_mode(modes.IndenterMode())
        self.editor.install_mode(modes.SymbolMatcherMode())

        # start pyqode server
        self.editor.start_server('../server.py')

        # connect to editor signals
        self.editor.dirty_changed.connect(self.actionSave.setEnabled)
        self.actionSave.triggered.connect(self.editor.save_to_file)

        # create edit menu
        mnu = QtGui.QMenu("Edit", self.menubar)
        mnu.addActions(self.editor.actions())
        self.menubar.addMenu(mnu)
        self.setupModesMenu()
        self.setupPanelsMenu()
        self.setupStylesMenu()

        # open a this module in the editor
        self.editor.open_file(__file__, detect_encoding=True)

    def setupStylesMenu(self):
        group = QtGui.QActionGroup(self)
        currentStyle = self.editor.get_mode(
            PygmentsSyntaxHighlighter).pygments_style
        group.triggered.connect(self.on_style_changed)
        for style in sorted(modes.PYGMENTS_STYLES):
            a = QtGui.QAction(self.menuStyles)
            a.setText(style)
            a.setCheckable(True)
            if style == currentStyle:
                a.setChecked(True)
            group.addAction(a)
            self.menuStyles.addAction(a)

    def setupModesMenu(self):
        # Add modes to the modes menu
        for k, v in sorted(self.editor.get_modes().items()):
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.on_mode_state_changed)
            a.mode = v
            self.menuModes.addAction(a)

    def setupPanelsMenu(self):
        for zones, panel_dic in sorted(self.editor.get_panels().items()):
            for k, v in panel_dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                a.setCheckable(True)
                a.setChecked(True)
                a.changed.connect(self.on_panel_state_changed)
                a.panel = v
                self.menuPanels.addAction(a)

    @QtCore.pyqtSlot(QtGui.QAction)
    def on_style_changed(self, action):
        style.pygments_style = action.text()
        self.editor.refresh_style()

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        filePath = QtGui.QFileDialog.getOpenFileName(
            self, "Choose a file", os.path.expanduser("~"))
        if filePath:
            self.editor.open_file(filePath, detect_encoding=True)

    def on_panel_state_changed(self):
        action = self.sender()
        action.panel.enabled = action.isChecked()

    def on_mode_state_changed(self):
        action = self.sender()
        action.mode.enabled = action.isChecked()


def main():
    app = QtGui.QApplication(sys.argv)
    win = SimpleEditorWindow()
    win.show()
    app.exec_()
    # cleanup
    win.editor.stop_server()  # ensure the server is properly closed.
    del win
    del app

if __name__ == "__main__":
    main()
