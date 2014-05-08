from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend, settings
from pyqode.core.frontend import modes


editor = None
mode = modes.IndenterMode()


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    editor.setMinimumWidth(800)
    editor.setMinimumWidth(600)
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_indent_selection():
    # select all
    frontend.select_lines(editor)
    mode.indent()
    mode.unindent()
    frontend.select_lines(editor, 1)
    mode.indent()
    mode.unindent()
    settings.use_spaces_instead_of_tabs = False
    frontend.select_lines(editor)
    mode.indent()
    mode.unindent()
