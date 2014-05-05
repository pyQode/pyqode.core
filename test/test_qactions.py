# -*- coding: utf-8 -*-
"""
Test scripts for the actions module.
"""
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
import sys
from pyqode.core import frontend
from pyqode.core import actions
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels

app = None
window = None
editor = None


def setup_module(*args):
    """
    Setup a QApplication and CodeEdit which open the client module code
    """
    global app, editor, window
    app = QtGui.QApplication.instance()
    window = QtGui.QMainWindow()
    editor = frontend.CodeEdit()
    frontend.install_mode(editor, modes.IndenterMode())
    frontend.install_panel(editor, panels.SearchAndReplacePanel())


def teardown_module(*args):
    """
    Close server and exit QApplication
    """
    global editor, app
    frontend.stop_server(editor)
    app.exit(0)
    QTest.qWait(1000)
    del editor


def test_actions():
    global editor
    assert actions.delete.shortcut == QtGui.QKeySequence.Delete
    actions.delete.shortcut = 'Ctrl+D'
    adelete = None
    for action in editor.actions():
        if action.text() == 'Delete':
            adelete = action
            break
    if adelete:
        assert adelete.shortcut() == QtGui.QKeySequence.Delete
    editor.refresh_actions()
    if adelete:
        assert adelete.shortcut() == 'Ctrl+D'
