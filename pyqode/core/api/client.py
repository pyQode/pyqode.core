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
This module contains client json tcp socket of the API. The client is
responsible of running and terminating the server process and takes care
of the send/receive operation. It allows to send/receive python objects that
are Json serializable.

One of the goal of this client-server architecture is to be able to run the
server process with a different interpreter than the one used for the gui
application. This is badly needed in pyqode.python to be able to support
python2 syntax in a python3 based application. This also simplify and open up
more possiblities when freezing a pyqode application.
"""
import json
import os
import socket
import struct
import sys
import uuid
from PyQt4 import QtCore, QtNetwork, QtGui


#: Maps QAbstractSocket::SocketError to string to easily get descriptive error
#: message out of error numbers.
SOCKET_ERROR_STRINGS = {
    0: 'the connection was refused by the peer (or timed out).',
    1: 'the remote host closed the connection.',
    2: 'the host address was not found.',
    3: 'the socket operation failed because the application lacked the '
       'required privileges.',
    4: 'the local system ran out of resources (e.g., too many sockets).',
    5: 'the socket operation timed out.',
    6: "the datagram was larger than the operating system's limit (which can "
       "be as low as 8192 bytes).",
    7: 'an error occurred with the network (e.g., the network cable was '
       'accidentally plugged out).',
    # 9 and 10 are UDP only, we only care about TCP.
    # all others erros are unlikely to happen in our case (proxy related errors)
    -1: 'an unidentified error occurred.',
}

PROCESS_ERROR_STRING = {
    0: 'the process failed to start. Either the invoked program is missing, or '
       'you may have insufficient permissions to invoke the program.',
    1: 'the process crashed some time after starting successfully.',
    2: 'the last waitFor...() function timed out. The state of QProcess is '
       'unchanged, and you can try calling waitFor...() again.',
    4: 'an error occurred when attempting to write to the process. '
       'For example, the process may not be running, or it may have closed its '
       'input channel.',
    3: 'an error occurred when attempting to read from the process. '
       'For example, the process may not be running.',
    5: 'an unknown error occurred. This is the default return value of error().'
}


class JsonTcpClient(QtNetwork.QTcpSocket):
    """
    A json tcp client socket used to start and communicate with the pyqode
    server.

    It uses a simple message protocol. A message is made up of two parts.
    parts:
      - header: this simply contains the length of the payload. (4bytes)
      - payload: this is the actual message data as a json (byte) string.
    """

    def __init__(self, parent):
        QtNetwork.QTcpSocket.__init__(self, parent)
        self.connected.connect(self._on_connected)
        self.error.connect(self._on_error)
        self.disconnected.connect(self._on_disconnected)
        self.readyRead.connect(self._on_ready_read)
        self._srv_logger = logging.getLogger('pyqode-server')
        self._cli_logger = logging.getLogger('pyqode-client')
        self._header_complete = False
        self._header_buf = bytes()
        self._to_read = 0
        self._data_buf = bytes()
        #: associate request uuid with a callback, popped once executed
        self._callbacks = {}
        self.is_connected = False
        self.is_server_running = False

    def close(self):
        """
        Closes the socket and terminates the server process.
        """
        if self.is_connected and self.is_server_running:
            # send shutdown request
            self.send('shutdown')
        QtNetwork.QTcpSocket.close(self)
        if self.is_server_running:
            self.is_server_running = False
            self._process.terminate()
            self._process.waitForFinished()
        self.is_connected = False

    def start(self, server_script, interpreter=sys.executable, args=None):
        """
        Starts a pyqode server (and connect our client socket when the server
        process has started). The server is started with a random free port
        on local host (the port number is defined by command line args).

        The server is a python script that starts a
        :class:`pyqode.core.api.server.JsonServer`. You (the user) must write
        the server script so that you can apply your own configuration
        server side.

        The script can be run with a custom interpreter. The default is to use
        sys.executable.

        :param str server_script: Path to the server main script.
        :param str interpreter: The python interpreter to use to run the server
            script. If None, sys.executable is used unless we are in a frozen
            application (cx_Freeze). The executable is not used if the
            executable scripts ends with '.exe' on Windows
        :param list args: list of additional command line args to use to start
            the server process.
        """
        self._cli_logger.debug('running with python %d.%d.%d' %
                               sys.version_info[:3])
        assert os.path.exists(server_script)
        if not interpreter:
            interpreter = sys.executable
        self._process = QtCore.QProcess(self.parent())
        self._process.started.connect(self._on_process_started)
        self._process.error.connect(self._on_process_error)
        self._process.finished.connect(self._on_process_finished)
        self._process.readyReadStandardOutput.connect(
            self._on_process_stdout_ready)
        self._process.readyReadStandardError.connect(
            self._on_process_stderr_ready)
        self._port = self._pick_free_port()
        if server_script.endswith('.exe'):
            # frozen server script on windows does not need an interpreter
            program = server_script
            pgm_args = [str(self._port)]
        else:
            program = interpreter
            pgm_args = [server_script, str(self._port)]
        if args:
            pgm_args += args
        self._process.start(program, pgm_args)
        self._cli_logger.debug('starting server process: %s %s' %
                               (program, ' '.join(pgm_args)))

    def request_work(self, worker_class_or_function, args, on_receive=None):
        """
        Request a work on the server.

        :param worker_class_or_function: fully qualified name of the worker
            class/function to execute remotely.
        :param args: worker args, any Json serializable objects
        :param on_receive: an optional callback executed when we receive the
            worker's results. The callback will be called with two arguments:
            the status (bool) and the results (object)
        """
        classname = '%s.%s' % (worker_class_or_function.__module__,
                               worker_class_or_function.__name__)
        request_id = str(uuid.uuid4())
        if on_receive:
            self._callbacks[request_id] = on_receive
        self.send({'request_id': request_id, 'worker': classname,
                   'data': args})

    def send(self, obj, encoding='utf-8'):
        """
        Sends a python object to the server. The object must be JSON
        serialisable.

        :param obj: object to send
        :param encoding: encoding used to encode the json message into a
            bytes array, this should match QCodeEdit.file_encoding.
        """
        self._cli_logger.debug('sending request: %r' % obj)
        msg = json.dumps(obj)
        msg = msg.encode(encoding)
        header = struct.pack('=I', len(msg))
        self.write(header)
        self.write(msg)

    def _pick_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        free_port = int(s.getsockname()[1])
        s.close()
        return free_port

    def _connect(self):
        address = QtNetwork.QHostAddress('127.0.0.1')
        self.connectToHost(address, self._port)

    def _on_connected(self):
        self._cli_logger.debug('connected to server: %s:%d' %
                               (self.peerName(), self.peerPort()))
        self.is_connected = True

    def _on_error(self, socket_error):
        if not socket_error in SOCKET_ERROR_STRINGS:
            socket_error = -1
        self._cli_logger.error('socket error %d: %s' % (socket_error,
                               SOCKET_ERROR_STRINGS[socket_error]))

    def _on_disconnected(self):
        try:
            self._cli_logger.debug('disconnected from server: %s:%d' %
                                   (self.peerName(), self.peerPort()))
        except AttributeError:
            pass   # logger might be None if for some reason qt deletes the
                   # socket after python global exit
        self.is_connected = False

    def _on_ready_read(self):
        while self.bytesAvailable():
            if not self._header_complete:
                self._header_buf += self.read(4)
                if len(self._header_buf) == 4:
                    self._header_complete = True
                    s = struct.unpack('=I', self._header_buf)
                    self._to_read = s[0]
                    self._header_buf = bytes()
            else:
                self._data_buf += self.read(self._to_read)
                self._to_read = self._to_read - len(self._data_buf)
                if self._to_read == 0:
                    data = self._data_buf.decode('utf-8')
                    obj = json.loads(data)
                    self._cli_logger.debug('response received: %r' % obj)
                    try:
                        request_id = obj['request_id']
                        results = obj['results']
                        status = obj['status']
                    except (TypeError, KeyError):
                        pass  # internal request, no callback
                    else:
                        # possible callback
                        if request_id in self._callbacks:
                            callback = self._callbacks.pop(request_id)
                            callback(status, results)
                    self._header_complete = False
                    self._data_buf = bytes()

    def _on_process_started(self):
        self._cli_logger.debug('server process started')
        QtCore.QTimer.singleShot(100, self._connect)
        self.is_server_running = True

    def _on_process_error(self, error):
        if not self.is_server_running:
            return
        if not error in PROCESS_ERROR_STRING:
            socket_error = -1
        self._cli_logger.debug('server process error %s: %s' % (error,
                               PROCESS_ERROR_STRING[error]))

    def _on_process_finished(self, exit_code):
        self._cli_logger.debug('server process finished with exit code %d' %
                               exit_code)
        self.is_server_running = False

    def _on_process_stdout_ready(self):
        output = bytes(self._process.readAllStandardOutput()).decode('utf-8')
        output = output[:output.rfind('\n')]
        for l in output.splitlines():
            self._srv_logger.debug(l)

    def _on_process_stderr_ready(self):
        output = bytes(self._process.readAllStandardError()).decode('utf-8')
        output = output[:output.rfind('\n')]
        for l in output.splitlines():
            self._srv_logger.error(l)


# Usage example
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from pyqode.core.api import server, workers

    def send_request():
        client.request_work(workers.echo,
                            {'code': 'print("Python is nice")',
                             'line': 1,
                             'column': 8,
                             'encoding': 'utf-8',
                             'path': '/a/path/to/a/file'},
                            on_receive=callback)
        QtCore.QTimer.singleShot(1000, send_request)

    def callback(status, results):
        logging.debug('Yeah I got results from the server: '
                      '(status=%r, results=%r)' % (status, results))

    app = QtGui.QApplication(sys.argv)
    window = QtGui.QPlainTextEdit()
    client = JsonTcpClient(window)
    client.start(server.__file__, 'python')
    client.connected.connect(send_request)
    window.show()
    app.exec_()
    client.close()
