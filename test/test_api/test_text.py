# -*- coding: utf-8 -*-
"""
This module tests the text frontend module (pyqode.core.api.TextHelper)
"""
import mimetypes
import os
import sys
import pytest
from pyqode.core.api.utils import TextHelper, keep_tc_pos

from pyqode.qt import QtGui, QtWidgets
from pyqode.qt.QtTest import QTest
from ..helpers import editor_open


@editor_open(__file__)
def test_line_count(editor):
    with open(__file__, 'r') as f:
        nb_lines = len(f.read().splitlines()) + 1
    assert TextHelper(editor).line_count() == nb_lines


@editor_open(__file__)
def test_goto_line(editor):
    assert editor.textCursor().blockNumber() == 0
    assert editor.textCursor().columnNumber() == 0
    cursor = TextHelper(editor).goto_line(2, 0, move=False)
    QTest.qWait(100)
    assert editor.textCursor().blockNumber() != cursor.blockNumber()
    assert editor.textCursor().columnNumber() == cursor.columnNumber()
    cursor = TextHelper(editor).goto_line(9, move=True)
    QTest.qWait(100)
    assert editor.textCursor().blockNumber() == cursor.blockNumber() == 9
    assert editor.textCursor().columnNumber() == cursor.columnNumber() == 0
    assert TextHelper(editor).current_line_nbr() == 9
    assert TextHelper(editor).current_column_nbr() == 0


@editor_open(__file__)
def test_selected_text(editor):
    helper = TextHelper(editor)
    helper.goto_line(2, 1, move=True)
    QTest.qWait(100)
    assert helper.word_under_cursor().selectedText() == 'T'
    assert helper.word_under_cursor(
        select_whole_word=True).selectedText() == 'This'


@editor_open(__file__)
def test_word_under_mouse_cursor(editor):
    assert TextHelper(editor).word_under_mouse_cursor() is not None


@editor_open(__file__)
def test_line_text(editor):
    TextHelper(editor).goto_line(2, 0, move=True)
    assert TextHelper(editor).current_line_text() == __doc__.splitlines()[1]


@editor_open(__file__)
def test_set_line_text(editor):
    TextHelper(editor).set_line_text(2, 'haha')
    TextHelper(editor).goto_line(2, 0, move=True)
    assert TextHelper(editor).current_line_text() == 'haha'


@editor_open(__file__)
def test_remove_last_line(editor):
    count = TextHelper(editor).line_count()
    TextHelper(editor).remove_last_line()
    assert TextHelper(editor).line_count() == count - 1


@editor_open(__file__)
def test_clean_document(editor):
    TextHelper(editor).clean_document()
    count = TextHelper(editor).line_count()
    TextHelper(editor).set_line_text(0, '"""   ')
    editor.appendPlainText("")
    editor.appendPlainText("")
    editor.appendPlainText("")
    assert TextHelper(editor).line_count() == count + 3
    TextHelper(editor).select_lines(0, TextHelper(editor).line_count())
    TextHelper(editor).clean_document()
    QTest.qWait(100)
    assert TextHelper(editor).line_count() == count


@editor_open(__file__)
def test_select_lines(editor):
    TextHelper(editor).select_lines(0, 4)
    QTest.qWait(100)
    QTest.qWait(1000)
    assert TextHelper(editor).selection_range() == (0, 4)
    TextHelper(editor).select_lines(-1, 10)
    assert TextHelper(editor).selection_range() == (0, 10)
    editor.decorations.clear()


@editor_open(__file__)
def test_line_pos_from_number(editor):
    assert TextHelper(editor).line_pos_from_number(0) is not None
    # out of range line will return the bottom of the document or the top
    assert TextHelper(editor).line_pos_from_number(-1) == 0
    pos = TextHelper(editor).line_pos_from_number(
        TextHelper(editor).line_count() + 10)
    assert pos is not None
    assert pos > 0


@editor_open(__file__)
def test_line_nbr_from_position(editor):
    editor.repaint()
    sys.stderr.write(str(editor.visible_blocks))
    assert TextHelper(editor).line_nbr_from_position(
        TextHelper(editor).line_pos_from_number(0)) is not None
    assert TextHelper(editor).line_nbr_from_position(-1) == -1
    QTest.qWait(100)


@editor_open(__file__)
def test_open_file(editor):
    editor.file.open(__file__, 'text/x-python')
    assert editor.file.path == __file__
    assert editor.file.mimetype == 'text/x-python'


@editor_open(__file__)
def test_save_file(editor):
    path = os.path.join(os.getcwd(), 'tmp.py')
    TextHelper(editor).select_lines(0, 1)
    assert isinstance(editor, QtWidgets.QPlainTextEdit)
    assert not editor.dirty
    editor.appendPlainText('some text')
    assert editor.dirty
    editor.file.save(path, encoding='utf-8')
    assert os.path.exists(path)
    assert editor.file.encoding == 'utf-8'
    editor.file.save(path, encoding='latin-1')
    assert editor.file.encoding == 'latin-1'
    os.remove('tmp.py')
    editor.file.open(__file__)
    with pytest.raises(IOError):
        editor.file.save(path='/usr/bin') is False
    editor.file._path = ''
    editor.file.save() is False


