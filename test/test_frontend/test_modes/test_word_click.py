from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest

from pyqode.core import frontend
from pyqode.core.frontend import modes


def get_mode(editor):
    return frontend.get_mode(editor, modes.WordClickMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_events(editor):
    mode = get_mode(editor)
    mode._add_decoration(editor.textCursor())
    pt = QtCore.QPoint(10, frontend.line_pos_from_number(editor, 1))
    QTest.mouseMove(editor, pt)
    editor.mouseMoveEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseMove, pt,
        QtCore.Qt.RightButton, QtCore.Qt.RightButton,
        QtCore.Qt.ControlModifier))
    # here we have a deco, try to click on it.
    editor.mousePressEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseButtonPress, pt,
        QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
    # move window without control -> remove deco
    editor.mouseMoveEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseMove, pt,
        QtCore.Qt.RightButton, QtCore.Qt.RightButton,
        QtCore.Qt.NoModifier))
