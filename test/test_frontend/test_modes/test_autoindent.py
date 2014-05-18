from PyQt5 import QtCore
from PyQt5.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


def get_mode(editor):
    return frontend.get_mode(editor, modes.AutoIndentMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_indent_eat_whitespaces(editor):
    editor.setPlainText('app = get_app(45, 4)', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 17)
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
