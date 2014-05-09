from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core import style
from test.helpers import preserve_style, editor_open


def get_mode(editor):
    return frontend.get_mode(editor, modes.CaretLineHighlighterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@preserve_style
def test_properties(editor):
    mode = get_mode(editor)
    assert isinstance(mode.background, QtGui.QColor)
    c = QtGui.QColor('red')
    mode.background = c
    assert mode.background.name() == c.name()


@preserve_style
def test_style(editor):
    mode = get_mode(editor)
    c = QtGui.QColor('yellow')
    style.caret_line_background = c
    editor.refresh_style()
    QTest.qWait(1000)
    assert mode.background.name() == c.name()
