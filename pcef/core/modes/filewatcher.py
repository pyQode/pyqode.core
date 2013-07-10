
#!/bin/python
"""
module test...
"""
import hashlib
import os
import subprocess
import time
from pcef.core.system import JobRunner
from pcef.qt import QtCore, QtGui
from pcef.core import constants
from pcef.core.mode import Mode


class FileWatcher(Mode):

    """"""

    #: Mode identifier
    IDENTIFIER = "FileWatcher"
    #: Mode description
    DESCRIPTION = "Verify if file is modified externally."

    def __init__(self):
        super(FileWatcher, self).__init__()
        self.jobRunner = JobRunner(self)
        self.__textSum = ""
        self.__notify = True

    def onFileChange(self):
        # TODO: put i18n for this method
        self.__notify = False
        msgBox = QtGui.QMessageBox(self.editor)
        msgBox.setText("The document has been modified")
        msgBox.setInformativeText("Do you want reload it?")
        msgBox.setStandardButtons(
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msgBox.setDefaultButton(QtGui.QMessageBox.No)
        ret = msgBox.exec_()
        if ret == QtGui.QMessageBox.Save:
            self.editor.openFile(self.editor.filePath)
        self.__notify = True

    @QtCore.Slot()
    def __setOriginalTextSum(self):
        editorContent = str(
            self.editor.toPlainText()).encode()
        self.__textSum = hashlib.md5(editorContent).hexdigest()

    def onStateChanged(self, state):
        """
        Connects/Disconnects to the mouseWheelActivated and keyPressed event
        """
        if state is True:
            self.editor.textSaved.connect(self.__setOriginalTextSum)
            self.editor.newTextSet.connect(self.__setOriginalTextSum)
            self.jobRunner.startJob(
                self.__compare, False, self.onFileChange)
            Mode.install(self, self.editor)
        else:
            self.jobRunner.stopJob()

    def __compare(self, callback, *args, **kwargs):
        """
        This function return the md5sum of file


        :param filePath: filePath.
        :type filePath: str

        :param editor: editor.
        :type editor: QTextEdit

        :param callback: callback.
        :type callback: callable

        :param args: *args
        :param kwargs: **kwargs
        """
        editor = self.editor
        while True:
            filePath = self.editor.filePath
            if filePath and self.__notify:
                with open(filePath, 'rb') as f:
                    fileContent = f.read()
                    fileContent = fileContent.replace(b"\r", b"")
                originalSum = hashlib.md5(fileContent).hexdigest()
                if self.__textSum != '' and self.__textSum != originalSum:
                    callback(*args, **kwargs)
            time.sleep(1)


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit, TextDecoration

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.installMode(FileWatcher())
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))

        def closeEvent(self, evt):
            print("closing")
            self.uninstallMode(FileWatcher)

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
