#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
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
This module contains the subprocess server used to run heavy task such as
code completion, code analysis,... in a background thread.

The server will start automatically when you create your first pyqode widget but
it can also be started manually with custom startup parameters (you can choose to
reuse an existing local server or start a new one for your process). There can only
be one server per process, the server is shared among all code editor instances.

The server is able to run multiple background worker in a dedicated worker slot.
A worker slot is a named background thread that will be used to run a specific
kind of worker. Worker object must define a _slot attribute that will be used to
dispatch them on the matching slot thread.
"""
import multiprocessing
from multiprocessing.connection import Client, Listener
Listener.fileno = lambda self: self._listener._socket.fileno()
import select
import sys
import time
if sys.version_info[0] == 3:
    import _thread as thread
else:
    import thread

from pyqode.core import logger
from pyqode.qt import QtGui, QtCore


class SubprocessServer(object):
    """
    Utility class to run a child process use to execute heavy load computations
    such as file layout analysis, code completion requests...

    To use the server, just create an instance and call the
    :meth:`pyqode.core.SubprocessServer.start` method.

    To request a job, use the requestWork method and pass it your worker object
    (already configured to do its work).

    The server will send the request to the child process and will emit the
    workCompleted signal when the job finished.
    """

    def __init__(self, name="pyQodeSubprocessServer", autoCloseOnQuit=True):
        #: Server signals; see :meth:`pyqode.core.system._ServerSignals`
        self.signals = _ServerSignals()
        self.__name = name
        self.__running = False
        self._workQueue = []
        if autoCloseOnQuit:
            QtGui.QApplication.instance().aboutToQuit.connect(self.close)

    def close(self):
        """
        Closes the server, terminates the child process.
        """
        logger.info("Close server")
        if self.__running:
            self.__running = False
            self.__process.terminate()

    def start(self, port=8080):
        """
        Starts the server. This will actually start the child process.

        :param port: Local TCP/IP port to which the underlying socket is
                     connected to.
        """
        self.__process = multiprocessing.Process(target=childProcess,
                                                 name=self.__name,
                                                 args=(port, ))
        self.__process.start()
        self.__running = False
        try:
            if sys.platform == "win32":
                self._client = Client(('localhost', port))
            else:
                try:
                    self._client = Client(('', port))
                except OSError:
                    # wait a second before starting, this occur if we were connected to
                    # previously running server that has just closed (we need to wait a
                    # little before starting a new one)
                    time.sleep(1)
                    self._client = Client(('', port))
            logger.info("Connected to Code Completion Server on 127.0.0.1:%d" %
                        port)
            self.__running = True
            self._lock = thread.allocate_lock()
            thread.start_new_thread(self._threadFct, ())
        except OSError:
            logger.exception("Failed to connect to Code Completion Server on "
                             "127.0.0.1:%d" % port)
        return self.__running

    def _threadFct(self, *args):
        while self.__running:
            with self._lock:
                while len(self._workQueue):
                    caller_id, worker = self._workQueue.pop(0)
                    self._client.send([caller_id, worker])
                    logger.debug("SubprocessServer work requested: %s " % worker)
            self.__poll()
            time.sleep(0.001)

    def requestWork(self, caller, worker):
        """
        Requests a work. The work will be called in the child process and its
        results will be available through the
        :attr:`pyqode.core.SubprocessServer.signals.workCompleted` signal.

        :param caller: caller object
        :type caller: object

        :param worker: Callable **object**, must override __call__ with no
                       parameters.
        :type worker: callable
        """
        logger.debug("SubprocessServer requesting work: %s " % worker)
        caller_id = id(caller)
        with self._lock:
            self._workQueue.append((caller_id, worker))

    def __poll(self):
        """
        Poll the child process for any incoming results
        """
        if self._client.poll():
            try:
                data = self._client.recv()
                if len(data) == 3:
                    caller_id = data[0]
                    worker = data[1]
                    results = data[2]
                    if results is not None:
                        self.signals.workCompleted.emit(caller_id, worker, results)
                else:
                    logger.info(data)
            except (IOError, EOFError):
                logger.warning("Lost completion server, restarting")
                self.start()


class _ServerSignals(QtCore.QObject):
    """
    Holds the server signals.
    """
    #: Signal emitted when a new work is requested.
    #:
    #: **Parameters**:
    #:   * caller id
    #:   * worker object
    workRequested = QtCore.Signal(object, object)

    #: Signal emitted when a new work is requested.
    #:
    #: **Parameters**:
    #:   * caller id
    #:   * worker object
    #:   * worker results
    workCompleted = QtCore.Signal(object, object, object)


def serverLoop(dict, listener):
    clients = []
    while True:
        r, w, e = select.select((listener, ), (), (), 0.1)
        if listener in r:
            cli = listener.accept()
            clients.append(cli)
            logger.debug("Client accepted: %s" % cli)
            logger.debug("Nb clients connected: %s" % len(clients))
        for cli in clients:
            try:
                if cli.poll():
                    data = cli.recv()
                    assert len(data) == 2
                    caller_id, worker = data[0], data[1]
                    setattr(worker, "processDict", dict)
                    execWorker(cli, caller_id, worker)
            except (IOError, OSError, EOFError):
                clients.remove(cli)


def childProcess(port):
    """
    This is the child process. It run endlessly waiting for incoming work
    requests.
    """
    dict = {}
    try:
        if sys.platform == "win32":
            listener = Listener(('localhost', port))
        else:
            listener = Listener(('', port))
        #client = listener.accept()
    except OSError:
        logger.warning("Failed to start the code completion server process on "
                       "port %d, there is probably another completion server "
                       "already running with a socket open on the same port. "
                       "\nThe existing server process will be used instead." % port)
        return 0
    else:
        logger.info("Code Completion Server started on 127.0.0.1:%d" % port)
        serverLoop(dict, listener)


def execWorker(conn, caller_id, worker):
    """
    This function call the worker object.

    :param conn: connection

    :param id: caller id

    :param worker: worker instance
    """
    try:
        results = worker(conn, caller_id)
    except Exception as e:
        logger.exception("SubprocessServer.Worker (%r)" % worker)
        results = []
    # reset obj attributes before sending it back to the main process
    worker.__dict__ = {}
    conn.send([caller_id, worker, results])