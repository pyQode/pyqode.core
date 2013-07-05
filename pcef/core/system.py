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
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def find_subpackages(pkgpath):
    import pkgutil
    for itm in pkgutil.iter_modules([pkgpath]):
        print(itm)





class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

class Invoker(QtCore.QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)
        return True



class JobThread(QtCore.QThread):
    '''Class for implement a thread, can be used and stoppen in any moment.
        * extend and override the run method and if you want onFinish
    '''

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.__jobResults = None
        self.args = ()
        self.kwargs = {}

    @staticmethod
    def stopJobThreadInstance(caller, method, *args, **kwargs):
        caller.invoker = Invoker()
        caller.invokeEvent = InvokeEvent(method, *args, **kwargs)
        QtCore.QCoreApplication.postEvent(caller.invoker, caller.invokeEvent)

    def stopRun(self):
        self.onFinish()
        self.terminate()

    def setMethods(self, onRun, onFinish):
        self.executeOnRun = onRun
        self.executeOnFinish = onFinish

    def setParameters(self, *a, **kw):
        self.args = a
        self.kwargs = kw

    def onFinish(self):
        if hasattr(self,"executeOnFinish") and self.executeOnFinish and hasattr(self.executeOnFinish, '__call__'):
            self.executeOnFinish()

    def run(self):
        if hasattr(self,"executeOnRun") and self.executeOnRun and hasattr(self.executeOnRun, '__call__'):
            self.executeOnRun( *self.args, **self.kwargs )
        else:
            raise Exception("Executing not callable statement")

    @property
    def jobResults(self):
        return self.__jobResults

    @jobResults.setter
    def jobResults(self, value):
        self.__jobResults = value

    @jobResults.deleter
    def jobResults(self, value):
        self.__jobResults = value


def singleton(class_):
    ''' Class implemented to have a unique instance of a JobRunner. 
    TODO: test in Python 2.X '''
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
            instances[class_].__instances = instances
        return instances[class_]
    return getinstance


class JobRunner:
    '''Class JobRunner, created to do a job and stop at anytime.
    If user Force=True the actual JobRunner is stopped 
    and the new JobRunner is created.'''

    def __init__(self, caller):
        self.thread = JobThread()
        self.caller = caller

    def startJob(self, callable, force, *args, **kwargs):
        '''function startJob, created to start a JobRunner.'''
        if force:
            self.thread.stopJob(self)
            del(self.thread)
            self.thread = JobThread()
        self.thread.setMethods(callable, None) # TODO: verify if onFinish is useful
        self.thread.setParameters(*args, **kwargs)
        self.thread
        self.thread.start()

    def stopJob(self):
        '''function stopJob, created to stop a JobRunner at anytime.'''
        JobThread.stopJobThreadInstance(self.caller, self.thread.stopRun)




if __name__ == '__main__':
    import time
    class ventana(QtGui.QWidget):

        def __init__(self):
            QtGui.QWidget.__init__(self,parent=None)
            self.btn = QtGui.QPushButton(self)
            self.btn.setText("Stop Me!!!")
            QtCore.QObject.connect( self.btn, QtCore.SIGNAL( "clicked()" ), self.hola)
            ############################################
            self.hilo = JobRunner(self)
            self.hilo.startJob(self.xxx ,False, 'Stop')
            ############################################

        def xxx(self, action):
            while 1:
                self.btn.setText(":O")
                time.sleep(1)
                self.btn.setText("{} Me!!!".format(action))
                time.sleep(1)

        def hola(self):
            self.hilo.stopJob()
            self.btn.setText("Thanks!!!")


    import sys
    app = QtGui.QApplication(sys.argv)
    v = ventana()
    v.show()
    sys.exit(app.exec_())

