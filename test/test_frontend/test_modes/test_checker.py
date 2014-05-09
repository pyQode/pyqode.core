from PyQt4.QtTest import QTest

from pyqode.core import frontend
from pyqode.core.frontend import modes, panels

from ...helpers import preserve_editor_config
from ...helpers import server_path


def get_mode(editor):
    return frontend.get_mode(editor, modes.CheckerMode)


def test_enabled(editor):
    try:
        mode = get_mode(editor)
    except KeyError:
        mode = modes.CheckerMode(check)
        frontend.install_mode(editor, mode)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_checker_message(editor):
    try:
        mode = get_mode(editor)
    except KeyError:
        mode = modes.CheckerMode(check)
        frontend.install_mode(editor, mode)
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.INFO) == 'Info'
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.WARNING) == 'Warning'
    assert modes.CheckerMessage.status_to_string(
        modes.CheckerMessages.ERROR) == 'Error'

    msg = modes.CheckerMessage('desc', modes.CheckerMessages.ERROR,
                               10, col=15, path=__file__)
    assert msg.status_string == 'Error'


@preserve_editor_config
def test_request_analysis(editor):
    try:
        mode = get_mode(editor)
    except KeyError:
        mode = modes.CheckerMode(check)
        frontend.install_mode(editor, mode)
    frontend.stop_server(editor)
    mode.clear_messages()
    mode.request_analysis()
    frontend.start_server(editor, server_path())
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
