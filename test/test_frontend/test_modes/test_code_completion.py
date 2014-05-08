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
    editor = frontend.CodeEdit()
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)


def teardown_module():
    global editor
    frontend.uninstall_mode(editor, modes.CodeCompletionMode)
    frontend.stop_server(editor)
    del editor


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


def test_completions_requests():
    mode.request_completion()
    frontend.start_server(editor, os.path.abspath('server.py'))
    QTest.qWait(500)
