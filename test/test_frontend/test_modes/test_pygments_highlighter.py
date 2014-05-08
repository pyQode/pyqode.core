from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


editor = None
mode = None


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    editor.setMinimumWidth(800)
    editor.setMinimumWidth(600)
    mode = modes.PygmentsSyntaxHighlighter(editor.document())
    frontend.install_mode(editor, mode)
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def teardown_module():
    global editor
    del editor


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_lexer_from_filename_tmp_file():
    mode.set_lexer_from_filename("file.py~")


def test_apply_all_pygments_styles():
    for style in modes.PYGMENTS_STYLES:
        mode.pygments_style = style
        assert mode.pygments_style == style
