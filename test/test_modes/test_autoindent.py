from pyqode.qt import QtCore
from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper
from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.AutoIndentMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_indent_eat_whitespaces(editor):
    editor.setPlainText('app = get_app(45, 4)', 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(0, 17)
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
