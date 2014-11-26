#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple example that shows how to setup CodeEdit.

In this example, we install a syntax highlighter mode (based on pygments), a
mode that highlights the current line and a _search and replace_ panel.

There are many other modes and panels, feel free to use this example as a
starting point to experiment.

"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.qt import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)

    # create editor and window
    window = QtWidgets.QMainWindow()
    editor = api.CodeEdit()
    window.setCentralWidget(editor)

    # start the backend as soon as possible
    editor.backend.start('server.py')

    # append some modes and panels
    editor.modes.append(modes.CodeCompletionMode())
    editor.modes.append(modes.CaretLineHighlighterMode())
    editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
    editor.panels.append(panels.SearchAndReplacePanel(),
                      api.Panel.Position.BOTTOM)

    # open a file
    editor.file.open(__file__)

    # run
    window.show()
    app.exec_()
    editor.file.close()


if __name__ == "__main__":
    main()
