# -*- coding: utf-8 -*-
"""
Test the client/server API
"""
import os
import sys
from PyQt5 import QtWidgets
import pytest
from PyQt5.QtTest import QTest
from pyqode.core import frontend
from pyqode.core import backend
from pyqode.core.frontend.client import JsonTcpClient
from ..helpers import cwd_at, require_python2, python2_path, server_path, wait_for_connected


client_socket = None


def _on_receive(status, results):
    """
    Assert recevied data is the same as the data we send, a string which contains
    'some data'.
    """
    assert status is True
    assert results == 'some data'
    app = QtWidgets.QApplication.instance()
    app.exit(0)


def _send_request():
    """
    Sends a request to the server. The request data is a simple string which
    contains 'some data'.
    """
    global client_socket
    client_socket.request_work(backend.echo_worker, 'some data',
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
    global client_socket
    win = QtWidgets.QMainWindow()
    client_socket = JsonTcpClient(win)
    with pytest.raises(frontend.NotConnectedError):
        client_socket.request_work(backend.echo_worker, 'some data',
                                   on_receive=_on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'),
                        args=['-s', '/path'],
                        port=5566)
    client_socket.connected.connect(_send_request)
    QTest.qWait(1000)
    client_socket.close()
    del client_socket
    del win


@cwd_at('test')
@require_python2()
def test_client_server_py2(editor, app):
    """
    Test client/server with a python2 server.
    """
    frontend.stop_server(editor)
    with pytest.raises(frontend.NotConnectedError):
        frontend.request_work(editor, backend.echo_worker, 'some data',
                              on_receive=_on_receive)
    frontend.start_server(editor, server_path(),
                          interpreter=python2_path())
    wait_for_connected(editor)
    frontend.request_work(editor, backend.echo_worker, 'some data',
                          on_receive=_on_receive)
    QTest.qWait(500)
    frontend.stop_server(editor)
    frontend.start_server(editor, server_path())


def test_frozen_server():
    global client_socket
    win = QtWidgets.QMainWindow()
    client_socket = JsonTcpClient(win)
    with pytest.raises(frontend.NotConnectedError):
        client_socket.request_work(backend.echo_worker, 'some data',
                                   on_receive=_on_receive)
    client_socket.start('server.exe', args=['-s', '/path'], port=5566)