from pyqode.qt import QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import modes
from test.helpers import preserve_style, editor_open


def get_mode(editor):
    return editor.modes.get(modes.CaretLineHighlighterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_properties(editor):
    mode = get_mode(editor)
    assert isinstance(mode.background, QtGui.QColor)
    c = QtGui.QColor('red')
    mode.background = c
    assert mode.background.name() == c.name()


def test_style(editor):
    mode = get_mode(editor)
    c = QtGui.QColor('yellow')
    mode.background = c
    QTest.qWait(1000)
    assert mode.background.name() == c.name()


@editor_open(__file__)
def test_deco(editor):
    assert len(editor.decorations) > 0
