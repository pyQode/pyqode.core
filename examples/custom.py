#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple example that shows how to setup a custom code editor widget based on
pyqode.core.QCodeEdit
"""
import sys
from PyQt4 import QtGui
import pyqode.core


def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = pyqode.core.QCodeEdit()
    editor.open_file(__file__)
    editor.install_mode(pyqode.core.PygmentsSyntaxHighlighter(
        editor.document()))
    editor.install_panel(pyqode.core.SearchAndReplacePanel(),
                        position=pyqode.core.PanelPosition.TOP)
    window.setCentralWidget(editor)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
