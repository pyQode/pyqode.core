#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example show you how to change default action properties.

Here we change the duplicate line action to use Ctrl+Shift+Down instead of
Ctrl+D, we also chnage the text to upper case.

"""
import sys
from pyqode.qt import QtWidgets

from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # configure editor (see examples/simple/basic.py)
    editor = api.CodeEdit()
    editor.file.open(__file__)
    editor.modes.append(modes.CaretLineHighlighterMode())
    editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
    editor.panels.append(panels.SearchAndReplacePanel(),
                      api.Panel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()

    # Change action properties
    editor.action_duplicate_line.setShortcut('Ctrl+Shift+Down')
    editor.action_duplicate_line.setText('DUPLICATE LINE')

    app.exec_()
    editor.file.close()
    del editor
    del window
    del app


if __name__ == "__main__":
    main()
