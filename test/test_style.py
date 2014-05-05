# -*- coding: utf-8 -*-
"""
Test scripts for the settings module.
"""
import os
import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core import style


from . import helpers
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels


@helpers.cwd_at('test')
def setup_module(*args):
    """
    Setup a QApplication and CodeEdit which open the client module code
    """
    print('setup')
    global app, editor, window, code_completion_mode
    app = QtGui.QApplication.instance()
    window = QtGui.QMainWindow()
    editor = frontend.CodeEdit(window)
    frontend.install_mode(editor, modes.IndenterMode())
    frontend.install_mode(editor, modes.AutoIndentMode())
    frontend.install_mode(editor, modes.FileWatcherMode())
    frontend.install_mode(editor, modes.RightMarginMode())
    frontend.install_panel(editor, panels.SearchAndReplacePanel())
    code_completion_mode = modes.CodeCompletionMode()
    frontend.install_mode(editor, code_completion_mode)
    window.setCentralWidget(editor)
    window.resize(800, 600)
    # window.show()
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    helpers.wait_for_connected(editor)


def teardown_module(*args):
    """
    Close server and exit QApplication
    """
    global editor, app
    frontend.stop_server(editor)
    app.exit(0)
    QTest.qWait(1000)
    del editor


def test_whitespaces_foreground():
    global editor
    assert style.whitespaces_foreground.name() == QtGui.QColor(
        'light gray').name()
    style.whitespaces_foreground = QtGui.QColor('#FFFF00')
    assert editor.whitespaces_foreground.name() != QtGui.QColor(
        '#FFFF00').name()
    editor.refresh_style()
    assert editor.whitespaces_foreground.name() == QtGui.QColor(
        '#FFFF00').name()
    style.whitespaces_foreground = QtGui.QColor('light gray')
