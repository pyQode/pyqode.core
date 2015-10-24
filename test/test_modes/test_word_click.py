import os
from pyqode.core.api import TextHelper
from pyqode.qt import QtCore, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.WordClickMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_events(editor):
    mode = get_mode(editor)
    mode._add_decoration(editor.textCursor())
    pt = QtCore.QPoint(10, TextHelper(editor).line_pos_from_number(0))
    if os.environ['QT_API'] == 'pyqt5':
        QTest.mouseMove(editor, pt)
        QTest.mousePress(editor, QtCore.Qt.LeftButton,
                         QtCore.Qt.ControlModifier, pt)
        QTest.mouseMove(editor, pt)
    else:
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
