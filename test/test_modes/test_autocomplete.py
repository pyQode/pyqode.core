from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper
from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.AutoCompleteMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_pressed(editor):
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText('"', 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(1, 0)
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText(')', 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(1, 0)
    QTest.keyPress(editor, ')')
