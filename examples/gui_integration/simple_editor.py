#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from pyqode.core.api import start_server, stop_server

logging.basicConfig(level=logging.DEBUG)
import os
import sys

from PyQt4 import QtCore, QtGui

from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core import style

from ui.simple_editor_ui import Ui_MainWindow


class SimpleEditorWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # add panels
        api.install_panel(self.editor, panels.LineNumberPanel())
        api.install_panel(self.editor, panels.SearchAndReplacePanel(),
                          panels.SearchAndReplacePanel.Position.BOTTOM)
        # add modes
        api.install_mode(self.editor, modes.AutoCompleteMode())
        api.install_mode(self.editor, modes.CaseConverterMode())
        api.install_mode(self.editor, modes.FileWatcherMode())
        api.install_mode(self.editor, modes.CaretLineHighlighterMode())
        api.install_mode(self.editor, modes.RightMarginMode())
        api.install_mode(self.editor, modes.PygmentsSyntaxHighlighter(
            self.editor.document()))
        api.install_mode(self.editor, modes.ZoomMode())
        api.install_mode(self.editor, modes.CodeCompletionMode())
        api.install_mode(self.editor, modes.AutoIndentMode())
        api.install_mode(self.editor, modes.IndenterMode())
        api.install_mode(self.editor, modes.SymbolMatcherMode())

        # start pyqode server for our code editor widget
        api.start_server(self.editor, '../server.py')

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

        # open this module file in the editor
        self.editor.open_file(__file__, detect_encoding=True)

    def setupStylesMenu(self):
        group = QtGui.QActionGroup(self)
        currentStyle = api.get_mode(self.editor,
            modes.PygmentsSyntaxHighlighter).pygments_style
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
        for k, v in sorted(api.get_modes(self.editor).items()):
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.on_mode_state_changed)
            a.mode = v
            self.menuModes.addAction(a)

    def setupPanelsMenu(self):
        for zones, panel_dic in sorted(api.get_panels(self.editor).items()):
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
    api.stop_server(win.editor)  # ensure the server is properly closed.
    del win
    del app

if __name__ == "__main__":
    main()
