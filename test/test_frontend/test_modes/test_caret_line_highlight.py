from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core import style


editor = None
mode = modes.CaretLineHighlighterMode()


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def teardown_module():
    global editor
    del editor


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_properties():
    assert isinstance(mode.background, QtGui.QColor)
    c = QtGui.QColor('red')
    mode.background = c
    assert mode.background.name() == c.name()


def test_style():
    c = QtGui.QColor('yellow')
    style.caret_line_background = c
    editor.refresh_style()
    assert mode.background.name() == c.name()
