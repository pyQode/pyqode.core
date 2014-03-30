#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple example using a pre-made editor: pyqode.core.QGenericCodeEdit
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from pyqode.core import QGenericCodeEdit


def main():
    app = QApplication(sys.argv)
    editor = QGenericCodeEdit()
    editor.start_server('server.py')
    editor.open_file(__file__)
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
