import random
from pyqode.qt.QtTest import QTest
import sys
import pytest
from pyqode.core import modes, panels

from ..helpers import wait_for_connected, editor_open
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
def test_add_messages(editor):
    mode = get_mode(editor)
    mode.clear_messages()
    status = [modes.CheckerMessages.ERROR, modes.CheckerMessages.WARNING,
              modes.CheckerMessages.INFO]
    mode.add_messages([modes.CheckerMessage('desc', random.choice(status),
                                            10 + i)
                       for i in range(500)])
    assert len(mode._messages) < 500
    QTest.qWait(500)


@editor_open(__file__)
def test_remove_message(editor):
    mode = get_mode(editor)
    QTest.qWait(5000)
    mode.clear_messages()
    status = [modes.CheckerMessages.ERROR, modes.CheckerMessages.WARNING,
              modes.CheckerMessages.INFO]
    mode.add_messages([modes.CheckerMessage('desc', modes.CheckerMessages.ERROR,
                                            10 + i)
                       for i in range(mode.limit * 2)])
    while not mode._finished:
        QTest.qWait(5000)
    assert len(mode._messages) == mode.limit
    QTest.qWait(5000)
    mode.remove_message(mode._messages[10])
    QTest.qWait(5000)
    assert len(mode._messages) == mode.limit - 1
    mode.clear_messages()


@editor_open(__file__)
def test_work_finished(editor):
    mode = get_mode(editor)
    mode._on_work_finished([])
    mode._on_work_finished([('desc', i % 3, 10 + i) for i in range(40)])


i = 0


def check(data):
    global i
    print('CHECKER FUNCTION: i = %d' % i)
    if i == 0:
        i += 1
        return []
    elif i == 1:
        i += 1
        return [('desc', 0, 10)]
    elif i == 2:
        i += 1
        return [('desc', i % 3, 10 + i) for i in range(150)]
    else:
        return [('desc', i % 3, 10 + i) for i in range(20)]
