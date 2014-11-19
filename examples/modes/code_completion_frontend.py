"""
This example show you how to setup a code completion mode on the frontend

This example uses the code_completion_backend.py example as a backend server.


The custom code completion provider will provides the following completions:
    - Code
    - completion
    - example
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.modes import CodeCompletionMode


# use a custom server that show how to create a custom code completion provider
import code_completion_backend


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(code_completion_backend.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(CodeCompletionMode()))
    editor.show()
    app.exec_()
    editor.close()
    del editor
    del app