@editor_open(__file__)
def test_mark_whole_doc_dirty(editor):
    TextHelper(editor).mark_whole_doc_dirty()


src = """def test_mark_whole_doc_dirty(editor):
    TextHelper(editor).mark_whole_doc_dirty()
"""


@editor_open(__file__)
def test_line_indent(editor):
    editor.setPlainText(src, 'text/x-python', 'utf-8')
    assert TextHelper(editor).line_indent(0) == 0
    assert TextHelper(editor).line_indent(1) == 4
    editor.file.open(__file__)
    assert TextHelper(editor).line_indent(TextHelper(editor).line_count() - 2) == 4


@editor_open(__file__)
def test_right_word(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_word() == 'This'


def test_right_char(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_character() == 'T'


@editor_open(__file__)
def test_insert_text(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    TextHelper(editor).insert_text('haha', keep_position=True)
    assert TextHelper(editor).get_right_word() == 'hahaThis'
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    TextHelper(editor).insert_text('haha', keep_position=False)
    assert TextHelper(editor).get_right_word() == 'This'
    assert TextHelper(editor).line_text(2).startswith('hahaThis')


@editor_open(__file__)
def test_clear_selection(editor):
    editor.file.open(__file__)
    helper = TextHelper(editor)
    TextHelper(editor).select_lines(0, 2)
    assert helper.selected_text() != ''
    TextHelper(editor).clear_selection()
    assert helper.selected_text() == ''


@editor_open(__file__)
def test_move_right(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    TextHelper(editor).move_right()
    assert TextHelper(editor).get_right_character() == 'h'


@editor_open(__file__)
def test_to_upper(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_word() == 'This'
    TextHelper(editor).select_lines(2, 1)
    TextHelper(editor).selected_text_to_upper()
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_word() == 'THIS'


@editor_open(__file__)
def test_to_lower(editor):
    editor.file.open(__file__)
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_word() == 'This'
    TextHelper(editor).select_lines(2, 1)
    TextHelper(editor).selected_text_to_lower()
    TextHelper(editor).goto_line(2)
    assert TextHelper(editor).get_right_word() == 'this'


@editor_open(__file__)
def test_search_text(editor):
    occurences, index = TextHelper(editor).search_text(
        editor.textCursor(), 'import', QtGui.QTextDocument.FindCaseSensitively)
    assert index == -1
    assert len(occurences) == 10


@editor_open(__file__)
def test_keep_tc(editor):
    @keep_tc_pos
    def move_cursor(editor, arg):
        assert arg == 'arg'
        TextHelper(editor).goto_line(4)

    l, c = TextHelper(editor).cursor_position()
    move_cursor(editor, 'arg')
    nl, nc = TextHelper(editor).cursor_position()
    assert l == nl and c == nc


@editor_open(__file__)
def test_get_mimetype(editor):
    from pyqode.core import managers
    assert managers.FileManager.get_mimetype('file.py') == 'text/x-python'
    assert managers.FileManager.get_mimetype('file.ui') == 'text/xml'
    assert managers.FileManager.get_mimetype('file.foo') == 'text/x-plain'


@editor_open(__file__)
def test_prev_line_text(editor):
    TextHelper(editor).goto_line(1)
    assert TextHelper(editor).previous_line_text() == '# -*- coding: utf-8 -*-'


@editor_open(__file__)
def test_select_whole_line(editor):
    cursor = TextHelper(editor).select_whole_line(2)
    assert isinstance(cursor, QtGui.QTextCursor)
    assert cursor.hasSelection()
    assert cursor.selectionStart() == 28
    assert cursor.selectionEnd() == 99


def test_extended_selection(editor):
    for line, column, text in [(8, 15, 'pyqode.core.api.utils'),
                               (8, 1, 'from')]:
        editor.file.open(__file__)
        QTest.qWait(1000)
        cursor = editor.textCursor()
        assert not cursor.hasSelection()
        helper = TextHelper(editor)
        helper.goto_line(line, column)
        assert helper.cursor_position()[0] == line
        assert helper.cursor_position()[1] == column
        cursor = editor.textCursor()
        assert text in cursor.block().text()
        helper.select_extended_word()
        cursor = editor.textCursor()
        assert cursor.hasSelection()
        assert cursor.selectedText() == text


@editor_open(__file__)
def test_matched_selection(editor):
    line, column, text = 297, 14, '''__file__'''
    cursor = editor.textCursor()
    assert not cursor.hasSelection()
    helper = TextHelper(editor)
    helper.goto_line(line, column)
    assert helper.cursor_position()[0] == line
    assert helper.cursor_position()[1] == column
    cursor = editor.textCursor()
    helper.match_select()
    cursor = editor.textCursor()
    assert cursor.hasSelection()
    assert text in cursor.selectedText()
