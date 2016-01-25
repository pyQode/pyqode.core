import os
import sys
from pyqode.core.api import CodeEdit
from pyqode.core.backend import NotRunning
from pyqode.qt import QtWidgets
import pytest
from pyqode.qt.QtTest import QTest
from pyqode.core import backend
from pyqode.core.managers.backend import BackendManager
from ..helpers import cwd_at, python2_path, server_path, wait_for_connected


from ..helpers import editor_open, ensure_connected


@editor_open(__file__)
@ensure_connected
def test_exit_code(editor):
    assert editor.backend.running
    assert editor.backend.exit_code is None
    editor.backend.stop()
    assert not editor.backend.running


backend_manager = None


def _on_receive(results):
    """
    Assert recevied data is the same as the data we send, a string which contains
    'some data'.
    """
    assert results == 'some data'
    app = QtWidgets.QApplication.instance()
    app.exit(0)


def _send_request():
    """
    Sends a request to the server. The request data is a simple string which
    contains 'some data'.
    """
    global backend_manager
    backend_manager.send_request(backend.echo_worker, 'some data',
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
    global backend_manager
    win = QtWidgets.QMainWindow()
    backend_manager = BackendManager(win)
    with pytest.raises(NotRunning):
        backend_manager.send_request(
            backend.echo_worker, 'some data', on_receive=_on_receive)
    backend_manager.start(os.path.join(os.getcwd(), 'server.py'))
    backend_manager._process.started.connect(_send_request)
    QTest.qWait(1000)
    backend_manager.stop()
    del backend_manager
    del win


def test_client_server_py2(editor):
    """
    Test client/server with a python2 server.
    """
    editor.backend.stop()
    with pytest.raises(NotRunning):
        editor.backend.send_request(
            backend.echo_worker, 'some data', on_receive=_on_receive)
    if os.path.exists(python2_path()):
        editor.backend.start(server_path(), interpreter=python2_path())
        wait_for_connected(editor)
        editor.backend.send_request(
            backend.echo_worker, 'some data', on_receive=_on_receive)
        QTest.qWait(500)
        editor.backend.stop()
        editor.backend.start(server_path())


def test_frozen_server():
    global backend_manager
    win = QtWidgets.QMainWindow()
    backend_manager = BackendManager(win)
    with pytest.raises(NotRunning):
        backend_manager.send_request(
            backend.echo_worker, 'some data', on_receive=_on_receive)
    backend_manager.start('server.exe')
