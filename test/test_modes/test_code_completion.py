"""
Tests the code completion mode
"""
import functools
import pytest

from pyqode.qt import QtCore, QtGui
from pyqode.qt.QtTest import QTest

from pyqode.core.api import TextHelper
from pyqode.core import modes
from pyqode.core.modes.code_completion import SubsequenceCompleter
from ..helpers import server_path, wait_for_connected
from ..helpers import ensure_visible, ensure_connected


def get_mode(editor):
    return editor.modes.get(modes.CodeCompletionMode)


code = '''"""
Empty module
"""
string = 'a string'
'''


def ensure_empty(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        editor.file._path = None
        editor.setPlainText(code, 'text/x-python', 'utf-8')
        return func(editor, *args, **kwds)
    return wrapper


@ensure_empty
@ensure_visible
@ensure_connected
def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@ensure_empty
@ensure_visible
@ensure_connected
def test_properties(editor):
    mode = get_mode(editor)
    mode.trigger_key = 'A'
    assert mode.trigger_key == 'A'
    mode.trigger_length = 3
    assert mode.trigger_length == 3
    mode.trigger_symbols = ['.', '->']
    assert len(mode.trigger_symbols) == 2
    assert '.' in mode.trigger_symbols
    assert '->' in mode.trigger_symbols
    mode.show_tooltips = False
    assert mode.show_tooltips is False
    mode.case_sensitive = True
    assert mode.case_sensitive is True
    mode.trigger_key = 1


@ensure_empty
@ensure_visible
@ensure_connected
@pytest.mark.xfail
def test_request_completion(editor):
    mode = get_mode(editor)
    QTest.qWait(1000)
    if editor.backend.running:
        editor.backend.stop()
    # starts the server after the request to test the retry on NotConnected
    # mechanism
    TextHelper(editor).goto_line(0)
    QTest.qWait(2000)
    mode.request_completion()
    editor.backend.start(server_path())
    QTest.qWait(1000)
    assert editor.backend.running is True
    # now this should work
    TextHelper(editor).goto_line(3)
    QTest.qWait(100)
    assert mode.request_completion() is True
    QTest.qWait(100)


@ensure_empty
@ensure_visible
@ensure_connected
@pytest.mark.xfail
def test_successive_requests(editor):
    mode = get_mode(editor)
    QTest.qWait(1000)
    TextHelper(editor).goto_line(3)
    assert editor.backend.running
    # only the first request should be accepted
    ret1 = mode.request_completion()
    ret2 = mode.request_completion()
    assert ret1 is True
    assert ret2 is True


@ensure_visible
@ensure_empty
@ensure_connected
def test_events(editor):
    assert editor.backend.running
    QTest.qWait(1000)
    TextHelper(editor).goto_line(3)
    QTest.keyPress(editor, QtCore.Qt.Key_Space, QtCore.Qt.ControlModifier)
    QTest.qWait(2000)
    QTest.keyPress(editor, QtCore.Qt.Key_Escape)
    QTest.qWait(500)
    QTest.keyPress(editor, 'm')
    QTest.keyPress(editor, 'o')
    QTest.qWait(1000)
    QTest.keyPress(editor, QtCore.Qt.Key_Escape)
    QTest.keyPress(editor, ' ')
    QTest.keyPress(editor, 'm')
    QTest.keyPress(editor, 'o')
    QTest.keyPress(editor, 'd')
    QTest.qWait(10)
    QTest.keyPress(editor, ' ')
    QTest.qWait(500)
    QTest.keyPress(editor, 'e')
    QTest.keyPress(editor, 'n')
    QTest.keyPress(editor, 'a')
    QTest.keyPress(editor, 'b')
    QTest.keyPress(editor, 'l')
    QTest.keyPress(editor, 'e')
    QTest.keyPress(editor, 'd')
    QTest.qWait(500)

    QTest.keyPress(editor, ' ')
    QTest.keyPress(editor, 'Q')
    QTest.keyPress(editor, 't')
    QTest.keyPress(editor, '.')
    QTest.qWait(500)

    QTest.keyPress(editor, 'Q')
    QTest.keyPress(editor, 't')
    QTest.qWait(500)
    QTest.keyPress(editor, QtCore.Qt.Key_Space, QtCore.Qt.ControlModifier)


@ensure_empty
@ensure_visible
@ensure_connected
def test_insert_completions(editor):
    assert editor.backend.running
    TextHelper(editor).goto_line(3)
    # check insert completions
    QTest.keyPress(editor, 'm')
    QTest.keyPress(editor, 'o')
    QTest.qWait(500)
    QTest.keyPress(editor, QtCore.Qt.Key_Return)

    # feature request #126: Key_Tab should select a completion
    QTest.keyPress(editor, QtCore.Qt.Key_Return)
    QTest.keyPress(editor, 'Q')
    QTest.keyPress(editor, 'T')
    QTest.keyPress(editor, 'e')
    QTest.keyPress(editor, 's')
    QTest.qWait(500)
    QTest.keyPress(editor, 't')

    QTest.qWait(100)


@ensure_empty
@ensure_connected
def test_show_completion_with_tooltip(editor):
    mode = get_mode(editor)
    mode.show_tooltips = True
    mode._show_completions([{'name': 'test', 'tooltip': 'test desc'}])
    mode._display_completion_tooltip('test')
    mode._display_completion_tooltip('spam')
    mode.show_tooltips = False
    mode._display_completion_tooltip('test')


@ensure_empty
@ensure_connected
def test_show_completion_with_icon(editor):
    mode = get_mode(editor)
    mode._show_completions([{'name': 'test',
                             'icon': ':/pyqode-icons/rc/edit-undo.png'}])


@pytest.mark.parametrize('case', [
    QtCore.Qt.CaseSensitive, QtCore.Qt.CaseInsensitive])
def test_subsequence_completer(case):
    completer = SubsequenceCompleter()
    words = ['actionA', 'actionB', 'setMySuperAction',
             'geTToolTip', 'setStatusTip', 'seTToolTip']
    model = QtGui.QStandardItemModel()
    for word in words:
        item = QtGui.QStandardItem()
        item.setData(word, QtCore.Qt.DisplayRole)
        model.appendRow(item)
    completer.setCaseSensitivity(case)
    completer.setModel(model)
    if case == QtCore.Qt.CaseInsensitive:
        completer.setCompletionPrefix('tip')
        completer.update_model()
        assert completer.completionCount() == 3
        completer.setCompletionPrefix('settip')
        completer.update_model()
        assert completer.completionCount() == 2
        completer.update_model()
        completer.setCompletionPrefix('action')
        completer.update_model()
        assert completer.completionCount() == 3
    else:
        completer.setCompletionPrefix('tip')
        completer.update_model()
        assert completer.completionCount() == 1  # setStatusTip
        completer.setCompletionPrefix('Tip')
        completer.update_model()
        assert completer.completionCount() == 3  # all word ending with Tip
        completer.setCompletionPrefix('setTip')
        completer.update_model()
        assert completer.completionCount() == 1  # setStatusTip
        completer.setCompletionPrefix('action')
        completer.update_model()
        assert completer.completionCount() == 2
