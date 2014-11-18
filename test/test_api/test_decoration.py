# -*- coding: utf-8 -*-
"""
This module tests the extension frontend module
(pyqode.core.api.decoration and pyqode.core.managers.TextDecorationManager)
"""
from pyqode.core.api import TextHelper, TextDecoration
from pyqode.qt import QtGui
from ..helpers import editor_open


@editor_open(__file__)
def test_add_decoration(editor):
    helper = TextHelper(editor)
    helper.goto_line(2, 2)
    cursor = helper.word_under_cursor(select_whole_word=True)
    deco = TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    editor.decorations.append(deco)
    assert not editor.decorations.append(deco)
    assert deco.contains_cursor(cursor)
    # keep editor clean for next tests
    editor.decorations.clear()


@editor_open(__file__)
def test_remove_decoration(editor):
    helper = TextHelper(editor)
    TextHelper(editor).goto_line(1, 2)
    cursor = helper.word_under_cursor(select_whole_word=True)
    deco = TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    editor.decorations.append(deco)
    assert editor.decorations.remove(deco)
    # already removed, return False
    assert not editor.decorations.remove(deco)
    assert editor.decorations.append(deco)
    # keep editor clean for next tests
    editor.decorations.clear()


@editor_open(__file__)
def test_clear_decoration(editor):
    # should work even when there are no more decorations
    helper = TextHelper(editor)
    editor.decorations.clear()
    cursor = helper.word_under_cursor(select_whole_word=True)
    deco = TextDecoration(cursor)
    deco.set_as_bold()
    deco.set_as_underlined(QtGui.QColor("#FF0000"))
    editor.decorations.append(deco)
    assert not editor.decorations.append(deco)
    editor.decorations.clear()
    assert editor.decorations.append(deco)
    assert editor.decorations.remove(deco)


@editor_open(__file__)
def test_constructors(editor):
    deco = TextDecoration(editor.textCursor(),
                                   start_pos=10, end_pos=15)
    deco = TextDecoration(editor.textCursor(),
                                   start_line=10, end_line=15)


@editor_open(__file__)
def test_formats(editor):
    deco = TextDecoration(editor.textCursor(),
                                   start_line=10, end_line=15)
    deco.set_foreground(QtGui.QColor('#FF0000'))
    deco.set_outline(QtGui.QColor('#FF0000'))
    deco.set_as_spell_check(QtGui.QColor('#FF0000'))
    deco.set_as_error(QtGui.QColor('#FF0000'))
    deco.set_as_error()
    deco.set_as_warning()
