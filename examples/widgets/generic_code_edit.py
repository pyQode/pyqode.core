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
from pyqode.qt import QtWidgets
from pyqode.core.widgets import GenericCodeEdit


def main():
    app = QtWidgets.QApplication(sys.argv)

    # create editor and window
    window = QtWidgets.QMainWindow()
    editor = GenericCodeEdit()

    # open a file
    editor.file.open(__file__)
    window.setCentralWidget(editor)

    # run
    window.show()
    app.exec_()
    editor.file.close()


if __name__ == "__main__":
    main()
