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
Contains the mode that control the external changes of file.
"""
import os
from pyqode.core import logger
from pyqode.core.mode import Mode
from pyqode.qt import QtCore, QtGui


class FileWatcherMode(Mode):
    """
    FileWatcher mode. (Verify the external changes from opened file)

    This mode adds the following properties to :attr:`pyqode.core.QCodeEdit.settings`

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

    @property
    def autoReloadChangedFiles(self):
        return self.editor.settings.value("autoReloadChangedFiles")

    @autoReloadChangedFiles.setter
    def autoReloadChangedFiles(self, value):
        self.editor.settings.setValue("autoReloadChangedFiles", value)

    def __init__(self):
        super(FileWatcherMode, self).__init__()
        self.__fileSystemWatcher = QtCore.QFileSystemWatcher()
        self.__flgNotify = False
        self.__changeWaiting = False

    def __notifyChange(self):
        """
        Notify user from external change if autoReloadChangedFiles is False then
        reload the changed file in the editor
        """
        self.__flgNotify = True
        auto = self.editor.settings.value("autoReloadChangedFiles")
        if (auto or QtGui.QMessageBox.question(
                self.editor, "File changed",
                "The file <i>%s</i> has has changed externally.\n"
                "Do you want reload it?" % os.path.basename(
                    self.editor.filePath),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) ==
                QtGui.QMessageBox.Yes):
            self.editor.openFile(self.editor.filePath)
        self.__changeWaiting = False
        self.__flgNotify = False

    def __onFileChanged(self, path):
        """
        On file changed, notify the user if we have focus, otherwise delay the
        notification to the focusIn event
        """
        content, encoding = self.editor.readFile(
            path, encoding=self.editor.fileEncoding)
        if content == self.editor.toPlainText():
            logger.debug("FileWatcherMode: Internal change, skipping")
            return
        self.__changeWaiting = True
        if self.editor.hasFocus() and self.__flgNotify:
            self.__notifyChange()

    @QtCore.Slot()
    def __onEditorFilePathChanged(self):
        """
        Change the watched file
        """
        path = self.editor.filePath
        if len(self.__fileSystemWatcher.files()):
            self.__fileSystemWatcher.removePaths(
                self.__fileSystemWatcher.files())
        if path and path not in self.__fileSystemWatcher.files():
            self.__fileSystemWatcher.addPath(path)

    @QtCore.Slot()
    def __onEditorFocusIn(self):
        """
        Notify if there are pending changes
        """
        if self.__changeWaiting:
            self.__notifyChange()

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
            # self.editor.textSaved.connect(self.__onEditorTextSaved)
            # self.editor.textSaving.connect(self.__onEditorTextSaving)
            self.__fileSystemWatcher.fileChanged.connect(self.__onFileChanged)
            self.editor.newTextSet.connect(self.__onEditorFilePathChanged)
            self.editor.focusedIn.connect(self.__onEditorFocusIn)
        else:
            # self.editor.textSaved.disconnect(self.__onEditorTextSaved)
            # self.editor.textSaving.connect(self.__onEditorTextSaving)
            self.editor.newTextSet.disconnect(self.__onEditorFilePathChanged)
            self.editor.focusedIn.disconnect(self.__onEditorFocusIn)
            self.__fileSystemWatcher.removePath(self.editor.filePath)
            self.__fileSystemWatcher.fileChanged.disconnect(self.__onFileChanged)


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
