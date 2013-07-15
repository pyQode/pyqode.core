"""
This is a simple test script to is meant to be run by Travis CI to ensure
everything works properly foreach bindings on each supported python
version (2.7, 3.2, 3.3).

It runs a QApplication and shows a QGenericCodeEdit for 500ms.
"""
import sys
from pcef.qt import QtCore, QtGui
from pcef.core import QGenericCodeEdit


def leave():
    app = QtGui.QApplication.instance()
    app.exit(0)


def main():
    app = QtGui.QApplication(sys.argv)
    editor = QGenericCodeEdit()
    editor.openFile(__file__)
    editor.show()
    QtCore.QTimer.singleShot(500, leave)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
