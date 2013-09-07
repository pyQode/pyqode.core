import sys
from pyqode.qt.QtGui import QApplication
from pyqode.qt.QtGui import QMainWindow
from pyqode.core import QGenericCodeEdit


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    editor = QGenericCodeEdit()
    editor.openFile(__file__)
    window.setCentralWidget(editor)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
