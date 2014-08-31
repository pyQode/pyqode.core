import os
from pyqode.qt import QtCore
from pyqode.qt import QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import modes


def test_enabled(editor):
    mode = editor.modes.get(modes.ZoomMode)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_events(editor):
    zoom = editor.zoom_level
    QTest.keyPress(editor, '+', QtCore.Qt.ControlModifier)
    assert editor.zoom_level > zoom
    QTest.keyPress(editor, '0', QtCore.Qt.ControlModifier)
    assert editor.zoom_level == zoom == 0
    QTest.keyPress(editor, '-', QtCore.Qt.ControlModifier)
    assert editor.zoom_level < zoom
    if os.environ['QT_API'].lower() == 'pyqt5':
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), editor.mapToGlobal(QtCore.QPoint(10, 10)),
            QtCore.QPoint(0, 1), QtCore.QPoint(0, 1), 1,
            QtCore.Qt.Vertical, QtCore.Qt.MidButton, QtCore.Qt.ControlModifier))
    else:
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), 1,
            QtCore.Qt.MidButton, QtCore.Qt.ControlModifier))
    if os.environ['QT_API'].lower() == 'pyqt5':
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), editor.mapToGlobal(QtCore.QPoint(10, 10)),
            QtCore.QPoint(0, -1), QtCore.QPoint(0, -1), -1,
             QtCore.Qt.Vertical, QtCore.Qt.MidButton, QtCore.Qt.ControlModifier))
    else:
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), -1,
            QtCore.Qt.MidButton, QtCore.Qt.ControlModifier))
