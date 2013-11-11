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
Contains utility functions
"""
import collections
import functools
import multiprocessing
from multiprocessing.connection import Listener, Client
import errno, socket
Listener.fileno = lambda self: self._listener._socket.fileno()
import select
import os
import sys
import time
import weakref
from pyqode.core import logger
from pyqode.qt import QtCore, QtGui
if sys.version_info[0] == 3:
    import _thread as thread
else:
    import thread


class memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            if not isinstance(args, collections.Hashable):
                # uncacheable. a list, for instance.
                # better to not cache than blow up.
                return self.func(*args)
            if args in self.cache:
                return self.cache[args]
            else:
                value = self.func(*args)
                self.cache[args] = value
                return value
        except TypeError:
            return self.func(*args)

    def __repr__(self):
        """ Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)


def findSettingsDirectory(appName="pyQode"):
    """
    Creates and returns the path to a directory that suits well to store app/lib
    settings on Windows and Linux.
    """
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        pth = os.path.join(home, appName)
    else:
        pth = os.path.join(home, ".%s" % appName)
    if not os.path.exists(pth):
        os.mkdir(pth)
    return pth


def mergedColors(colorA, colorB, factor):
    maxFactor = 100
    colorA = QtGui.QColor(colorA)
    colorB = QtGui.QColor(colorB)
    tmp = colorA
    tmp.setRed((tmp.red() * factor) / maxFactor +
               (colorB.red() * (maxFactor - factor)) / maxFactor)
    tmp.setGreen((tmp.green() * factor) / maxFactor +
                 (colorB.green() * (maxFactor - factor)) / maxFactor)
    tmp.setBlue((tmp.blue() * factor) / maxFactor +
                (colorB.blue() * (maxFactor - factor)) / maxFactor)
    return tmp


def driftColor(baseColor, factor=110):
    """
    Return a near color that is lighter or darker than the base color.

    If baseColor.lightness is higher than 128 than darker is used else lighter
    is used.

    :param baseColor: The base color to drift.

    :return A lighter or darker color.
    """
    if baseColor.lightness() > 128:
        return baseColor.darker(factor)
    else:
        return baseColor.lighter(factor+10)


def indexMatching(seq, condition):
    """
    Returns the index of the element that match condition.

    :param seq: The sequence to parse

    :param condition: The index condition

    :return: Index of the element that mathc the condition of -1
    """
    for i,x in enumerate(seq):
        if condition(x):
            return i
    return -1


def indexByName(seq, name):
    """
    Search an element by "name".

    :param seq: Sequence to parse

    :param name: Name of the element

    :return: Index of the element of -1
    """
    return indexMatching(seq, lambda x: x.name == name)


class TextStyle(object):
    """
    Defines a text style: a color associated with text style options (bold,
    italic and underline).

    This class has methods to set the text style from a string and to easily
    be created from a string.
    """

    def __init__(self, style=None):
        """
        :param style: The style string ("#rrggbb [bold] [italic] [underlined])
        """
        self.color = QtGui.QColor()
        self.bold = False
        self.italic = False
        self.underlined = False
        if style:
            self.from_string(style)

    def __repr__(self):
        color = self.color.name()
        bold = "nbold"
        if self.bold:
            bold = "bold"
        italic = "nitalic"
        if self.italic:
            italic = "italic"
        underlined = "nunderlined"
        if self.underlined:
            underlined = "underlined"
        return " ".join([color, bold, italic, underlined])

    @memoized
    def from_string(self, string):
        tokens = string.split(" ")
        assert len(tokens) == 4
        self.color = QtGui.QColor(tokens[0])
        self.bold = False
        if tokens[1] == "bold":
            self.bold = True
        self.italic = False
        if tokens[2] == "italic":
            self.italic = True
        self.underlined = False
        if tokens[3] == "underlined":
            self.underlined = True


def inheritors(klass):
    """
    Returns all the class that inherits from klass (all the classes that
    were already imported)

    :param klass: class type

    :return: list of subclasses
    """
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


