from PyQt5.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes
from test.helpers import editor_open


def get_mode(editor):
    return frontend.get_mode(editor, modes.PygmentsSyntaxHighlighter)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@editor_open(__file__)
def test_lexer_from_filename_tmp_file(editor):
    mode = get_mode(editor)
    mode.set_lexer_from_filename("file.py~")


@editor_open(__file__)
def test_apply_all_pygments_styles(editor):
    mode = get_mode(editor)
    for style in modes.PYGMENTS_STYLES:
        mode.pygments_style = style
        assert mode.pygments_style == style
        QTest.qWait(500)
