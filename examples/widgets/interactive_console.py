"""
This example show you how to use the InteractiveConsole. To make this example
complete and cross-platform, we created an interactive process which prints some text
and asks for user inputs. That way you can see that the console is actually interactive.
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import InteractiveConsole
app = QtWidgets.QApplication(sys.argv)
console = InteractiveConsole()
console.start_process(sys.executable, ['interactive_process.py'])
console.show()
app.exec_()
