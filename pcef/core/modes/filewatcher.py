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
Contains the mode that control the external changes of file.
"""
import os
from pcef.core.mode import Mode
from pcef.qt import QtCore, QtGui


class FileWatcherMode(Mode):
    """
    FileWatcher mode. (Verify the external changes from opened file)
    """
    #: Mode identifier
    IDENTIFIER = "fileWatcherMode"
    #: Mode description
    DESCRIPTION = "Watch the editor's file and take care of the reloading."

    def __init__(self):
        super(FileWatcherMode, self).__init__()
        self.__fileSystemWatcher = QtCore.QFileSystemWatcher()
        self.__flgNotify = False
        self.__changeWaiting = False
        self.__fileSystemWatcher.fileChanged.connect(self.__onFileChanged)

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
        self.__changeWaiting = True
        if self.editor.hasFocus() and self.__flgNotify:
            self.__notifyChange()

    def __onEditorTextSaved(self, path):
        """
        Reconnect fileChanged signal after a short amount of time.
        """
        QtCore.QTimer.singleShot(100, self.__reconnectFileChanged)

    def __onEditorTextSaving(self, path):
        """
        Disconnect fileChanged signal to avoid notification when the file is
        saved by the pcef widget.
        """
        self.__fileSystemWatcher.fileChanged.disconnect(self.__onFileChanged)

    def __reconnectFileChanged(self):
        """
        Connects the fileChanged again
        """
        self.__fileSystemWatcher.fileChanged.connect(self.__onFileChanged)

    @QtCore.Slot()
    def __onEditorFilePathChanged(self):
        """
        Change the watched file
        """
        path = self.editor.filePath
        if len(self.__fileSystemWatcher.files()):
            self.__fileSystemWatcher.removePaths(
                self.__fileSystemWatcher.files())
        if path not in self.__fileSystemWatcher.files():
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
            self.editor.textSaved.connect(self.__onEditorTextSaved)
            self.editor.textSaving.connect(self.__onEditorTextSaving)
            self.editor.newTextSet.connect(self.__onEditorFilePathChanged)
            self.editor.focusedIn.connect(self.__onEditorFocusIn)
        else:
            self.editor.textSaved.disconnect(self.__onEditorTextSaved)
            self.editor.textSaving.connect(self.__onEditorTextSaving)
            self.editor.newTextSet.disconnect(self.__onEditorFilePathChanged)
            self.editor.focusedIn.disconnect(self.__onEditorFocusIn)
            self.__fileSystemWatcher.removePath(self.editor.filePath)


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit

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
