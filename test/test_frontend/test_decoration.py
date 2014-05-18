# -*- coding: utf-8 -*-
"""
This module tests the extension frontend module
(pyqode.core.frontend.extension)
"""
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtTest import QTest
from pyqode.core import frontend

from ..helpers import log_test_name
from ..helpers import editor_open


@editor_open(__file__)
@log_test_name
def test_add_decoration(editor):
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


@editor_open(__file__)
@log_test_name
def test_remove_decoration(editor):
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


@editor_open(__file__)
@log_test_name
def test_clear_decoration(editor):
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


@editor_open(__file__)
@log_test_name
def test_constructors(editor):
    deco = frontend.TextDecoration(editor.textCursor(),
                                   start_pos=10, end_pos=15)
    deco = frontend.TextDecoration(editor.textCursor(),
                                   start_line=10, end_line=15)


@editor_open(__file__)
@log_test_name
def test_formats(editor):
    deco = frontend.TextDecoration(editor.textCursor(),
                                   start_line=10, end_line=15)
    deco.set_foreground(QtGui.QColor('#FF0000'))
    deco.set_outline(QtGui.QColor('#FF0000'))
    deco.set_as_spell_check(QtGui.QColor('#FF0000'))
    deco.set_as_error(QtGui.QColor('#FF0000'))
    deco.set_as_error()
    deco.set_as_warning()
