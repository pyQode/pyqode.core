import os
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import SplittableCodeEditTabWidget


def open_in_explorer():
    print('open %r in explorer' %
          SplittableCodeEditTabWidget.tab_under_menu.file.path)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    tab_widget = SplittableCodeEditTabWidget()
    action = QtWidgets.QAction('Open in explorer', tab_widget)
    action.triggered.connect(open_in_explorer)
    tab_widget.add_context_action(action)
    tab_widget.setMinimumSize(800, 600)
    tab_widget.open_document(
        os.path.join(os.getcwd(), 'test_dir', 'readme.txt'))
    tab_widget.open_document(
        os.path.join(os.getcwd(), 'test_dir', 'subdir', 'readme.txt'))
    tab_widget.create_new_document('My New Document', '.pyw')
    tab_widget.create_new_document('My New Document', '.pyw')
    tab_widget.show()
    app.exec_()
