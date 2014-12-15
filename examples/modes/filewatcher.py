"""
Minimal example showing the use of the FileWatcherMode.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtCore, QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.modes import FileWatcherMode


def simulate_external_modifcations():
    with open('test_file.txt', 'w') as f:
        f.write('test file modified!')


def print_reloaded_event():
    print('File reloaded')


if __name__ == '__main__':
    with open('test_file.txt', 'w') as f:
        f.write('test file')

    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    print(editor.modes.append(FileWatcherMode()))
    editor.file.open('test_file.txt')
    editor.modes.get(FileWatcherMode).file_reloaded.connect(print_reloaded_event)
    editor.modes.get(FileWatcherMode).auto_reload = False
    editor.show()
    QtCore.QTimer.singleShot(1000, simulate_external_modifcations)
    app.exec_()
    editor.close()
    del editor
    del app
