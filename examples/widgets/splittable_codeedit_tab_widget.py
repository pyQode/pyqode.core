import os
import sys
from pyqode.qt import QtWidgets
from pyqode.core.widgets import SplittableCodeEditTabWidget


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    tab_widget = SplittableCodeEditTabWidget()
    tab_widget.setMinimumSize(800, 600)
    tab_widget.open_document(__file__)
    tab_widget.open_document(QtWidgets.__file__)
    tab_widget.create_new_document('My New Document', '.pyw')
    tab_widget.create_new_document('My New Document', '.pyw')
    tab_widget.show()
    app.exec_()
