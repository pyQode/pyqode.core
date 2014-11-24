# import os
# import sys
# from pyqode.core.backend import server
#
# import logging
# logging.basicConfig(level=logging.DEBUG, filename='cli.log', filemode='w')
#
# sys.path.insert(0, os.path.abspath(
#     os.path.join(os.getcwd(), '..', '..', '..')))
# from pyqode.core.api.code_edit import CodeEdit
# from pyqode.qt import QtWidgets, QtCore
# from pyqode.core import modes
#
#
# editor = None
# app = None
#
#
# def quit():
#     global app, editor
#     editor.close()
#     QtCore.QTimer.singleShot(2000, app.quit)
#
#
# def main():
#     global editor, app
#
#     app = QtWidgets.QApplication(sys.argv)
#     window = QtWidgets.QMainWindow()
#     editor = CodeEdit()
#     editor.backend.start(server.__file__)
#     editor.backend._port = 6789  # hack to connect to the server started
#                                  # by pytest
#     editor.file.open(__file__)
#     cc_mode = modes.CodeCompletionMode()
#     editor.modes.append(cc_mode)
#     window.setCentralWidget(editor)
#     window.show()
#
#     timer = QtCore.QTimer()
#     timer.timeout.connect(cc_mode.request_completion)
#     timer.start(1000)
#
#     QtCore.QTimer.singleShot(5000, quit)
#
#     app.exec_()
#     del editor
#     del window
#     del app
#
#
# if __name__ == "__main__":
#     main()
