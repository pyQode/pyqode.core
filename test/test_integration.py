# -*- coding: utf-8 -*-
"""
A series of simple integration test, we check that a simple pyqode application
is running is working as expected, that the client server architecture works
as intended
"""
import os
import sys
import pytest

from PyQt4 import QtCore
from PyQt4 import QtGui

from pyqode.core.editor import QCodeEdit
from pyqode.core import client
from pyqode.core import workers
from pyqode.core._internal.client import JsonTcpClient

from .helpers import cwd_at
from .helpers import require_python2
from .helpers import python2_path
from .helpers import not_py2


import logging
logging.basicConfig(level=logging.DEBUG)


# -----------------
# Simple application test
# -----------------
@cwd_at('test')
def test_app():
    """
    Test a simple but complete app
    """
    def _leave():
        """
        Leave test_app after a certain amount of time.
        """
        app = QtGui.QApplication.instance()
        app.exit(0)

    app = QtGui.QApplication(sys.argv)
    editor = QCodeEdit()
    client.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    editor.open_file(__file__)
    editor.show()
    QtCore.QTimer.singleShot(2000, _leave)
    app.exec_()
    client.stop_server(editor)
    del editor
    del app


# -----------------
# Client/server tests
# -----------------
client_socket = None


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
    client_socket.request_work(workers.echo, 'some data',
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
    app = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow()
    client_socket = JsonTcpClient(win)
    with pytest.raises(client.NotConnectedError):
        client_socket.request_work(workers.echo, 'some data',
                                   on_receive=_on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'))
    client_socket.connected.connect(_send_request)
    win.show()
    app.exec_()
    client_socket.close()
    del client_socket
    del win
    del app


@cwd_at('test')
@require_python2()
@not_py2()
def test_client_server_py2():
    """
    Same test as above except we run the server with python2 if available
    """
    global client_socket
    app = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow()
    client_socket = JsonTcpClient(win)
    with pytest.raises(client.NotConnectedError):
        client_socket.request_work(workers.echo, 'some data',
                                   on_receive=_on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'),
                        interpreter=python2_path())
    client_socket.connected.connect(_send_request)
    win.show()
    app.exec_()
    client_socket.close()
    del client_socket
    del win
    del app
