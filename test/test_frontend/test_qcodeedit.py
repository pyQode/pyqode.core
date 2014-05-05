# -*- coding: utf-8 -*-
"""
This module tests the CodeEdit class
"""
import mimetypes
import os
import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest

import pytest
from pyqode.core import frontend, style
from pyqode.core.frontend import panels, modes
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


def test_set_plain_text():
    global editor
    with pytest.raises(TypeError):
        editor.setPlainText('Some text')
    editor.setPlainText('Some text', mimetypes.guess_type('file.py'), 'utf-8')
    assert editor.toPlainText() == 'Some text'


def test_actions():
    # 13 default shortcuts
    assert len(editor.actions()) == 13
    action = QtGui.QAction('my_action', editor)
    editor.add_action(action)
    assert len(editor.actions()) == 14
    editor.add_separator()
    assert len(editor.actions()) == 15


def test_duplicate_line():
    editor.setPlainText('Some text', mimetypes.guess_type('file.py'), 'utf-8')
    assert editor.toPlainText() == 'Some text'
    editor.duplicate_line()
    assert editor.toPlainText() == 'Some text\nSome text'


def test_show_tooltip():
    editor.show_tooltip(QtCore.QPoint(0, 0), 'A tooltip')


def test_margin_size():
    global editor, window
    # we really need to show the window here to get correct margin size.
    window.show()
    QTest.qWaitForWindowShown(window)
    for position in frontend.Panel.Position.iterable():
        # there is no panel on this widget, all margin must be 0
        assert editor.margin_size(position) == 0
    panel = frontend.panels.LineNumberPanel()
    frontend.install_panel(editor, panel,
                           position=frontend.Panel.Position.LEFT)
    panel.setVisible(True)
    process_events()
    # as the window is not visible, we need to refresh panels manually
    assert editor.margin_size(frontend.Panel.Position.LEFT) != 0
    window.hide()


def test_zoom():
    global editor
    assert editor.font_size == style.font_size
    editor.zoom_in()
    assert editor.font_size == style.font_size + 1
    editor.reset_zoom()
    assert editor.font_size == style.font_size
    editor.zoom_out()
    assert editor.font_size == style.font_size - 1


def test_indent():
    editor.setPlainText('Some text', mimetypes.guess_type('file.py'), 'utf-8')
    frontend.goto_line(editor, 1)
    editor.indent()
    # no indenter mode -> indent should not do anything
    assert editor.toPlainText() == 'Some text'
    editor.un_indent()
    assert editor.toPlainText() == 'Some text'
    # add indenter mode, call to indent/un_indent should now work
    frontend.install_mode(editor, modes.IndenterMode())
    editor.setPlainText('Some text', mimetypes.guess_type('file.py'), 'utf-8')
    frontend.goto_line(editor, 1)
    editor.indent()
    assert editor.toPlainText() == '    Some text'
    editor.un_indent()
    assert editor.toPlainText() == 'Some text'
