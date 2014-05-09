# -*- coding: utf-8 -*-
"""
This module tests the text frontend module (pyqode.core.frontend.text)
"""
import mimetypes
import os
import sys

from PyQt4 import QtGui
from PyQt4.QtTest import QTest

from pyqode.core import frontend

from ..helpers import editor_open
from ..helpers import log_test_name


@editor_open(__file__)
@log_test_name
def test_line_count(editor):
    with open(__file__, 'r') as f:
        nb_lines = len(f.read().splitlines()) + 1
    assert frontend.line_count(editor) == nb_lines


@editor_open(__file__)
@log_test_name
def test_goto_line(editor):
    assert editor.textCursor().blockNumber() == 0
    assert editor.textCursor().columnNumber() == 0
    cursor = frontend.goto_line(editor, 3, 0, move=False)
    QTest.qWait(100)
    assert editor.textCursor().blockNumber() != cursor.blockNumber()
    assert editor.textCursor().columnNumber() == cursor.columnNumber()
    cursor = frontend.goto_line(editor, 10, move=True)
    QTest.qWait(100)
    assert editor.textCursor().blockNumber() == cursor.blockNumber() == 9
    assert editor.textCursor().columnNumber() == cursor.columnNumber() == 0
    assert frontend.current_line_nbr(editor) == 10
    assert frontend.current_column_nbr(editor) == 0


@editor_open(__file__)
@log_test_name
def test_selected_text(editor):
    frontend.goto_line(editor, 3, 1, move=True)
    QTest.qWait(100)
    assert frontend.word_under_cursor(editor).selectedText() == 'T'
    assert frontend.word_under_cursor(
        editor, select_whole_word=True).selectedText() == 'This'


@editor_open(__file__)
@log_test_name
def test_word_under_mouse_cursor(editor):
    assert frontend.word_under_mouse_cursor(editor) is not None


@editor_open(__file__)
@log_test_name
def test_line_text(editor):
    frontend.goto_line(editor, 3, 0, move=True)
    assert frontend.current_line_text(editor) == __doc__.splitlines()[1]


@editor_open(__file__)
@log_test_name
def test_set_line_text(editor):
    frontend.set_line_text(editor, 3, 'haha')
    frontend.goto_line(editor, 3, 0, move=True)
    assert frontend.current_line_text(editor) == 'haha'


@editor_open(__file__)
@log_test_name
def test_remove_last_line(editor):
    count = frontend.line_count(editor)
    frontend.remove_last_line(editor)
    assert frontend.line_count(editor) == count - 1


@editor_open(__file__)
@log_test_name
def test_clean_document(editor):
    frontend.clean_document(editor)
    count = frontend.line_count(editor)
    frontend.set_line_text(editor, 1, '"""   ')
    editor.appendPlainText("")
    editor.appendPlainText("")
    editor.appendPlainText("")
    assert frontend.line_count(editor) == count + 3
    frontend.select_lines(editor, 1, frontend.line_count(editor))
    frontend.clean_document(editor)
    QTest.qWait(100)
    assert frontend.line_count(editor) == count


@editor_open(__file__)
@log_test_name
def test_select_lines(editor):
    frontend.select_lines(editor, 1, 5)
    QTest.qWait(100)
    QTest.qWait(1000)
    assert frontend.selection_range(editor) == (1, 5)
    frontend.clear_decorations(editor)


@editor_open(__file__)
@log_test_name
def test_line_pos_from_number(editor):
    assert frontend.line_pos_from_number(editor, 1) is not None
    assert frontend.line_pos_from_number(
        editor, frontend.line_count(editor) + 10) is None


@editor_open(__file__)
@log_test_name
def test_line_nbr_from_position(editor):
    editor.repaint()
    sys.stderr.write(str(editor.visible_blocks))
    assert frontend.line_nbr_from_position(
        editor, frontend.line_pos_from_number(editor, 1)) is not None
    assert frontend.line_nbr_from_position(
        editor, 0) is None
    QTest.qWait(100)


@editor_open(__file__)
@log_test_name
def test_open_file(editor):
    frontend.open_file(editor, __file__)
    assert editor.file_path == __file__
    assert editor.mime_type == 'text/x-python'


@editor_open(__file__)
@log_test_name
def test_save_file(editor):
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


@editor_open(__file__)
@log_test_name
def test_mark_whole_doc_dirty(editor):
    frontend.mark_whole_doc_dirty(editor)


src = """@editor_open(__file__)
@log_test_name
def test_mark_whole_doc_dirty(editor):
    frontend.mark_whole_doc_dirty(editor)
"""


@editor_open(__file__)
@log_test_name
def test_line_indent(editor):
    editor.setPlainText(src, 'text/x-python', 'utf-8')
    assert frontend.line_indent(editor, 1) == 0
    assert frontend.line_indent(editor, 2) == 4
    frontend.open_file(editor, __file__)
    assert frontend.line_indent(editor, frontend.line_count(editor) - 1) == 4


@editor_open(__file__)
@log_test_name
def test_right_word(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'


@editor_open(__file__)
@log_test_name
def test_right_char(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_character(editor) == 'T'


@editor_open(__file__)
@log_test_name
def test_insert_text(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.insert_text(editor, 'haha', keep_position=True)
    assert frontend.get_right_word(editor) == 'hahaThis'
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.insert_text(editor, 'haha', keep_position=False)
    assert frontend.get_right_word(editor) == 'This'
    assert frontend.line_text(editor, 3).startswith('hahaThis')


@editor_open(__file__)
@log_test_name
def test_clear_selection(editor):
    frontend.open_file(editor, __file__)
    frontend.select_lines(editor, 1, 3)
    assert frontend.selected_text(editor) != ''
    frontend.clear_selection(editor)
    assert frontend.selected_text(editor) == ''


@editor_open(__file__)
@log_test_name
def test_move_right(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    frontend.move_right(editor)
    assert frontend.get_right_character(editor) == 'h'


@editor_open(__file__)
@log_test_name
def test_to_upper(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'
    frontend.select_lines(editor, 3, 2)
    frontend.selected_text_to_upper(editor)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'THIS'


@editor_open(__file__)
@log_test_name
def test_to_lower(editor):
    frontend.open_file(editor, __file__)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'This'
    frontend.select_lines(editor, 3, 2)
    frontend.selected_text_to_lower(editor)
    frontend.goto_line(editor, 3)
    assert frontend.get_right_word(editor) == 'this'


@editor_open(__file__)
@log_test_name
def test_search_text(editor):
    import os.path
    frontend.open_file(editor, os.path.__file__)
    occurences, index = frontend.search_text(
        editor.document(), editor.textCursor(),
        'import', QtGui.QTextDocument.FindCaseSensitively)
    assert index == -1
    assert len(occurences) == 11


@editor_open(__file__)
@log_test_name
def test_keep_tc(editor):
    @frontend.keep_tc_pos
    def move_cursor(editor, arg):
        assert arg == 'arg'
        frontend.goto_line(editor, 5)

    l, c = frontend.cursor_position(editor)
    move_cursor(editor, 'arg')
    nl, nc = frontend.cursor_position(editor)
    assert l == nl and c == nc


@editor_open(__file__)
@log_test_name
def test_get_mimetype(editor):
    mimetypes.add_type('text/x-python', '.py')
    mimetypes.add_type('text/xml', '.ui')
    assert frontend.get_mimetype('file.py') == 'text/x-python'
    assert frontend.get_mimetype('file.ui') == 'text/xml'
    assert frontend.get_mimetype('file.foo') == 'text/plain'
