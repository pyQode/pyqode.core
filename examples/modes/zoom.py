"""
Minimal example showing the use of the ZoomMode.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import ZoomMode


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(ZoomMode()))
    editor.appendPlainText(
        'Use Ctrl+Mouse wheel to zoom in/out\n'
        'Ctrl++ and Ctrl+- can also be used\n'
        'Ctrl+0 resets the editor zoom level to 0')
    editor.show()
    app.exec_()
    editor.close()
    del editor
    del app
