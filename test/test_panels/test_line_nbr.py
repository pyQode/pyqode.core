from pyqode.core.api import TextHelper
from pyqode.qt import QtCore, QtWidgets, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import panels
from test.helpers import editor_open


def get_panel(editor):
    return editor.panels.get(panels.LineNumberPanel)


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


@editor_open(__file__)
def test_mouse_press(editor):
    panel = get_panel(editor)
    y_pos = TextHelper(editor).line_pos_from_number(0)
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(1000, 1000))
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(3, y_pos))


@editor_open(__file__)
def test_mouse_release(editor):
    panel = get_panel(editor)
    y_pos = TextHelper(editor).line_pos_from_number(0)
    QTest.mouseRelease(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                       QtCore.QPoint(3, y_pos))


@editor_open(__file__)
def test_mouse_move(editor):
    panel = get_panel(editor)
    y_pos = TextHelper(editor).line_pos_from_number(0)
    panel._selecting = True
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos))
    QTest.qWait(1000)
    QTest.mouseMove(panel, QtCore.QPoint(1000, 1000))
    panel.mouseMoveEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseMove, QtCore.QPoint(10, 10),
        QtCore.Qt.RightButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))


@editor_open(__file__)
def test_leave_event(editor):
    panel = get_panel(editor)
    panel.leaveEvent(None)
