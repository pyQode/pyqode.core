from pyqode.qt import QtWidgets, QtCore

__author__ = 'colin'


class TabBar(QtWidgets.QTabBar):
    """
    Tab bar specialized to allow the user to close a tab using mouse middle
    click. Also exposes a double clicked signal.
    """
    double_clicked = QtCore.Signal()

    def __init__(self, parent):
        QtWidgets.QTabBar.__init__(self, parent)
        self.setTabsClosable(True)

    def mousePressEvent(self, event):
        QtWidgets.QTabBar.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.MiddleButton:
            self.parentWidget().tabCloseRequested.emit(self.tabAt(
                event.pos()))

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
