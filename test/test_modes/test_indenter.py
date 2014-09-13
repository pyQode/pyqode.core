from pyqode.qt.QtTest import QTest
from pyqode.core import api
from pyqode.core import modes
from pyqode.core.api import TextHelper


def test_enabled(editor):
    mode = editor.modes.get(modes.IndenterMode)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_indent_selection(editor):
    mode = editor.modes.get(modes.IndenterMode)
    # select all
    TextHelper(editor).select_lines()
    mode.indent()
    mode.unindent()
    TextHelper(editor).select_lines(0)
    mode.indent()
    mode.unindent()
    editor.use_spaces_instead_of_tabs = False
    TextHelper(editor).select_lines()
    mode.indent()
    mode.unindent()


def test_bug_unindent(editor):
    mode = editor.modes.get(modes.IndenterMode)
    editor.use_spaces_instead_of_tabs = True
    editor.setPlainText('    print("foo")', 'text/x-python', 'utf-8')
    api.TextHelper(editor).goto_line(0, column=len('    print("foo")'))
    mode.unindent()
    assert editor.toPlainText() == 'print("foo")'
