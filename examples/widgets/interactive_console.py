"""
Simple interactive process used to demonstrate the use of the
InteractiveConsole widget.
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import InteractiveConsole
app = QtWidgets.QApplication(sys.argv)
console = InteractiveConsole()
console.start_process(r'C:\Users\Colin\bin\TEST.exe')
console.show()
app.exec_()
