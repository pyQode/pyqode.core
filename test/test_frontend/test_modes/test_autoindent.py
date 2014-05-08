from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core import style


editor = None
mode = modes.AutoIndentMode()


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
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


def test_indent_eat_whitespaces():
    editor.setPlainText('app = get_app(45, 4)', 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 17)
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
