#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains utility functions
"""
import glob
import os
import sys
import logging
import weakref
import pcef
from pcef.qt import QtCore, QtGui


def findSettingsDirectory(appName="PCEF"):
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

    def __str__(self):
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
        if tokens[1] == "underlined":
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

    def __del__(self):
        print("_JobThread deleted")

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
            raise Exception("Executing not callable statement")


class JobRunner:
    """
    Utility class to easily run an asynchroneous job. A job is a simple callable
    (method) that will be run in a background thread.

    JobRunner implements a job queue to ensure there is only one job running per
    JobRunner instance. If a job is already running, the new job will wait for
    the current job to finish unless you want to force its execution. It that
    case the current job will be terminated.

    Additional parameters can be supplied to the job using *args and
    **kwargs.

    Usage
    ------------
    self.jobRunner = JobRunner(self)
    self.jobRunner.startJob(self.aJobMethod, False, arg1, ... , arg1=kwarg1 , ...)
    """
    @property
    def caller(self):
        return self.__caller()

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

    def __del__(self):
        print("JobRunner del")

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

        :param force: Specify if we must force the job execution by stopping the
        job that is currently running (if any).
        :type force: bool

        :param args: *args
        :param kwargs: **kwargs
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
            logging.getLogger("pcef").debug(
                "Failed to queue job. All threads are used")
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


if __name__ == '__main__':
    import time
    from pcef.core import QGenericCodeEdit, TextDecoration

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))

        def __del__(self):
            print("Editor del")

        def showEvent(self, QShowEvent):
            QGenericCodeEdit.showEvent(self, QShowEvent)
            self.jobRunner = JobRunner(self, nbThreadsMax=3)
            self.jobRunner.startJob(self.xxx, False, "#FF0000", 0)
            self.jobRunner.startJob(self.xxx, False, "#00FF00", 10)
            self.jobRunner.startJob(self.xxx, False, "#0000FF", 20)

        def xxx(self, color, offset):
            for i in range(10):
                print(color)
                tc = self.textCursor()
                tc.setPosition(0)
                tc.movePosition(QtGui.QTextCursor.Down,
                                QtGui.QTextCursor.MoveAnchor,
                                i + offset)
                d = TextDecoration(tc)
                d.setError(QtGui.QColor(color))
                d.setFullWidth(True)
                self.addDecoration(d)
                time.sleep(0.1)
            if offset == 10:
                self.jobRunner.startJob(self.xxx, False, "#FF00FF", 30)
            print("Finished")

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
