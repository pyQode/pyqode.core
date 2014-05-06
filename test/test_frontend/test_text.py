# -*- coding: utf-8 -*-
"""
This module tests the text frontend module (pyqode.core.frontend.text)
"""
import mimetypes
import os
import sys

from PyQt4 import QtGui, QtCore
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
    cursor = frontend.goto_line(editor, 3, 0, move=False)
    process_events()
    assert editor.textCursor().blockNumber() != cursor.blockNumber()
    assert editor.textCursor().columnNumber() == cursor.columnNumber()
    cursor = frontend.goto_line(editor, 10, move=True)
    process_events()
    assert editor.textCursor().blockNumber() == cursor.blockNumber() == 9
    assert editor.textCursor().columnNumber() == cursor.columnNumber() == 0
    assert frontend.current_line_nbr(editor) == 10
    assert frontend.current_column_nbr(editor) == 0


def test_selected_text():
    global editor
    frontend.goto_line(editor, 3, 1, move=True)
    process_events()
    assert frontend.word_under_cursor(editor).selectedText() == 'T'
    assert frontend.word_under_cursor(
        editor, select_whole_word=True).selectedText() == 'This'


def test_word_under_mouse_cursor():
    global editor
    assert frontend.word_under_mouse_cursor(editor) is not None


def test_line_text():
    global editor
    frontend.goto_line(editor, 3, 0, move=True)
    assert frontend.current_line_text(editor) == __doc__.splitlines()[1]


def test_set_line_text():
    global editor
    frontend.set_line_text(editor, 3, 'haha')
    frontend.goto_line(editor, 3, 0, move=True)
    assert frontend.current_line_text(editor) == 'haha'


def test_remove_last_line():
    global editor
    count = frontend.line_count(editor)
    frontend.remove_last_line(editor)
    assert frontend.line_count(editor) == count - 1


def test_clean_document():
    global editor
    frontend.clean_document(editor)
    count = frontend.line_count(editor)
    frontend.set_line_text(editor, 1, '"""   ')
    editor.appendPlainText("")
    editor.appendPlainText("")
    editor.appendPlainText("")
    assert frontend.line_count(editor) == count + 3
    frontend.select_lines(editor, 1, frontend.line_count(editor))
    frontend.clean_document(editor)
    process_events()
    assert frontend.line_count(editor) == count


def test_select_lines():
    global editor
    frontend.select_lines(editor, 1, 5)
    process_events()
    QTest.qWait(1000)
    assert frontend.selection_range(editor) == (1, 5)
    frontend.clear_decorations(editor)


def test_line_pos_from_number():
    assert frontend.line_pos_from_number(editor, 1) is not None
    assert frontend.line_pos_from_number(
        editor, frontend.line_count(editor) + 10) is None


def test_line_nbr_from_position():
    frontend.open_file(editor, __file__)
    window.show()
    editor.repaint()
    sys.stderr.write(str(editor.visible_blocks))
    assert frontend.line_nbr_from_position(
        editor, frontend.line_pos_from_number(editor, 1)) is not None
    assert frontend.line_nbr_from_position(
        editor, 0) is None
    window.hide()
    process_events()


def test_open_file():
    global editor
    frontend.open_file(editor, __file__)
    assert editor.file_path == __file__
    assert editor.mime_type == 'text/x-python'


def test_save_file():
    global editor
    path = os.path.join(os.getcwd(), 'tmp.py')
    frontend.select_lines(editor, 1, 2)
    assert frontend.save_to_file(editor, path=path, encoding='utf-8') is True
    assert os.path.exists(path)
    assert editor.file_encoding == 'utf-8'
    assert frontend.save_to_file(editor, path=path, encoding='latin-1') is True
    assert editor.file_encoding == 'latin-1'
    frontend.open_file(editor, path, detect_encoding_func=None,
                       default_encoding='latin-1')
    QTest.qWait(1000)
    assert editor.file_encoding == 'latin-1'
    os.remove('tmp.py')
    frontend.open_file(editor, __file__)
    assert frontend.save_to_file(editor, path='/usr/bin', encoding='utf-8') \
        is False
    editor.file_path = None
    assert frontend.save_to_file(editor) is False


def test_mark_whole_doc_dirty():
    global editor
    frontend.mark_whole_doc_dirty(editor)


src = """def test_mark_whole_doc_dirty():
    global editor
    frontend.mark_whole_doc_dirty(editor)
"""


def test_line_indent():
    global editor
    editor.setPlainText(src, 'text/x-python', 'utf-8')
    assert frontend.line_indent(editor, 1) == 0
    assert frontend.line_indent(editor, 2) == 4
    frontend.open_file(editor, __file__)
    assert frontend.line_indent(editor, frontend.line_count(editor) - 1) == 4


def test_right_word():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'


def test_right_char():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_character(editor) == 'T'


def test_insert_text():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.insert_text(editor, 'haha', keep_position=True)
    assert frontend.get_right_word(editor) == 'hahaThis'
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.insert_text(editor, 'haha', keep_position=False)
    assert frontend.get_right_word(editor) == 'This'
    assert frontend.line_text(editor, 3).startswith('hahaThis')


def test_clear_selection():
    global editor
    frontend.open_file(editor, __file__)
    frontend.select_lines(editor, 1, 3)
    assert frontend.selected_text(editor) != ''
    frontend.clear_selection(editor)
    assert frontend.selected_text(editor) == ''


def test_move_right():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.move_right(editor)
    assert frontend.get_right_character(editor) == 'h'


def test_to_upper():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'
    frontend.select_lines(editor, 3, 2)
    frontend.selected_text_to_upper(editor)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'THIS'


def test_to_lower():
    global editor
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'
    frontend.select_lines(editor, 3, 2)
    frontend.selected_text_to_lower(editor)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'this'


def test_search_text():
    global editor
    import os.path
    frontend.open_file(editor, os.path.__file__)
    occurences, index = frontend.search_text(
        editor.document(), editor.textCursor(),
        'import', QtGui.QTextDocument.FindCaseSensitively)
    assert index == -1
    assert len(occurences) == 11


def test_keep_tc():
    @frontend.keep_tc_pos
    def move_cursor(editor, arg):
        assert arg == 'arg'
        frontend.goto_line(editor, 5)

    l, c = frontend.cursor_position(editor)
    move_cursor(editor, 'arg')
    nl, nc = frontend.cursor_position(editor)
    assert l == nl and c == nc


def test_get_mimetype():
    mimetypes.add_type('text/x-python', '.py')
    mimetypes.add_type('text/xml', '.ui')
    assert frontend.get_mimetype('file.py') == 'text/x-python'
    assert frontend.get_mimetype('file.ui') == 'text/xml'
    assert frontend.get_mimetype('file.foo') == 'text/plain'
