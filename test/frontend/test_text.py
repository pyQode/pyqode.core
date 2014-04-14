"""
This module tests the text frontend module (pyqode.core.frontend.text)
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
    window.show()
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


def test_line_count():
    global editor
    with open(__file__, 'r') as f:
        nb_lines = len(f.read().splitlines()) + 1
    assert frontend.line_count(editor) == nb_lines


def test_goto_line():
    global editor, window
    QTest.qWaitForWindowShown(window)
    assert editor.textCursor().blockNumber() == 0
    assert editor.textCursor().columnNumber() == 0
    cursor = frontend.goto_line(editor, 2, 0, move=False)
    process_events()
    assert editor.textCursor().blockNumber() != cursor.blockNumber()
    assert editor.textCursor().columnNumber() == cursor.columnNumber()
    cursor = frontend.goto_line(editor, 10, move=True)
    process_events()
    assert editor.textCursor().blockNumber() == cursor.blockNumber() == 9
    assert editor.textCursor().columnNumber() == cursor.columnNumber() == 0
    assert frontend.cursor_line_nbr(editor) == 10
    assert frontend.cursor_column_nbr(editor) == 0


def test_selected_text():
    global editor
    frontend.goto_line(editor, 2, 1, move=True)
    process_events()
    assert frontend.word_under_cursor(editor).selectedText() == 'T'
    assert frontend.word_under_cursor(
        editor, select_whole_word=True).selectedText() == 'This'


def test_line_text():
    global editor
    frontend.goto_line(editor, 2, 0, move=True)
    assert frontend.current_line_text(editor) == __doc__.splitlines()[1]


def test_set_line_text():
    global editor
    frontend.set_line_text(editor, 2, 'haha')
    frontend.goto_line(editor, 2, 0, move=True)
    assert frontend.current_line_text(editor) == 'haha'


def test_remove_last_line():
    global editor
    count = frontend.line_count(editor)
    frontend.remove_last_line(editor)
    assert frontend.line_count(editor) == count - 1


def test_clean_document():
    global editor
    count = frontend.line_count(editor) + 1
    editor.appendPlainText("\n\n\n")
    assert frontend.line_count(editor) == count + 3
    frontend.clean_document(editor)
    process_events()
    assert frontend.line_count(editor) == count


def test_select_lines():
    global editor
    frontend.select_lines(editor, 1, 5)
    process_events()
    QTest.qWait(1000)
    assert frontend.selection_range(editor) == (1, 5)


def test_line_pos_line_nbr():
    global editor
    # ensure we are at the top of the document
    frontend.goto_line(editor, 1, 0, move=True)
    process_events()
    pos = frontend.line_pos_from_number(editor, 2)
    assert pos is not None
    nbr = frontend.line_nbr_from_position(editor, pos)
    assert nbr == 2

def test_open_file():
    global editor
    frontend.open_file(editor, __file__)
    assert editor.file_path == __file__
    assert editor.file_encoding == 'ascii'
    assert editor.mime_type == 'text/x-python'
    with open(__file__, 'r') as f:
        assert editor.toPlainText() == f.read()
