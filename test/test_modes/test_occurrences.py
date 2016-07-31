import pytest
from pyqode.qt import QtGui
from pyqode.qt.QtTest import QTest

from pyqode.core.api import TextHelper
from pyqode.core import modes

from ..helpers import ensure_visible, ensure_connected


def get_mode(editor):
    return editor.modes.get(modes.OccurrencesHighlighterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@ensure_connected
@ensure_visible
def test_delay(editor):
    mode = get_mode(editor)
    assert mode.delay == 1000
    mode.delay = 3000
    assert mode.delay == 3000
    mode.delay = 1000
    assert mode.delay == 1000


@ensure_connected
@ensure_visible
def test_background(editor):
    mode = get_mode(editor)
    assert mode.background.name() == '#ccffcc'
    mode.background = QtGui.QColor('#404040')
    assert mode.background.name() == '#404040'


@ensure_connected
@ensure_visible
def test_foreground(editor):
    mode = get_mode(editor)
    assert mode.foreground is None
    mode.foreground = QtGui.QColor('#202020')
    assert mode.foreground.name() == '#202020'


@ensure_connected
@ensure_visible
@pytest.mark.xfail
def test_occurrences(editor):
    for underlined in [True, False]:
        editor.file.open(__file__)
        assert editor.backend.running is True
        mode = get_mode(editor)
        mode.underlined = underlined
        assert len(mode._decorations) == 0
        assert mode.delay == 1000
        TextHelper(editor).goto_line(16, 7)
        QTest.qWait(2000)
        assert len(mode._decorations) > 0
