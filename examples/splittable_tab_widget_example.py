import os
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import GenericCodeEdit, InteractiveConsole
from pyqode.core.backend import server
from pyqode.core.widgets import SplittableTabWidget


class MyInteractiveConsole(InteractiveConsole):
    def __init__(self, parent=None):
        super(MyInteractiveConsole, self).__init__(parent)
        if sys.platform == 'win32':
            self.start_process('dir')
        else:
            self.start_process('ls', ['-s'])

    def split(self):
        return MyInteractiveConsole()


def print_last_tab_closed():
    print('last tab closed')


def print_current_tab(current):
    print('current tab changed: %r' % current)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = GenericCodeEdit(None, server.__file__)
    editor.file.open(__file__)
    tab_widget = SplittableTabWidget()
    tab_widget.add_tab(editor, title=os.path.split(__file__)[1])
    tab_widget.setMinimumSize(800, 600)
    tab_widget.last_tab_closed.connect(print_last_tab_closed)
    tab_widget.current_changed.connect(print_current_tab)
    mc = MyInteractiveConsole()
    tab_widget.add_tab(mc, 'Console')
    tab_widget.show()
    app.exec_()
