from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.api import TextHelper
from pyqode.core.qt import QtCore
from pyqode.core.qt.QtTest import QTest
from test.helpers import editor_open


def get_panel(editor):
    return editor.panels.get(panels.CheckerPanel)


def get_mode(editor):
    try:
        mode = editor.modes.get(modes.CheckerMode)
    except KeyError:
        mode = modes.CheckerMode(check)
        editor.modes.append(mode)
    return mode


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


@editor_open(__file__)
def test_mouse_press(editor):
    mode = get_mode(editor)
    mode.request_analysis()
    QTest.qWait(2000)
    panel = get_panel(editor)
    y_pos = TextHelper(editor).line_pos_from_number(1)
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(1000, 1000))
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(3, y_pos))
    mode.clear_messages()


@editor_open(__file__)
def test_mouse_move(editor):
    mode = get_mode(editor)
    mode.request_analysis()
    QTest.qWait(2000)
    panel = get_panel(editor)
    y_pos = TextHelper(editor).line_pos_from_number(1)
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos))
    QTest.qWait(1000)
    QTest.mouseMove(panel, QtCore.QPoint(1000, 1000))
    mode.clear_messages()


def check(data):
    return True, [('desc', i % 3, i + 1) for i in range(20)]
