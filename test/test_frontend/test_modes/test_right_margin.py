from pyqode.core import frontend, style
from pyqode.core.frontend import modes
from PyQt5 import QtGui


def get_mode(editor):
    return frontend.get_mode(editor, modes.RightMarginMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_position(editor):
    mode = get_mode(editor)
    assert mode.position == 79
    mode.position = 119
    assert mode.position == 119


def test_color(editor):
    mode = get_mode(editor)
    assert mode.color.name() == style.right_margin_color.name()
    mode.color = QtGui.QColor('#00FF00')
    assert mode.color.name() == QtGui.QColor('#00FF00').name()
