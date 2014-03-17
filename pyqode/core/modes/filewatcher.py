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
from pyqode.core.editor import Mode
from PyQt4 import QtCore, QtGui


class FileWatcherMode(Mode, QtCore.QObject):
    """
    FileWatcher mode, check if the opened file has changed externally.

    This mode adds the following properties to
    :attr:`pyqode.core.QCodeEdit.settings`

    """
    #: Mode identifier
    IDENTIFIER = "fileWatcherMode"
    #: Mode description
    DESCRIPTION = "Watch the editor's file and take care of the reloading."

    #: Signal emitted when the file has been deleted. The pyqtSignal is emitted
    #: with the current editor instance so that user have a chance to close
    #: the editor.
    fileDeleted = QtCore.pyqtSignal(object)

    @property
    def auto_reload_changed_files(self):
        return self.editor.settings.value("autoReloadChangedFiles")

    @auto_reload_changed_files.setter
    def auto_reload_changed_files(self, value):
        self.editor.settings.set_value("autoReloadChangedFiles", value)

    def __init__(self):
        QtCore.QObject.__init__(self)
        Mode.__init__(self)
        self._timer = QtCore.QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._check_mtime)
        self._mtime = 0
        self._notification_pending = False
        self._processing = False

    def _on_install(self, editor):
        """
        Adds autoReloadChangedFiles settings on install.
        """
        Mode._on_install(self, editor)
        self.editor.settings.add_property("autoReloadChangedFiles", False)

    def _on_state_changed(self, state):
        """
        Connects/Disconnects to the mouseWheelActivated and keyPressed event
        """
        if state is True:
            self._timer.start()
            self.editor.newTextSet.connect(self._update_mtime)
            self.editor.textSaved.connect(self._update_mtime)
            self.editor.textSaved.connect(self._timer.start)
            self.editor.textSaving.connect(self._timer.stop)
            self.editor.focusedIn.connect(self._check_for_pending)
        else:
            self._timer.stop()
            self.editor.newTextSet.disconnect(self._update_mtime)
            self.editor.textSaved.disconnect(self._update_mtime)
            self.editor.textSaved.disconnect(self._timer.start)
            self.editor.textSaving.disconnect(self._timer.stop)
            self.editor.focusedIn.disconnect(self._check_for_pending)

    def _update_mtime(self):
        try:
            self._mtime = os.path.getmtime(self.editor.file_path)
        except OSError:
            self._mtime = 0
            self._timer.stop()

    def _check_mtime(self):
        if self.editor is None:
            return
        if not self.editor.file_path:
            return
        if not os.path.exists(self.editor.file_path) and self._mtime:
            self._notify_deleted_file()
        else:
            mtime = os.path.getmtime(self.editor.file_path)
            if mtime > self._mtime:
                self._mtime = mtime
                self._notify_change()

    def __notify(self, settings_val, title, message, dlg_type=None,
                 expected_type=None, expected_action=None):
        """
        Notify user from external event
        """
        self._flg_notify = True
        dlg_type = (QtGui.QMessageBox.Yes |
                    QtGui.QMessageBox.No) if not dlg_type else dlg_type
        expected_type = QtGui.QMessageBox.Yes if not expected_type \
            else expected_type
        expected_action = (
            lambda *x: None) if not expected_action else expected_action
        auto = self.editor.settings.value(settings_val)
        if (auto or QtGui.QMessageBox.question(
                self.editor, title, message,
                dlg_type) == expected_type):
            expected_action(self.editor.file_path)
        self._update_mtime()

    def _notify_change(self):
        """
        Notify user from external change if autoReloadChangedFiles is False
        then reload the changed file in the editor
        """
        def inner_action(*a):
            self.editor.open_file(self.editor.file_path)

        args = ("autoReloadChangedFiles", "File changed",
                "The file <i>%s</i> has changed externally.\nDo you want to "
                "reload it?" % os.path.basename(self.editor.file_path))
        kwargs = {"expectedAction": inner_action}
        if self.editor.hasFocus():
            self.__notify(*args, **kwargs)
        else:
            self._notification_pending = True
            self._args = args
            self._kwargs = kwargs

    def _check_for_pending(self, *args, **kwargs):
        if self._notification_pending and not self._processing:
            self._processing = True
            self.__notify(*self._args, **self._kwargs)
            self._notification_pending = False
            self._processing = False

    def _notify_deleted_file(self):
        """
        Notify user from external file removal if autoReloadChangedFiles is
        False then reload the changed file in the editor
        """
        self.fileDeleted.emit(self.editor)
