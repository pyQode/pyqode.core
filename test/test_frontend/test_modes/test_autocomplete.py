from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


def get_mode(editor):
    return frontend.get_mode(editor, modes.AutoCompleteMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_pressed(editor):
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText('"', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 0)
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText(')', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 0)
    QTest.keyPress(editor, ')')
