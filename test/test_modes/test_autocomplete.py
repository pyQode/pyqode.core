from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper, CodeEdit
from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.AutoCompleteMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_pressed():
    # " -> ""
    editor = CodeEdit()
    editor.modes.append(modes.AutoCompleteMode())
    editor.setPlainText('', '', 'utf-8')
    QTest.keyPress(editor, '"')
    assert editor.toPlainText() == '""'
    editor.clear()

    # if a " already exists, cursor should just move after " and a new " should
    # not be inserted
    editor.setPlainText('"', 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(0, 0)
    QTest.keyPress(editor, '"')
    assert editor.toPlainText() == '"'
    editor.clear()

    # if a ) already exists, cursor should just move after ) and a new ) should
    # not be inserted
    editor.setPlainText(')', 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(0, 0)
    QTest.keyPress(editor, ')')
    QTest.qWait(1000)
    assert editor.toPlainText() == ')'

    # ] should be inserted ")" -> "])"
    TextHelper(editor).goto_line(0, 0)
    QTest.keyPress(editor, ']')
    QTest.qWait(1000)
    assert editor.toPlainText() == '])'


def test_quoting_selection(editor):
    editor.setPlainText('foo', '', 'utf-8')
    TextHelper(editor).goto_line(0, 0)
    editor.selectAll()
    QTest.keyPress(editor, '(')
    assert editor.toPlainText() == '(foo)'
