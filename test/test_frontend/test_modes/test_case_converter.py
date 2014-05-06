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
    mode = modes.CaseConverterMode()
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


def test_slots():
    mode.to_upper()
    mode.to_lower()
