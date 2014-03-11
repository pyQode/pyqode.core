#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""
Contains the mode that control the external changes of file.
"""
import os
from pyqode.core import logger
from pyqode.core.mode import Mode
from pyqode.qt import QtCore, QtGui


class FileWatcherMode(Mode, QtCore.QObject):
    """
    FileWatcher mode, check if the opened file has changed externally.

    This mode adds the following properties to
    :attr:`pyqode.core.QCodeEdit.settings`

    ====================== ====================== ======= ====================== ================
    Key                    Section                Type    Default value          Description
    ====================== ====================== ======= ====================== ================
    autoReloadChangedFiles General                bool    False                  Auto reload files that changed externally.
    ====================== ====================== ======= ====================== ================
    """
    #: Mode identifier
    IDENTIFIER = "fileWatcherMode"
    #: Mode description
    DESCRIPTION = "Watch the editor's file and take care of the reloading."

    #: Signal emitted when the file has been deleted. The signal is emitted
    #: with the current editor instance so that user have a chance to close
    #: the editor.
    fileDeleted = QtCore.Signal(object)

    @property
    def autoReloadChangedFiles(self):
        return self.editor.settings.value("autoReloadChangedFiles")

    @autoReloadChangedFiles.setter
    def autoReloadChangedFiles(self, value):
        self.editor.settings.setValue("autoReloadChangedFiles", value)

    def __init__(self):
        QtCore.QObject.__init__(self)
        Mode.__init__(self)
        self._timer = QtCore.QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._checkModTime)
        self._mtime = 0
        self._notificationPending = False
        self._processing = False

    def _onInstall(self, editor):
        """
        Adds autoReloadChangedFiles settings on install.
        """
        Mode._onInstall(self, editor)
        self.editor.settings.addProperty("autoReloadChangedFiles", False)

    def _onStateChanged(self, state):
        """
        Connects/Disconnects to the mouseWheelActivated and keyPressed event
        """
        if state is True:
            self._timer.start()
            self.editor.newTextSet.connect(self._updateModTime)
            self.editor.textSaved.connect(self._updateModTime)
            self.editor.textSaved.connect(self._timer.start)
            self.editor.textSaving.connect(self._timer.stop)
            self.editor.focusedIn.connect(self._checkForPendingNotification)
        else:
            self._timer.stop()
            self.editor.newTextSet.disconnect(self._updateModTime)
            self.editor.textSaved.disconnect(self._updateModTime)
            self.editor.textSaved.disconnect(self._timer.start)
            self.editor.textSaving.disconnect(self._timer.stop)
            self.editor.focusedIn.disconnect(self._checkForPendingNotification)

    def _updateModTime(self):
        try:
            self._mtime = os.path.getmtime(self.editor.filePath)
        except OSError:
            self._mtime = 0
            self._timer.stop()

    def _checkModTime(self):
        if self.editor is None:
            return
        if not self.editor.filePath:
            return
        if not os.path.exists(self.editor.filePath) and self._mtime:
            self.__notifyDeletedFile()
        else:
            mtime = os.path.getmtime(self.editor.filePath)
            if mtime > self._mtime:
                self._mtime = mtime
                self.__notifyChange()

    def __notify(self, settingsValue, title, message, dialogType=None,
                 expectedType=None, expectedAction=None):
        """
        Notify user from external event
        """
        self.__flgNotify = True
        dialogType = (QtGui.QMessageBox.Yes |
                      QtGui.QMessageBox.No) if not dialogType else dialogType
        expectedType = QtGui.QMessageBox.Yes if not expectedType else expectedType
        expectedAction = (
            lambda *x: None) if not expectedAction else expectedAction
        auto = self.editor.settings.value(settingsValue)
        if (auto or QtGui.QMessageBox.question(
                self.editor, title, message,
                dialogType) == expectedType):
            expectedAction(self.editor.filePath)
        self._updateModTime()

    def __notifyChange(self):
        """
        Notify user from external change if autoReloadChangedFiles is False then
        reload the changed file in the editor
        """
        def innerAction(*a):
            self.editor.openFile(self.editor.filePath)

        args = ("autoReloadChangedFiles", "File changed",
                "The file <i>%s</i> has changed externally.\nDo you want to "
                "reload it?" % os.path.basename(self.editor.filePath))
        kwargs = {"expectedAction": innerAction}
        if self.editor.hasFocus():
            self.__notify(*args, **kwargs)
        else:
            self._notificationPending = True
            self._args = args
            self._kwargs = kwargs

    def _checkForPendingNotification(self, *args, **kwargs):
        if self._notificationPending and not self._processing:
            self._processing = True
            self.__notify(*self._args, **self._kwargs)
            self._notificationPending = False
            self._processing = False


    def __notifyDeletedFile(self):
        """
        Notify user from external file removal if autoReloadChangedFiles is False then
        reload the changed file in the editor
        """
        self.fileDeleted.emit(self.editor)


if __name__ == '__main__':
    from pyqode.core import QGenericCodeEdit

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.installMode(FileWatcherMode())
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
