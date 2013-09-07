import sys
from pyqode.qt import QtGui
import pyqode.core


def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = pyqode.core.QCodeEdit()
    editor.openFile(__file__)
    editor.installMode(pyqode.core.PygmentsSyntaxHighlighter(editor.document()))
    editor.installPanel(pyqode.core.SearchAndReplacePanel(),
                        position=pyqode.core.PanelPosition.TOP)
    window.setCentralWidget(editor)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
