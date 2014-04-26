"""
This package contains the code of the notepad application:

    - editor: contains our custom CodeEdit class definition. This is just
    a CodeEdit configured with a set of modes and panels.

    - main_window: This is the main window of the application

    - server.py: This is the server script for the pyqode backend.
"""
import sys
from PyQt4.QtGui import QApplication
from notepad.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()
