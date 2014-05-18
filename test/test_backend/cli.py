import logging
import sys

from PyQt5 import QtWidgets, QtCore

from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels


editor = None
app = None


def quit():
    global app, editor
    editor._client.send('shutdown')
    QtCore.QTimer.singleShot(2000, app.quit)


def main():
    global editor, app

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = frontend.CodeEdit()
    # frontend.start_server(editor, 'server.py')
    editor._client._port = int(sys.argv[1])
    editor._client._connect()
    editor._client._process = QtCore.QProcess()
    editor._client._process.running = True
    frontend.open_file(editor, __file__)
    cc_mode = modes.CodeCompletionMode()
    frontend.install_mode(editor, cc_mode)
    frontend.install_mode(editor,
                          modes.PygmentsSyntaxHighlighter(editor.document()))
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_panel(editor, panels.SearchAndReplacePanel(),
                           position=panels.SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    # window.show()

    cc_mode.request_completion()
    # frontend.goto_line()

    QtCore.QTimer.singleShot(5000, quit)
    app.exec_()
    del editor
    del window
    del app


if __name__ == "__main__":
    main()




