#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple example that shows how to setup QCodeEdit, in this example we install
a syntax highlighter mode (base on pygments), a mode that highlights the
current line and a _search and replace_ panel.

There are many other modes and panels, feel free to use this example as a
starting point and experiment!
"""
import sys
from PyQt4 import QtGui
from pyqode.core.editor import QCodeEdit
from pyqode.core.modes import PygmentsSyntaxHighlighter
from pyqode.core.modes import CaretLineHighlighterMode
from pyqode.core.panels import SearchAndReplacePanel


def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = QCodeEdit()
    editor.open_file(__file__)
    editor.install_mode(PygmentsSyntaxHighlighter(editor.document()))
    editor.install_mode(CaretLineHighlighterMode())
    editor.install_panel(SearchAndReplacePanel(),
                         position=SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
