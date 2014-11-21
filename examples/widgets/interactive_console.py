"""
Simple interactive process used to demonstrate the use of the
InteractiveConsole widget.
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import InteractiveConsole
app = QtWidgets.QApplication(sys.argv)
console = InteractiveConsole()
console.start_process(sys.executable, ['interactive_process.py'])
console.show()
app.exec_()
