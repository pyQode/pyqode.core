from pyqode.qt import QtCore, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper
from pyqode.core import modes
from test.helpers import editor_open


def get_mode(editor):
    return editor.modes.get(modes.ExtendedSelectionMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@editor_open(__file__)
def test_extended_selection(editor):
    QTest.qWait(1000)
    mode = get_mode(editor)
    TextHelper(editor).goto_line(0, 10)
    QTest.qWait(1000)
    try:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPointF(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton,
                                  QtCore.Qt.ControlModifier)
    except TypeError:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPoint(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton,
                                  QtCore.Qt.ControlModifier)
    mode._on_double_click(event)
    assert editor.textCursor().selectedText() == 'pyqode.qt'
    QTest.qWait(1000)


@editor_open(__file__)
def test_matched_selection(editor):
    QTest.qWait(1000)
    mode = get_mode(editor)
    TextHelper(editor).goto_line(8, 29)
    QTest.qWait(1000)
    try:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPointF(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton,
                                  QtCore.Qt.AltModifier)
    except TypeError:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPoint(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton,
                                  QtCore.Qt.AltModifier)
    mode._on_double_click(event)
    assert editor.textCursor().selectedText() == 'modes.ExtendedSelectionMode'
    QTest.qWait(1000)


@editor_open(__file__)
def test_word_selection(editor):
    QTest.qWait(1000)
    mode = get_mode(editor)
    TextHelper(editor).goto_line(8, 29)
    QTest.qWait(1000)
    try:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPointF(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
    except TypeError:
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick,
                                  QtCore.QPoint(0, 0), QtCore.Qt.LeftButton,
                                  QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
    mode._on_double_click(event)
    assert editor.textCursor().selectedText() == 'modes'
    QTest.qWait(1000)


@editor_open(__file__)
def test_line_selection(editor):
    QTest.qWait(1000)
    mode = get_mode(editor)
    TextHelper(editor).goto_line(0, 2)
    QTest.qWait(1000)
    mode.perform_line_selection()
    assert editor.textCursor().selectedText() == 'from pyqode.qt import QtCore, QtGui'
    QTest.qWait(1000)
