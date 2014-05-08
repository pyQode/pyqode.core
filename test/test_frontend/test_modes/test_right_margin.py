from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend, style
from pyqode.core.frontend import modes


editor = None
mode = None


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    mode = modes.RightMarginMode()
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def teardown_module():
    global editor
    del editor


def teardown_module():
    global editor
    frontend.stop_server(editor)
    del editor


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_position():
    assert mode.position == 79
    mode.position = 119
    assert mode.position == 119


def test_color():
    assert mode.color.name() == style.right_margin_color.name()
    mode.color = QtGui.QColor('#00FF00')
    assert mode.color.name() == QtGui.QColor('#00FF00').name()
