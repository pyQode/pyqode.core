import os
import sys
from PyQt4 import QtGui
import pytest
from pyqode.core import frontend
from pyqode.core import backend
from pyqode.core.frontend.client import JsonTcpClient
from ..helpers import cwd_at
from ..helpers import require_python2
from ..helpers import python2_path
from ..helpers import not_py2

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
    app = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow()
    client_socket = JsonTcpClient(win)
    with pytest.raises(frontend.NotConnectedError):
        client_socket.request_work(backend.echo_worker, 'some data',
                                   on_receive=_on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'))
    client_socket.connected.connect(_send_request)
    # win.show()
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
    with pytest.raises(frontend.NotConnectedError):
        client_socket.request_work(backend.echo_worker, 'some data',
                                   on_receive=_on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'),
                        interpreter=python2_path())
    client_socket.connected.connect(_send_request)
    # win.show()
    app.exec_()
    client_socket.close()
    del client_socket
    del win
    del app



