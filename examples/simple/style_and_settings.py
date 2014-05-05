#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This example expands the simple example to show you how to define custom
settings and styles.

In this example, we are going to make a dark code editor widget which shows
the whitespaces.

"""
import sys

from PyQt4 import QtGui

from pyqode.core import frontend, settings, style
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels



def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()

    # make the code edit show whitespaces in dark gray
    settings.show_white_spaces = True
    style.whitespaces_foreground = QtGui.QColor('#606020')

    # make a dark editor using the monokai theme
    style.pygments_style = 'monokai'

    # code from the simple example
    editor = frontend.CodeEdit()
    frontend.open_file(editor, __file__)
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_mode(editor,
                          modes.PygmentsSyntaxHighlighter(editor.document()))
    frontend.install_panel(editor,
                           panels.SearchAndReplacePanel(),
                           position=panels.SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()

    app.exec_()

    del editor
    del window
    del app


if __name__ == "__main__":
    main()

