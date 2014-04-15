# -*- coding: utf-8 -*-
"""
A series of simple integration test, we check that a simple pyqode application
is running is working as expected, that the client server architecture works
as intended
"""
import os
import sys
import logging
from PyQt4 import QtCore
from PyQt4 import QtGui
from pyqode.core import frontend
from .helpers import cwd_at


# -----------------
# Simple application test
# -----------------
@cwd_at('test')
def test_app():
    """
    Test a simple but complete app
    """
    def _leave():
        """
        Leave test_app after a certain amount of time.
        """
        app = QtGui.QApplication.instance()
        app.exit(0)

    logging.basicConfig(level=logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    editor = frontend.QCodeEdit()
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    frontend.open_file(editor, __file__)
    # editor.show()
    QtCore.QTimer.singleShot(2000, _leave)
    app.exec_()
    frontend.stop_server(editor)
    del editor
    del app
