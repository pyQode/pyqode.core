"""
Minimal example showing the use of the CaseConverterMode.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import CaseConverterMode


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(CaseConverterMode()))
    editor.show()
    editor.setPlainText(
        'Press Ctrl+Shift+U to convert selected text to upper  case\n'
        'and Ctrl+U to convert the text to lower case.', '', '')
    editor.selectAll()
    app.exec_()
    editor.close()
    del editor
    del app
