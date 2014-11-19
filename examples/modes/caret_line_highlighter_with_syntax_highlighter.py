"""
This example will show you that the caret line color is automatically set
by the syntax highlighter mode.

See how the color is different from the color obtained in
``caret_line_highligter.py``
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import CaretLineHighlighterMode
from pyqode.core.modes import PygmentsSyntaxHighlighter


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(CaretLineHighlighterMode()))
    print(editor.modes.append(PygmentsSyntaxHighlighter(editor.document())))
    editor.show()
    editor.appendPlainText('\n' * 10)
    app.exec_()
    editor.close()
    del editor
    del app
