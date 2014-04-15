"""
This module tests the extension frontend module
(pyqode.core.frontend.extension)
"""
import os
import sys

from PyQt4 import QtGui
from PyQt4.QtTest import QTest

import pytest
from pyqode.core import frontend
from ..helpers import cwd_at, wait_for_connected


app = None
editor = None
window = None


def process_events():
    global app
    app.processEvents()


@cwd_at('test')
def setup_module():
    """
    Setup a QApplication and QCodeEdit which open the client module code
    """
    global app, editor, window
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = frontend.QCodeEdit(window)
    window.setCentralWidget(editor)
    window.resize(800, 600)
    frontend.open_file(editor, __file__)
    # window.show()
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    wait_for_connected(editor)


def teardown_module():
    """
    Close server and exit QApplication
    """
    global editor, app
    frontend.stop_server(editor)
    app.exit(0)
    QTest.qWait(1000)
    del editor
    del app


def test_modes():
    """
    Test to install, retrieve and remove a mode.

    """
    from pyqode.core.frontend.modes import CaseConverterMode
    global editor
    mode = CaseConverterMode()
    frontend.install_mode(editor, mode)
    m = frontend.get_mode(editor, CaseConverterMode)
    assert m == mode
    m = frontend.uninstall_mode(editor, CaseConverterMode)
    assert m == mode
    with pytest.raises(KeyError):
        frontend.uninstall_mode(editor, CaseConverterMode)


def test_panels():
    """
    Test to install, retrieve and remove a panel

    """
    from pyqode.core.frontend.panels import LineNumberPanel
    global editor
    panel = LineNumberPanel()
    frontend.install_panel(editor, panel, panel.Position.LEFT)
    QTest.qWait(1000)
    p, zone = frontend.get_panel(editor, LineNumberPanel, get_zone=True)
    assert p == panel
    assert zone == panel.Position.LEFT
    p = frontend.uninstall_panel(editor, LineNumberPanel)
    assert p == panel
    with pytest.raises(KeyError):
        frontend.uninstall_panel(editor, LineNumberPanel)
