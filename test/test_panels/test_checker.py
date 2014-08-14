from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.api import TextHelper
from pyqode.qt import QtCore
from pyqode.qt.QtTest import QTest
from test.helpers import editor_open


def get_panel(editor):
    return editor.panels.get(panels.CheckerPanel)


def get_mode(editor):
    try:
        mode = editor.modes.get(modes.CheckerMode)
    except KeyError:
        mode = modes.CheckerMode(check)
        editor.modes.append(mode)
    return mode


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


def check(data):
    return True, [('desc', i % 3, i + 1) for i in range(20)]
