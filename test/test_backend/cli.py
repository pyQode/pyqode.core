import logging
import sys
from pyqode.core.api.code_edit import CodeEdit

from pyqode.qt import QtWidgets, QtCore

from pyqode.core import modes


editor = None
app = None


def quit():
    global app, editor
    editor.backend.socket.send('shutdown')
    QtCore.QTimer.singleShot(2000, app.quit)


def main():
    global editor, app

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = CodeEdit()
    # connect to an existing instance of server
    editor.backend.socket._port = int(sys.argv[1])
    editor.backend.socket._connect()
    editor.backend.socket._process = QtCore.QProcess()
    editor.backend.socket._process.running = True
    editor.file.open(__file__)
    cc_mode = modes.CodeCompletionMode()
    editor.modes.append(cc_mode)
    window.setCentralWidget(editor)
    # window.show()

    cc_mode.request_completion()

    QtCore.QTimer.singleShot(5000, quit)
    app.exec_()
    del editor
    del window
    del app


if __name__ == "__main__":
    main()
