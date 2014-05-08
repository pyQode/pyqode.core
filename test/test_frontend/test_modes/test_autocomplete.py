from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


editor = None
mode = modes.AutoCompleteMode()


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    editor.setMinimumWidth(800)
    editor.setMinimumWidth(600)
    frontend.install_mode(editor, mode)
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


def test_key_pressed():
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText('"', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 0)
    QTest.keyPress(editor, '"')
    editor.clear()
    editor.setPlainText(')', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 0)
    QTest.keyPress(editor, ')')
