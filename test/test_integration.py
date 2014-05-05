# -*- coding: utf-8 -*-
"""
A series of simple integration test, we check that a simple pyqode application
is running as expected, that the client server architecture works
as intended
"""
import os
import sys
import pytest

from PyQt4.QtTest import QTest
from PyQt4 import QtGui

from pyqode.core import frontend
from pyqode.core import backend
from pyqode.core.frontend.client import JsonTcpClient
from pyqode.core.frontend import modes, panels

from .helpers import cwd_at
from .helpers import require_python2
from .helpers import not_py2
from .helpers import python2_path


# -----------------
# Simple application test
# -----------------
@cwd_at('test')
def test_app():
    """
    Test a simple but complete app
    """
    editor = frontend.CodeEdit()
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))

    # install the same modes/panels as in the simple_editor example
    # add panels
    frontend.install_panel(editor, panels.LineNumberPanel())
    frontend.install_panel(editor, panels.SearchAndReplacePanel(),
                           panels.SearchAndReplacePanel.Position.BOTTOM)
    # add modes
    frontend.install_mode(editor, modes.AutoCompleteMode())
    frontend.install_mode(editor, modes.CaseConverterMode())
    frontend.install_mode(editor, modes.FileWatcherMode())
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_mode(editor, modes.RightMarginMode())
    frontend.install_mode(editor, modes.PygmentsSyntaxHighlighter(
        editor.document()))
    frontend.install_mode(editor, modes.ZoomMode())
    frontend.install_mode(editor, modes.CodeCompletionMode())
    frontend.install_mode(editor, modes.AutoIndentMode())
    frontend.install_mode(editor, modes.IndenterMode())
    frontend.install_mode(editor, modes.SymbolMatcherMode())

    frontend.open_file(editor, __file__)
    # editor.show()
    # QtCore.QTimer.singleShot(2000, _leave)
    QTest.qWait(2000)
    frontend.stop_server(editor)
    del editor


# -----------------
# Client/server tests
# -----------------
editor = None


def _on_receive(status, results):
    """
    Assert recevied data is the same as the data we send, a string wich contains
    'some data'.
    """
    assert status is True
    assert results == 'some data'
    app = QtGui.QApplication.instance()
    app.exit(0)


def _send_request():
    """
    Sends a request to the server. The request data is a simple string which
    contains 'some data'.
    """
    global client_socket
    frontend.request_work(editor,
                          backend.echo_worker, 'some data',
                          on_receive=_on_receive)


@cwd_at('test')
def test_client_server():
    """
    Checks that the client-server works as expected. We will send
    a request using the echo worker and assert it has the same data as we send,
    providing assurance that the client-server communication and protocol is
    OK.

    Once the result has been received we quit the qt app.
    """
    global editor
    app = QtGui.QApplication.instance()
    editor = frontend.CodeEdit()
    with pytest.raises(frontend.NotConnectedError):
        frontend.request_work(editor, backend.echo_worker, 'some data',
                              on_receive=_on_receive)
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    editor._client.connected.connect(_send_request)
    # win.show()
    app.exec_()
    del editor


@cwd_at('test')
@require_python2()
@not_py2()
def test_client_server_py2():
    """
    Same test as above except we run the server with python2 if available
    """
    global editor
    app = QtGui.QApplication.instance()
    editor = frontend.CodeEdit()
    with pytest.raises(frontend.NotConnectedError):
        frontend.request_work(editor, backend.echo_worker, 'some data',
                              on_receive=_on_receive)
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'),
                          interpreter=python2_path())
    editor._client.connected.connect(_send_request)
    app.exec_()
    del editor
