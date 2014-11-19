"""
Minimal example showing the use of the ExtendedSelectionMode.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import ExtendedSelectionMode


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(ExtendedSelectionMode()))
    editor.file.open(__file__)
    editor.show()
    app.exec_()
    editor.close()
    del editor
    del app