class _InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, _InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class _Invoker(QtCore.QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)
        return True


class _JobThread(QtCore.QThread):
    """
    Runs a callable into a QThread. The thread may be stopped at anytime using
    the stopJobThreadInstance static method.
    """

    __name = "JobThread({}{}{})"

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.__jobResults = None
        self.used = False
        self.args = ()
        self.kwargs = {}
        self.executeOnRun = None
        self.executeOnFinish = None

    @staticmethod
    def stopJobThreadInstance(caller, method, *args, **kwargs):
        caller.invoker = _Invoker()
        caller.invokeEvent = _InvokeEvent(method, *args, **kwargs)
        QtCore.QCoreApplication.postEvent(caller.invoker, caller.invokeEvent)

    def __repr__(self):
        if hasattr(self, "executeOnRun"):
            name = self.executeOnRun.__name__
        else:
            name = hex(id(self))
        return self.__name.format(name, self.args, self.kwargs)

    def stopRun(self):
        self.onFinish()
        self.terminate()
        self.used = False
        self.setMethods(None, None)

    def setMethods(self, onRun, onFinish):
        self.executeOnRun = onRun
        self.executeOnFinish = onFinish

    def setParameters(self, *a, **kw):
        self.args = a
        self.kwargs = kw

    def onFinish(self):
        if (hasattr(self, "executeOnFinish") and self.executeOnFinish
                and hasattr(self.executeOnFinish, '__call__')):
            self.executeOnFinish()

    def run(self):
        if (hasattr(self, "executeOnRun") and self.executeOnRun
                and hasattr(self.executeOnRun, '__call__')):
            self.executeOnRun(*self.args, **self.kwargs)
            self.onFinish()
            self.used = False
            self.setMethods(None, None)
        else:
            logger.warning("Executing not callable statement: %s" %
                            self.executeOnRun)


class JobRunner(object):
    """
    Utility class to easily run an asynchroneous job. A job is a simple
    callable (method) that will be run in a background thread.

    JobRunner implements a job queue to ensure there is only one job running
    per JobRunner instance. If a job is already running, the new job will wait
    for the current job to finish unless you want to force its execution. It
    that case the current job will be terminated.

    Additional parameters can be supplied to the job using args and kwargs.

    .. code-block:: python

        self.jobRunner = JobRunner(self)
        self.jobRunner.startJob(self.aJobMethod)

    .. warning:: Do not manipulate QWidgets from your job method. Use
                 signal/slots to propagate changes to the ui.
    """
    @property
    def caller(self):
        return self.__caller()

    @property
    def jobRunning(self):
        return self.__jobRunning

    def __init__(self, caller, nbThreadsMax=3):
        """
        :param caller: The object that will ask for a job to be run. This must
        be a subclass of QObject.
        """
        self.__caller = weakref.ref(caller)
        self.__jobQueue = []
        self.__threads = []
        self.__jobRunning = False
        for i in range(nbThreadsMax):
            self.__threads.append(_JobThread())

    def __repr__(self):
        return repr(self.__jobQueue[0] if len(self.__jobQueue) > 0 else "None")

    def findUnusedThread(self):
        for thread in self.__threads:
            if not thread.used:
                return thread
        return None

    def startJob(self, job, force, *args, **kwargs):
        """
        Starts a job in a background thread.

        :param job: job.
        :type job: callable

        :param force: Specify if we must force the job execution by stopping
                      the job that is currently running (if any).
        :type force: bool

        :param args: args
        :param kwargs: kwargs
        """
        thread = self.findUnusedThread()
        if thread:
            thread.setMethods(job, self.__executeNext)
            thread.setParameters(*args, **kwargs)
            thread.used = True
            if force:
                self.__jobQueue.append(thread)
                self.stopJob()
            else:
                self.__jobQueue.append(thread)
            if not self.__jobRunning:
                self.__jobQueue[0].setMethods(job, self.__executeNext)
                self.__jobQueue[0].setParameters(*args, **kwargs)
                self.__jobRunning = True
                self.__jobQueue[0].start()
            return True
        else:
            logger.debug("Failed to queue job. All threads are used")
            return False

    def __executeNext(self):
        self.__jobRunning = False
        if len(self.__jobQueue) > 0:
            self.__jobQueue.pop(0)
        if len(self.__jobQueue) > 0:
            self.__jobQueue[0].start()
            self.__jobRunning = True
            self.__jobQueue[0].used = True

    def stopJob(self):
        """
        Stops the current job
        """
        if len(self.__jobQueue) > 0:
            _JobThread.stopJobThreadInstance(
                self.caller, self.__jobQueue[0].stopRun)


