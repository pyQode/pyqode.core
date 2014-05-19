#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This example is an alternative version of style_and_settings where we modify
the settings and styles after CodeEdit has been shown.

"""
import sys

from pyqode.qt import QtWidgets, QtGui

from pyqode.core import frontend
from pyqode.core import settings
from pyqode.core import style
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # code from the simple example
    editor = frontend.CodeEdit()
    frontend.open_file(editor, __file__)
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_mode(editor, modes.PygmentsSyntaxHighlighter(
        editor.document()))
    frontend.install_panel(
        editor, panels.SearchAndReplacePanel(),
        position=panels.SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()

    # show whitespaces in dark gray
    settings.show_white_spaces = True
    style.whitespaces_foreground = QtGui.QColor('#606020')

    # make a dark editor using the monokai theme
    style.pygments_style = 'monokai'

    # we need to tell CodeEdit instance to refresh its settings and style
    editor.refresh_settings()
    editor.refresh_style()

    app.exec_()

    del editor
    del window
    del app


if __name__ == "__main__":
    main()