# -*- coding: utf-8 -*-
"""
A helper module for testing, introducing some helper functions. Inspired by
the jedi helper module for their testing package
"""
import os
import functools
import platform
from os.path import abspath
from os.path import dirname
from pyqode.core.cache import Cache
from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit, IndentFoldDetector, ColorScheme
from pyqode.core import modes
from pyqode.core import panels
from pyqode.qt.QtTest import QTest


test_dir = dirname(abspath(__file__))


# -------------------
# Decorators
# -------------------
def cwd_at(path):
    """
    Decorator to run function at `path`.

    :type path: str
    :arg path: relative path from repository root (e.g., 'pyqode' or 'test').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                oldcwd = os.getcwd()
                repo_root = os.path.dirname(test_dir)
                os.chdir(os.path.join(repo_root, path))
                return func(*args, **kwds)
            finally:
                os.chdir(oldcwd)
        return wrapper
    return decorator


def delete_file_on_return(path):
    """
    Decorator to run function at `path`.

    :type path: str
    :arg path: relative path from repository root (e.g., 'pyqode' or 'test').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            finally:
                try:
                    os.remove(path)
                except (IOError, OSError):
                    pass
        return wrapper
    return decorator


def editor_open(path):
    if not os.path.exists(path):
        try:
            with open(path, 'w') as dst:
                with open(__file__, 'r') as src:
                    dst.write(src.read())
        except OSError:
            pass

    def decorator(func):
        @functools.wraps(func)
        def wrapper(editor, *args, **kwds):
            editor.file.open(path)
            QTest.qWait(100)
            return func(editor, *args, **kwds)
        return wrapper
    return decorator


def preserve_settings(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        editor.save_on_focus_out = False
        editor.modes.get(modes.FileWatcherMode).auto_reload = False
        try:
            ret = func(editor, *args, **kwds)
        finally:
            assert isinstance(editor, CodeEdit)
            editor.save_on_focus_out = False
            editor.modes.get(modes.FileWatcherMode).auto_reload = False
        return ret
    return wrapper


def preserve_style(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        try:
            ret = func(editor, *args, **kwds)
        finally:
            editor.font_name = 'Source Code Pro'
            editor.font_size = 10
            editor.reset_zoom()
        return ret
    return wrapper


def reset_editor(editor):
    assert isinstance(editor, CodeEdit)
    Cache().clear()
    editor.modes.clear()
    editor.panels.clear()
    setup_editor(editor)
    editor.font_name = CodeEdit._DEFAULT_FONT
    editor.font_size = 10
    editor.use_spaces_instead_of_tabs = True
    editor.tab_length = 4
    editor.save_on_focus_out = False
    pal = QtWidgets.QApplication.instance().palette()
    editor.selection_background = pal.highlight().color()
    editor.selection_foreground = pal.highlightedText().color()
    editor.syntax_highlighter.color_scheme = ColorScheme('qt')
    editor.zoom_level = 0
    editor.resize(800, 600)
    editor.backend.stop()
    assert not editor.backend.running
    editor.backend.start(server_path())
    wait_for_connected(editor)
    assert editor.backend.running

# -------------------
# Helper functions
# -------------------
def wait_for_connected(editor):
    while not editor.backend.running:
        QTest.qWait(100)


def python2_path():
    """
    Returns the path to the python2 interpreter.

    The expected python2 path is '/usr/bin/python' on Linux and
    'c:\Python27\python.exe' on Windows.
    """
    return '/usr/bin/python' if platform.system() == 'Linux' else \
        'c:\\Python27\\python.exe'


def server_path():
    return os.path.join(os.path.dirname(__file__), 'server.py')


def setup_editor(code_edit):
        # append panels
    p = panels.FoldingPanel(highlight_caret_scope=True)
    code_edit.panels.append(p)
    p.show()
    p = panels.LineNumberPanel()
    code_edit.panels.append(p)
    p.show()
    p = panels.MarkerPanel()
    code_edit.panels.append(p)
    p.show()
    p = panels.CheckerPanel()
    code_edit.panels.append(p)
    p.show()
    p = panels.SearchAndReplacePanel()
    code_edit.panels.append(p, p.Position.BOTTOM)
    p.show()
    p = panels.GlobalCheckerPanel()
    code_edit.panels.append(p, p.Position.RIGHT)
    p.show()

    # append modes
    code_edit.modes.append(modes.AutoCompleteMode())
    code_edit.modes.append(modes.CaseConverterMode())
    code_edit.modes.append(modes.FileWatcherMode())
    code_edit.modes.append(modes.CaretLineHighlighterMode())
    code_edit.modes.append(modes.RightMarginMode())
    code_edit.modes.append(modes.PygmentsSyntaxHighlighter(
        code_edit.document()))
    code_edit.modes.append(modes.ZoomMode())
    code_edit.modes.append(modes.CodeCompletionMode())
    code_edit.modes.append(modes.AutoIndentMode())
    code_edit.modes.append(modes.IndenterMode())
    code_edit.modes.append(modes.SymbolMatcherMode())
    code_edit.modes.append(modes.WordClickMode())
    code_edit.modes.get(modes.FileWatcherMode).auto_reload = True
    code_edit.syntax_highlighter.fold_detector = IndentFoldDetector()
    code_edit.modes.append(modes.SmartBackSpaceMode())
    code_edit.modes.append(modes.ExtendedSelectionMode())
    code_edit.modes.append(modes.OccurrencesHighlighterMode())


def ensure_visible(func):
    """
    Ensures the frontend is connect is connected to the server. If that is not
    the case, the code completion server is started automatically
    """
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        QtWidgets.QApplication.setActiveWindow(editor)
        editor.show()
        editor.raise_()
        editor.setFocus()
        editor.setReadOnly(False)
        return func(editor, *args, **kwds)
    return wrapper


def ensure_connected(func):
    """
    Ensures the frontend is connect is connected to the server. If that is not
    the case, the code completion server is started automatically
    """
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        if not editor.backend.running:
            editor.backend.start(server_path())
            wait_for_connected(editor)
        return func(editor, *args, **kwds)
    return wrapper
