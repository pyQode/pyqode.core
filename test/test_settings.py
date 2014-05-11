# -*- coding: utf-8 -*-
"""
Test scripts for the settings module.
"""
from PyQt4 import QtCore
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core import settings
from pyqode.core.frontend import modes
from test.helpers import log_test_name
from test.helpers import preserve_settings


@preserve_settings
@log_test_name
def test_show_white_spaces(editor):
    assert settings.show_white_spaces is False
    assert editor.show_whitespaces is False
    # change settings
    settings.show_white_spaces = True
    assert settings.show_white_spaces is True
    # new editors will have the new settings
    new_editor = frontend.CodeEdit()
    assert new_editor.show_whitespaces is True
    # existing editor didn't changed
    assert editor.show_whitespaces is False
    # refresh changes
    editor.refresh_settings()
    # changes should have been applied
    assert editor.show_whitespaces is True
    # reset settings for next tests
    settings.show_white_spaces = False


@preserve_settings
@log_test_name
def test_tab_length(editor):
    assert settings.tab_length == 4
    QTest.keyPress(editor, QtCore.Qt.Key_Tab)
    assert editor.toPlainText() == 4 * ' '
    editor.clear()

    # change settings
    settings.tab_length = 8
    assert settings.tab_length == 8
    QTest.keyPress(editor, QtCore.Qt.Key_Tab)
    assert editor.toPlainText() == 8 * ' '

    # reset settings for next tests
    settings.tab_length = 4


@preserve_settings
@log_test_name
def test_use_spaces_instead_of_tabs(editor):
    editor.clear()
    assert settings.use_spaces_instead_of_tabs is True
    settings.tab_length = 4
    QTest.keyPress(editor, QtCore.Qt.Key_Tab)
    assert editor.toPlainText() == '    '
    # change settings
    settings.use_spaces_instead_of_tabs = False
    assert settings.use_spaces_instead_of_tabs is False
    QTest.keyPress(editor, QtCore.Qt.Key_Tab)
    assert editor.toPlainText() == '    \t'
    # reset settings for next tests
    settings.use_spaces_instead_of_tabs = True


@preserve_settings
@log_test_name
def test_min_indent_column(editor):
    editor.clear()
    assert settings.min_indent_column == 0
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
    assert editor.toPlainText() == '\n'
    assert editor.toPlainText() == '\n'
    # change settings
    settings.min_indent_column = 4
    assert settings.min_indent_column == 4
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
    assert editor.toPlainText() == '\n\n'
    editor.refresh_settings()
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
    assert editor.toPlainText() == '\n\n\n    '
    # reset settings for next tests
    settings.min_indent_column = 0


def get_completion_mode(editor):
    return frontend.get_mode(editor, modes.CodeCompletionMode)


@preserve_settings
@log_test_name
def test_cc_trigger_key(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.cc_trigger_key == ord(' ')
    assert isinstance(code_completion_mode, modes.CodeCompletionMode)
    assert code_completion_mode.trigger_key == ord(' ')
    settings.cc_trigger_key = ord('M')
    assert code_completion_mode.trigger_key == ord(' ')
    editor.refresh_settings()
    assert code_completion_mode.trigger_key == ord('M')
    # reset settings for next tests
    settings.cc_trigger_key = ord(' ')


@preserve_settings
@log_test_name
def test_cc_trigger_len(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.cc_trigger_len == 1
    assert isinstance(code_completion_mode, modes.CodeCompletionMode)
    assert code_completion_mode.trigger_length == 1
    settings.cc_trigger_len = 3
    assert code_completion_mode.trigger_length == 1
    editor.refresh_settings()
    assert code_completion_mode.trigger_length == 3
    # reset settings for next tests
    settings.cc_trigger_len = 1


@preserve_settings
@log_test_name
def test_cc_trigger_symbols(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.cc_trigger_symbols == ['.']
    assert isinstance(code_completion_mode, modes.CodeCompletionMode)
    assert code_completion_mode.trigger_symbols == ['.']
    settings.cc_trigger_symbols = ['.', '->']
    assert code_completion_mode.trigger_symbols == ['.']
    editor.refresh_settings()
    assert code_completion_mode.trigger_symbols == ['.', '->']
    # reset settings for next tests
    settings.cc_trigger_symbols = ['.']


@preserve_settings
@log_test_name
def test_cc_show_tooltips(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.cc_show_tooltips is True
    assert isinstance(code_completion_mode, modes.CodeCompletionMode)
    assert code_completion_mode.show_tooltips is True
    settings.cc_show_tooltips = False
    assert code_completion_mode.show_tooltips is True
    editor.refresh_settings()
    assert code_completion_mode.show_tooltips is False
    # reset settings for next tests
    settings.cc_show_tooltips = True


@preserve_settings
@log_test_name
def test_cc_case_sensitive(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.cc_case_sensitive is False
    assert isinstance(code_completion_mode, modes.CodeCompletionMode)
    assert code_completion_mode.case_sensitive is False
    settings.cc_case_sensitive = True
    assert code_completion_mode.case_sensitive is False
    editor.refresh_settings()
    assert code_completion_mode.case_sensitive is True
    # reset settings for next tests
    settings.cc_case_sensitive = False


@preserve_settings
@log_test_name
def test_file_watcher_auto_reload(editor):
    code_completion_mode = get_completion_mode(editor)
    assert settings.file_watcher_auto_reload is True
    fw = frontend.get_mode(editor, modes.FileWatcherMode)
    assert fw
    assert fw.auto_reload is True
    settings.file_watcher_auto_reload = False
    assert fw.auto_reload is True
    editor.refresh_settings()
    assert fw.auto_reload is False
    # reset settings for next tests
    settings.file_watcher_auto_reload = True


@preserve_settings
@log_test_name
def test_right_margin_pos(editor):
    assert settings.right_margin_pos == 79
    rm = frontend.get_mode(editor, modes.RightMarginMode)
    assert rm
    assert rm.position == 79
    settings.right_margin_pos = 120
    assert rm.position == 79
    editor.refresh_settings()
    assert rm.position == 120
    # reset settings for next tests
    settings.right_margin_pos = 79
