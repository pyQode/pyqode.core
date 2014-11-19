"""
Minimal example showing the use of the CaretLineHighlighterMode.

This example editor does not have a SyntaxHighlighterMode, the caret line color
is simply derived from the background color (darker for white background,
lighter for dark background)
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import CaretLineHighlighterMode


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(CaretLineHighlighterMode()))
    editor.show()
    editor.appendPlainText('\n' * 10)
    app.exec_()
    editor.close()
    del editor
    del app