class DelayJobRunner(JobRunner):
    """
    Extends the JobRunner to introduce a delay between the job request and the
    job execution. If a new job is requested, the timer is stopped discarding a
    possible waiting job.

    This is heavily used internally for situations where the user can cancel a
    job (code completion, calltips,...).
    """
    def __init__(self, caller, nbThreadsMax=3, delay=500):
        JobRunner.__init__(self, caller, nbThreadsMax=nbThreadsMax)
        self.__timer = QtCore.QTimer()
        self.__interval = delay
        self.__timer.timeout.connect(self.__execRequestedJob)

    def requestJob(self, job, async, *args, **kwargs):
        """
        Request a job execution. The job will be executed after the delay
        specified in the DelayJobRunner contructor elapsed if no other job is
        requested until then.

        :param job: job.
        :type job: callable

        :param async: Specify if the job should be run asynchronously
        :type async: bool

        :param force: Specify if we must force the job execution by stopping
                      the job that is currently running (if any).
        :type force: bool

        :param args: args
        :param kwargs: kwargs
        """
        self.__timer.stop()
        self.__job = job
        self.__args = args
        self.__kwargs = kwargs
        self.__async = async
        self.__timer.start(self.__interval)

    def cancelRequests(self):
        """
        Cancels pending requests.
        """
        self.__timer.stop()

    def __execRequestedJob(self):
        """
        Execute the requested job after the timer has timeout.
        """
        self.__timer.stop()
        if self.__async:
            self.startJob(self.__job, False, *self.__args, **self.__kwargs)
        else:
            self.__job(*self.__args, **self.__kwargs)
        self.__job = None
        self.__args = None
        self.__kwargs = None
        self.__async = None


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
    logger.debug("Send result %r for worker %r" % (results, worker))
    # reset obj attributes before sending it back to the main process
    worker.__dict__ = {}
    conn.send([caller_id, worker, results])


if __name__ == '__main__':
    import time
    from pyqode.core import QGenericCodeEdit, TextDecoration

    class Example(QGenericCodeEdit):

        addDecorationRequested = QtCore.Signal(str, int)

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.addDecorationRequested.connect(self.decorateLine)

        def showEvent(self, QShowEvent):
            QGenericCodeEdit.showEvent(self, QShowEvent)
            self.jobRunner = JobRunner(self, nbThreadsMax=3)
            self.jobRunner.startJob(self.xxx, False, "#FF0000", 0)
            self.jobRunner.startJob(self.xxx, False, "#00FF00", 10)
            self.jobRunner.startJob(self.xxx, False, "#0000FF", 20)

        def decorateLine(self, color, line):
            tc = self.textCursor()
            tc.setPosition(0)
            tc.movePosition(QtGui.QTextCursor.Down,
                            QtGui.QTextCursor.MoveAnchor,
                            line)
            d = TextDecoration(tc)
            d.setError(QtGui.QColor(color))
            d.setFullWidth(True)
            self.addDecoration(d)

        def xxx(self, color, offset):
            for i in range(10):
                line = i + offset
                print("Decorate line {0} with color {1} from a background "
                      "thread".format(line, color))
                self.addDecorationRequested.emit(color, line)
                time.sleep(0.1)
            if offset == 10:
                self.jobRunner.startJob(self.xxx, False, "#FF00FF", 30)
            print("Finished")

    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
