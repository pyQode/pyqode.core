from pyqode.core import frontend
from pyqode.core.frontend import modes


def test_enabled(editor):
    mode = frontend.get_mode(editor, modes.IndenterMode)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_indent_selection(editor):
    mode = frontend.get_mode(editor, modes.IndenterMode)
    # select all
    frontend.select_lines(editor)
    mode.indent()
    mode.unindent()
    frontend.select_lines(editor, 1)
    mode.indent()
    mode.unindent()
    editor.use_spaces_instead_of_tabs = False
    frontend.select_lines(editor)
    mode.indent()
    mode.unindent()
