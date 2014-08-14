"""
Regroup functions common to all examples.
"""
import sys
import os
from pyqode.core import api
from pyqode.qt import QtWidgets

_window = None

def get_file_path():
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        path = sys.argv[1]
    else:
        # default to a file encoded with big5 encoding (chinese).
        path = os.path.abspath(
            os.path.join('..', '..', 'test', 'files', 'big5hkscs.txt'))
    return path


def setup_editor(modes=None, panels=None):
    global _window
    _window = QtWidgets.QMainWindow()
    _window.setMinimumSize(800, 600)
    editor = api.CodeEdit(_window)
    _window.setCentralWidget(editor)
    _window.show()
    if modes:
        for mode in modes:
            editor.modes.append(mode)
    if panels:
        for panel, position in panels:
            editor.panels.append(panel, position)
    return editor
