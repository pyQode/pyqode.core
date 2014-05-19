import os
from pyqode.qt import QtCore
from pyqode.qt import QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


def test_enabled(editor):
    mode = frontend.get_mode(editor, modes.ZoomMode)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_events(editor):
    zoom = editor.font_size
    QTest.keyPress(editor, '+', QtCore.Qt.ControlModifier)
    assert editor.font_size > zoom
    QTest.keyPress(editor, '0', QtCore.Qt.ControlModifier)
    assert editor.font_size == zoom
    QTest.keyPress(editor, '-', QtCore.Qt.ControlModifier)
    assert editor.font_size < zoom
    if os.environ['QT_API'].lower() == 'PyQt5':
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), editor.mapToGlobal(QtCore.QPoint(10, 10)),
            QtCore.QPoint(0, 1), QtCore.QPoint(0, 1), 1,
            QtCore.Qt.Vertical, QtCore.Qt.MidButton, QtCore.Qt.NoModifier))
    else:
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), 1,
            QtCore.Qt.MidButton, QtCore.Qt.NoModifier))
    if os.environ['QT_API'].lower() == 'PyQt5':
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), editor.mapToGlobal(QtCore.QPoint(10, 10)),
            QtCore.QPoint(0, -1), QtCore.QPoint(0, -1), -1,
            QtCore.Qt.MidButton, QtCore.Qt.NoModifier))
    else:
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), -1,
            QtCore.Qt.MidButton, QtCore.Qt.NoModifier))
