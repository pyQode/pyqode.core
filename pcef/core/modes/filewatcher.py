
#!/bin/python
"""

"""
import hashlib
import os
import subprocess
import time
from pcef.core.system import JobRunner
from pcef.qt import QtCore, QtGui


class FileWatcher(QtCore.QObject):

    # TODO:

    def __init__(self, filePath, editor):
        self.jobRunner = JobRunner(self)
        self.jobRunner.startJob(
            self.compare, False, filePath, editor, self.onFileChange)

    def onFileChange(self):
        # TODO:
        print("Ooops... Son diferentes...")

    def compare(self, filePath, editor, callback, *args, **kwargs):
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
        while 1:
            with open(filePath, 'rb') as f:
                fileContent = f.read()
                fileContent = fileContent.replace(b"\r",b"")
            editorContent = str(
                editor.toPlainText()).encode()
            editorContent = editorContent.replace(b"\r",b"")
            originalSum = hashlib.md5(fileContent).hexdigest()
            editorSum = hashlib.md5(editorContent).hexdigest()
            if editorSum != originalSum:
                callback(*args, **kwargs)
            time.sleep(1)


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit, TextDecoration

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            fw = FileWatcher(__file__, self)

        def showEvent(self, QShowEvent):
            QGenericCodeEdit.showEvent(self, QShowEvent)

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
