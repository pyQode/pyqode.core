"""
Tests the code completion mode
"""
import functools
from pyqode.qt import QtCore, QtWidgets
from pyqode.qt.QtTest import QTest
from pyqode.core import frontend, settings
from pyqode.core.frontend import modes

from ...helpers import cwd_at, server_path, wait_for_connected
from ...helpers import editor_open


def get_mode(editor):
    return frontend.get_mode(editor, modes.CodeCompletionMode)


def ensure_visible(func):
    """
    Ensures the frontend is connect is connected to the server. If that is not
    the case, the code completion server is started automatically
    """
    @functools.wraps(func)
    @cwd_at('test')
    def wrapper(editor, *args, **kwds):
        QtWidgets.QApplication.setActiveWindow(editor)
        editor.setFocus(True)
        return func(editor, *args, **kwds)
    return wrapper


def ensure_connected(func):
    """
    Ensures the frontend is connect is connected to the server. If that is not
    the case, the code completion server is started automatically
    """
    @functools.wraps(func)
    @cwd_at('test')
    def wrapper(editor, *args, **kwds):
        if not frontend.connected_to_server(editor):
            frontend.start_server(editor, server_path())
            wait_for_connected(editor)
        return func(editor, *args, **kwds)
    return wrapper


@editor_open(__file__)
@ensure_visible
def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


@editor_open(__file__)
@ensure_visible
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

    # restore settings for other tests
    editor.refresh_settings()
    assert mode.trigger_key == settings.cc_trigger_key


@editor_open(__file__)
@ensure_visible
def test_request_completion(editor):
    mode = get_mode(editor)
    QTest.qWait(1000)
    if frontend.connected_to_server(editor):
        frontend.stop_server(editor)
    # request a completion at start of the document, this request will be
    # skipped because we are in a comment/docstring zone.
    assert mode.request_completion() is False
    frontend.goto_line(editor, 4)
    QTest.qWait(100)
    assert mode.request_completion() is True
    # starts the server after the request to test the retry on NotConnected
    # mechanism
    frontend.start_server(editor, server_path())
    QTest.qWait(2000)
    # only the first request should be accepted
    ret1 = mode.request_completion()
    ret2 = mode.request_completion()
    assert ret1 is True and ret2 is False


@editor_open(__file__)
@ensure_connected
@ensure_visible
def test_events(editor):
    assert frontend.connected_to_server(editor)
    frontend.goto_line(editor, 4)
    QTest.keyPress(editor, settings.cc_trigger_key, QtCore.Qt.ControlModifier)
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
    QTest.keyPress(editor, settings.cc_trigger_key, QtCore.Qt.ControlModifier)


@editor_open(__file__)
@ensure_connected
@ensure_visible
def test_insert_completions(editor):
    assert frontend.connected_to_server(editor)
    frontend.goto_line(editor, 4)
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


@editor_open(__file__)
@ensure_connected
def test_show_completion_with_tooltip(editor):
    mode = get_mode(editor)
    settings.cc_show_tooltips = True
    editor.refresh_settings()
    mode._show_completions([{'name': 'test', 'tooltip': 'test desc'}])
    mode._display_completion_tooltip('test')
    mode._display_completion_tooltip('spam')
    mode.show_tooltips = False
    mode._display_completion_tooltip('test')


@editor_open(__file__)
@ensure_connected
def test_show_completion_with_icon(editor):
    mode = get_mode(editor)
    mode._show_completions([{'name': 'test',
                             'icon': ':/pyqode-icons/rc/edit-undo.png'}])
