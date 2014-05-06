# -*- coding: utf-8 -*-
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
    Setup a QApplication and CodeEdit which open the client module code
    """
    global app, editor, window
    app = QtGui.QApplication.instance()
    window = QtGui.QMainWindow()
    editor = frontend.CodeEdit(window)
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


def test_modes():
    """
    Test to install, retrieve and remove a mode.

    """
    from pyqode.core.frontend.modes import CaseConverterMode
    global editor
    mode = CaseConverterMode()
    frontend.install_mode(editor, mode)
    m = frontend.get_mode(editor, CaseConverterMode)
    assert len(frontend.get_modes(editor)) == 1
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
    global editor, window
    window.show()
    panel = LineNumberPanel()
    frontend.install_panel(editor, panel, panel.Position.LEFT)
    QTest.qWait(1000)
    p, zone = frontend.get_panel(editor, LineNumberPanel, get_zone=True)
    p2 = frontend.get_panel(editor, LineNumberPanel, get_zone=False)
    assert p == panel == p2
    assert zone == panel.Position.LEFT
    assert len(frontend.get_panels(editor)) == 4
    for i in range(4):
        p.enabled = not p.enabled
    p = frontend.uninstall_panel(editor, LineNumberPanel)
    assert p == panel
    with pytest.raises(KeyError):
        frontend.uninstall_panel(editor, LineNumberPanel)
    window.hide()


def test_uninstall_all():
    global editor
    frontend.uninstall_all(editor)
    from pyqode.core.frontend.modes import CaseConverterMode
    from pyqode.core.frontend.panels import LineNumberPanel
    mode = CaseConverterMode()
    frontend.install_mode(editor, mode)
    frontend.install_panel(editor, LineNumberPanel(),
                           LineNumberPanel.Position.LEFT)
    frontend.uninstall_all(editor)
