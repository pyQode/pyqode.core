from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


editor = None
mode = None


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    mode = modes.ZoomMode()
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def teardown_module():
    global editor
    frontend.stop_server(editor)
    del editor


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_key_events():
    global editor
    zoom = editor.font_size
    QTest.keyPress(editor, '+', QtCore.Qt.ControlModifier)
    assert editor.font_size > zoom
    QTest.keyPress(editor, '0', QtCore.Qt.ControlModifier)
    assert editor.font_size == zoom
    QTest.keyPress(editor, '-', QtCore.Qt.ControlModifier)
    assert editor.font_size < zoom
    editor.wheelEvent(QtGui.QWheelEvent(
        QtCore.QPoint(10, 10), 1, QtCore.Qt.MidButton,
        QtCore.Qt.ControlModifier))
    editor.wheelEvent(QtGui.QWheelEvent(
        QtCore.QPoint(10, 10), -1, QtCore.Qt.MidButton,
        QtCore.Qt.ControlModifier))