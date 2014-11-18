import pytest
from pyqode.qt import QtGui
from pyqode.qt.QtTest import QTest

from pyqode.core.api import TextHelper
from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.OccurrencesHighlighterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_delay(editor):
    mode = get_mode(editor)
    assert mode.delay == 1000
    mode.delay = 3000
    assert mode.delay == 3000
    mode.delay = 1000
    assert mode.delay == 1000


def test_background(editor):
    mode = get_mode(editor)
    assert mode.background.name() == '#80cc80'
    mode.background = QtGui.QColor('#404040')
    assert mode.background.name() == '#404040'


def test_foreground(editor):
    mode = get_mode(editor)
    assert mode.foreground.name() == '#404040'
    mode.foreground = QtGui.QColor('#202020')
    assert mode.foreground.name() == '#202020'


@pytest.mark.parametrize('underlined', [True, False])
def test_occurrences(editor, underlined):
    editor.file.open(__file__)
    mode = get_mode(editor)
    mode.underlined = underlined
    assert len(mode._decorations) == 0
    assert mode.delay == 1000
    TextHelper(editor).goto_line(16, 7)
    QTest.qWait(2000)
    assert len(mode._decorations) == 23
