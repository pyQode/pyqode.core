"""
This example show how to use the OutputWindow widget.
"""
import sys
from pyqode.qt import QtWidgets

from pyqode.core.widgets import OutputWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = OutputWindow()
    win.resize(800, 600)
    win.start_process(sys.executable, ['interactive_process.py'])
    win.show()
    app.exec_()
