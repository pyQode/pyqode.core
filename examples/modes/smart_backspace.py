"""
Minimal example showing the use of the SmartBackSpaceMode.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit, TextHelper
from pyqode.core.backend import server
from pyqode.core.modes import SmartBackSpaceMode


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(SmartBackSpaceMode()))
    editor.show()
    editor.appendPlainText(
        '    Please press "BACKSPACE"; the 4 whitespaces should be deleted '
        'with a single key press')
    TextHelper(editor).goto_line(0, 4)
    app.exec_()
    editor.close()
    del editor
    del app
