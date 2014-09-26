from pyqode.qt import QtCore
from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper
from pyqode.core import modes
from test.helpers import editor_open


def get_mode(editor):
    return editor.modes.get(modes.SmartBackSpaceMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@editor_open(__file__)
def test_key_pressed(editor):
    QTest.qWait(1000)
    TextHelper(editor).goto_line(21, 4)
    # QTest.qWait(2000)
    assert editor.textCursor().positionInBlock() == 4
    QTest.keyPress(editor, QtCore.Qt.Key_Backspace)
