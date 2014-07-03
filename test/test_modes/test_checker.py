import random
from pyqode.core.qt.QtTest import QTest
from pyqode.core import modes, panels

from ..helpers import preserve_editor_config, wait_for_connected, editor_open
from ..helpers import server_path


def get_mode(editor):
    try:
        mode = editor.modes.get(modes.CheckerMode)
    except KeyError:
        mode = modes.CheckerMode(check)
        editor.modes.append(mode)
    return mode


def test_enabled(editor):
    mode = get_mode(editor)
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


@editor_open(__file__)
@preserve_editor_config
def test_request_analysis(editor):
    try:
        mode = get_mode(editor)
    except KeyError:
        mode = modes.CheckerMode(check)
        editor.modes.append(mode)
    editor.backend.stop()
    mode.clear_messages()
    if editor.backend.connected:
        editor.backend.stop()
    mode.request_analysis()
    QTest.qWait(500)
    editor.backend.start(server_path())
    wait_for_connected(editor)
    mode.request_analysis()
    QTest.qWait(3000)
    editor.panels.append(panels.MarkerPanel())
    mode.request_analysis()
    QTest.qWait(3000)
    mode.clear_messages()
    mode.request_analysis()
    QTest.qWait(3000)
    editor.panels.remove(panels.MarkerPanel)
    mode.clear_messages()


@editor_open(__file__)
@preserve_editor_config
def test_add_messages(editor):
    mode = get_mode(editor)
    mode.clear_messages()
    status = [modes.CheckerMessages.ERROR, modes.CheckerMessages.WARNING,
              modes.CheckerMessages.INFO]
    mode.add_messages([modes.CheckerMessage('desc', random.choice(status),
                                            10 + i)
                       for i in range(40)])
    assert len(mode._messages) == 20
    QTest.qWait(500)


@editor_open(__file__)
@preserve_editor_config
def test_remove_message(editor):
    mode = get_mode(editor)
    status = [modes.CheckerMessages.ERROR, modes.CheckerMessages.WARNING,
              modes.CheckerMessages.INFO]
    mode.add_messages([modes.CheckerMessage('desc', random.choice(status),
                                            10 + i)
                       for i in range(40)])
    assert len(mode._messages) == 20
    QTest.qWait(500)
    mode.remove_message(mode._messages[10])
    QTest.qWait(500)
    assert len(mode._messages) == 19
    mode.clear_messages()


@editor_open(__file__)
@preserve_editor_config
def test_work_finished(editor):
    mode = get_mode(editor)
    mode._on_work_finished(False, [])
    mode._on_work_finished(False, [('desc', i % 3, 10 + i) for i in range(40)])


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
