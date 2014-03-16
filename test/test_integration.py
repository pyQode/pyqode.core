#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
A series of simple integration test, we check that a simple pyqode application
is running is working as expected, that the client server is respected,...
"""
import os
import pytest
import sys
if sys.version_info[0] == 2:
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
from PyQt4 import QtCore, QtGui
from pyqode.core import QGenericCodeEdit
from pyqode.core.api import client, server, workers
from .helpers import cwd_at


client_socket = None


def _leave():
    app = QtGui.QApplication.instance()
    app.exit(0)


@cwd_at('test')
def test_app():
    """
    Test an entire app
    """
    app = QtGui.QApplication(sys.argv)
    editor = QGenericCodeEdit()
    editor.start_server(os.path.join(os.getcwd(), 'server.py'))
    editor.openFile(__file__)
    editor.show()
    QtCore.QTimer.singleShot(500, _leave)
    app.exec_()
    del editor
    del app


def on_receive(status, results):
    assert status is True
    assert results == 'some data'
    app = QtGui.QApplication.instance()
    app.exit(0)


def send_request():
    global client_socket
    client_socket.request_work(workers.echo, 'some data',
                               on_receive=on_receive)


@cwd_at('test')
def test_client_server():
    """
    Checks that the client-server works as expected. We will send
    a request using the echo worker and assert it has the same data as we send,
    providing assurance that the client-server communication and protocol is OK.

    Once the result has been received we quit the qt app.
    """
    global client_socket
    app = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow()
    client_socket = client.JsonTcpClient(win)
    with pytest.raises(client.NotConnectedError):
        client_socket.request_work(workers.echo, 'some data',
                                   on_receive=on_receive)
    client_socket.start(os.path.join(os.getcwd(), 'server.py'))
    client_socket.connected.connect(send_request)
    win.show()
    app.exec_()
    client_socket.close()
    del client_socket
    del win
    del app
