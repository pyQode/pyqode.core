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
from pyqode.core import settings
from pyqode.core import style
from pyqode.core.editor import QCodeEdit
from pyqode.core.modes import PygmentsSyntaxHighlighter
from pyqode.core.modes import CaretLineHighlighterMode
from pyqode.core.panels import SearchAndReplacePanel


def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()

    # make the code edit show whitespaces in dark gray
    settings.show_white_spaces = True
    style.whitespaces_foreground = QtGui.QColor('#606020')

    # make a dark editor using the monokai theme
    style.pygments_style = 'monokai'

    # code from the simple example
    editor = QCodeEdit()
    editor.open_file(__file__)
    editor.install_mode(CaretLineHighlighterMode())
    editor.install_mode(PygmentsSyntaxHighlighter(editor.document()))
    editor.install_panel(SearchAndReplacePanel(),
                         position=SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()