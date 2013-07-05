"""
This module contains the definition of auxiliar classes for 
"""

from pcef.qt import QtGui, QtCore


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

    @staticmethod
    def stopJobThreadInstance(caller, method, *args, **kwargs):
        caller.invoker = Invoker()
        caller.invokeEvent = InvokeEvent(method, *args, **kwargs)
        QtCore.QCoreApplication.postEvent(caller.invoker, caller.invokeEvent)

    def stopJob(self):
        self.onFinish()
        self.terminate()

    def onFinish(self):
        pass

    def run(self):
        pass

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


@singleton
class JobRunner(JobThread):
    '''Class JobRunner, created to do a job and stop at anytime.
    Only one JobRunner can be executed, if user Force=True the actual JobRunner is stopped 
    and the new JobRunner is created.'''

    def __init__(self, callable, force, *args, **kwargs):
        JobThread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.callable = callable

    def run(self):
        self.callable(*self.args, **self.kwargs)


def stopJob(caller, job):
    '''function stopJob, created to stop a JobRunner at anytime.'''
    JobThread.stopJobThreadInstance(caller, job.stopJob)

def startJob(caller, callable, force, *a, **kw):
    '''function startJob, created to start a JobRunner.'''
    if force:
        actual = JobRunner(callable, force, *a, **kw)
        actual.__instances.pop(type(actual))
        stopJob(caller,actual)
    return JobRunner(callable, force, *a, **kw)






if __name__ == '__main__':

    class ventana(QtGui.QWidget):

        def __init__(self):
            QtGui.QWidget.__init__(self,parent=None)
            self.btn = QtGui.QPushButton(self)
            self.btn.setText("Stop Me!!!")
            QtCore.QObject.connect( self.btn, QtCore.SIGNAL( "clicked()" ), self.hola)
            ############################################
            self.hilo = startJob(self, self.xxx ,False)
            self.hilo.start()
            self.hilo = startJob(self, self.xxx ,True)
            self.hilo.start()
            ############################################

        def xxx(self):
            while 1:
                self.btn.setText(":O")
                time.sleep(1)
                self.btn.setText("Stop Me!!!")
                time.sleep(1)

        def hola(self):
            stopJob(self,self.hilo)
            self.btn.setText("I'm Stopped!!!")


    import sys
    app = QtGui.QApplication(sys.argv)
    v = ventana()
    v.show()
    sys.exit(app.exec_())

