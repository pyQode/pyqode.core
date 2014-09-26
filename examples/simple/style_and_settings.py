#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this example, we are going to make a dark code editor widget and make it show visual
whitespaces.

"""
import sys
from pyqode.qt import QtWidgets, QtGui
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # code from the simple example
    editor = api.CodeEdit()
    editor.file.open(__file__)
    editor.modes.append(modes.CaretLineHighlighterMode())
    sh = modes.PygmentsSyntaxHighlighter(editor.document())
    editor.modes.append(sh)
    editor.panels.append(panels.SearchAndReplacePanel(),
                      api.Panel.Position.TOP)
    # make the code edit show whitespaces in dark gray
    editor.show_white_spaces = True
    editor.whitespaces_foreground = QtGui.QColor('#606020')

    # make a dark editor using the monokai theme
    sh.pygments_style = 'monokai'

    window.setCentralWidget(editor)
    window.show()

    app.exec_()

    editor.file.close()
    del editor
    del window
    del app


if __name__ == "__main__":
    main()

