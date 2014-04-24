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
    Setup a QApplication and QCodeEdit which open the client module code
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


def test_add_decoration():
    global editor
    frontend.goto_line(editor, 2, 2)
    cursor = frontend.word_under_cursor(editor, select_whole_word=True)
    deco = frontend.TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    assert frontend.add_decoration(editor, deco)
    assert not frontend.add_decoration(editor, deco)
    assert deco.contains_cursor(cursor)
    # keep editor clean for next tests
    frontend.clear_decorations(editor)


def test_remove_decoration():
    global editor
    frontend.goto_line(editor, 3, 2)
    cursor = frontend.word_under_cursor(editor, select_whole_word=True)
    deco = frontend.TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    frontend.add_decoration(editor, deco)
    assert frontend.remove_decoration(editor, deco)
    # already removed, return False
    assert not frontend.remove_decoration(editor, deco)
    assert frontend.add_decoration(editor, deco)
    # keep editor clean for next tests
    frontend.clear_decorations(editor)


def test_clear_decoration():
    global editor
    # should work even when there are no more decorations
    frontend.clear_decorations(editor)

    cursor = frontend.word_under_cursor(editor, select_whole_word=True)
    deco = frontend.TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    frontend.add_decoration(editor, deco)
    assert not frontend.add_decoration(editor, deco)
    frontend.clear_decorations(editor)
    assert frontend.add_decoration(editor, deco)
    assert frontend.remove_decoration(editor, deco)
