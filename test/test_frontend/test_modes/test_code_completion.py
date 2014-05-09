"""
Tests the code completion mode
"""
import functools
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend, settings
from pyqode.core.frontend import modes, panels
from ...helpers import cwd_at


editor = None
mode = modes.CodeCompletionMode()


@cwd_at('test')
def setup_module():
    global editor, mode
    settings.save_on_focus_out = False
    editor = frontend.CodeEdit()
    frontend.install_mode(editor, mode)
    frontend.install_mode(editor, modes.PygmentsSyntaxHighlighter(
        editor.document()))
    frontend.open_file(editor, __file__)
    editor.setMinimumWidth(800)
    editor.show()


def teardown_module():
    global editor
    frontend.uninstall_mode(editor, modes.CodeCompletionMode)
    frontend.stop_server(editor)
    del editor


def ensure_connected_and_visible(func):
    """
    Ensures the frontend is connect is connected to the server. If that is not
    the case, the code completion server is started automatically
    """
    @functools.wraps(func)
    @cwd_at('test')
    def wrapper(*args, **kwds):
        global editor
        if not frontend.connected_to_server(editor):
            frontend.start_server(editor, 'server.py')
        QtGui.QApplication.instance().setActiveWindow(editor)
        return func(*args, **kwds)
    return wrapper


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_properties():
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


@cwd_at('test')
def test_request_completion():
    QtGui.QApplication.instance().setActiveWindow(editor)
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
    frontend.start_server(editor, os.path.abspath('server.py'))
    QTest.qWait(2000)
    # only the first request should be accepted
    ret1 = mode.request_completion()
    ret2 = mode.request_completion()
    assert ret1 is True and ret2 is False


@ensure_connected_and_visible
def test_events():
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


@ensure_connected_and_visible
def test_insert_completions():
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


def test_show_completion_with_tooltip():
    settings.cc_show_tooltips = True
    editor.refresh_settings()
    mode._show_completions([{'name': 'test', 'tooltip': 'test desc'}])
    mode._display_completion_tooltip('test')
    mode._display_completion_tooltip('spam')
    mode.show_tooltips = False
    mode._display_completion_tooltip('test')


def test_show_completion_with_icon():
    mode._show_completions([{'name': 'test',
                             'icon': ':/pyqode-icons/rc/edit-undo.png'}])
