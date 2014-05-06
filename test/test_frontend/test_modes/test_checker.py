import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest

from pyqode.core import frontend
from pyqode.core.frontend import modes, panels


editor = None
mode = None

from ...helpers import cwd_at


@cwd_at('test')
def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    mode = modes.CheckerMode(check, delay=1, show_tooltip=True)
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)


def teardown_module():
    global editor
    frontend.stop_server(editor)
    del editor


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_checker_message():
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.INFO) == 'Info'
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.WARNING) == 'Warning'
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.ERROR) == 'Error'

    msg = modes.CheckerMessage('desc', modes.CheckerMessages.ERROR,
                               10, col=15, path=__file__)
    assert msg.status_string == 'Error'


@cwd_at('test')
def test_request_analysis():
    mode.clear_messages()
    mode.request_analysis()
    frontend.start_server(editor, os.path.abspath('server.py'))
    QTest.qWait(2000)
    mode.request_analysis()
    QTest.qWait(2000)
    frontend.install_panel(editor, panels.MarkerPanel())
    mode.request_analysis()
    QTest.qWait(2000)
    mode.clear_messages()
    mode.request_analysis()
    QTest.qWait(2000)
    frontend.uninstall_panel(editor, panels.MarkerPanel)
    mode.clear_messages()


i = 0


def check(data):
    global i
    if i == 0:
        i += 1
        return False, None
    elif i == 1:
        i += 1
        return True, [('desc', 0, 10)]
    else:
        return True, [('desc', i % 3, 10 + i) for i in range(40)]
