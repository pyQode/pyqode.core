# -*- coding: utf-8 -*-
"""
Contains the mode that control the external changes of file.
"""
import os
from pyqode.core import settings
from pyqode.core.frontend import Mode
from PyQt4 import QtCore, QtGui


class FileWatcherMode(Mode, QtCore.QObject):
    """
    FileWatcher mode, check if the opened file has changed externally.

    """
    #: Signal emitted when the file has been deleted. The pyqtSignal is emitted
    #: with the current editor instance so that user have a chance to close
    #: the editor.
    file_deleted = QtCore.pyqtSignal(object)

    @property
    def auto_reload(self):
        """
        Automatically reloads changed files
        """
        return self._auto_reload

    @auto_reload.setter
    def auto_reload(self, value):
        self._auto_reload = value

    def __init__(self):
        QtCore.QObject.__init__(self)
        Mode.__init__(self)
        self._timer = QtCore.QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._check_mtime)
        self._mtime = 0
        self._notification_pending = False
        self._processing = False
        self.refresh_settings()

    def refresh_settings(self):
        self._auto_reload = settings.file_watcher_auto_reload

    def _on_state_changed(self, state):
        """
        Connects/Disconnects to the mouse_wheel_activated and key_pressed event
        """
        if state is True:
            self._timer.start()
            self.editor.new_text_set.connect(self._update_mtime)
            self.editor.text_saved.connect(self._update_mtime)
            self.editor.text_saved.connect(self._timer.start)
            self.editor.text_saving.connect(self._timer.stop)
            self.editor.focused_in.connect(self._check_for_pending)
        else:
            self._timer.stop()
            self.editor.new_text_set.disconnect(self._update_mtime)
            self.editor.text_saved.disconnect(self._update_mtime)
            self.editor.text_saved.disconnect(self._timer.start)
            self.editor.text_saving.disconnect(self._timer.stop)
            self.editor.focused_in.disconnect(self._check_for_pending)

    def _update_mtime(self):
        try:
            self._mtime = os.path.getmtime(self.editor.file_path)
        except OSError:
            self._mtime = 0
            self._timer.stop()
        except TypeError:
            # file path is none, this happen if you use setPlainText instead of
            # openFile. This is perfectly fine, we just do not have anything to
            # watch
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

    def _notify(self, settings_val, title, message, dlg_type=None,
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
        if (self._auto_reload or QtGui.QMessageBox.question(
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
            self._notify(*args, **kwargs)
        else:
            self._notification_pending = True
            self._args = args
            self._kwargs = kwargs

    def _check_for_pending(self, *args, **kwargs):
        if self._notification_pending and not self._processing:
            self._processing = True
            self._notify(*self._args, **self._kwargs)
            self._notification_pending = False
            self._processing = False

    def _notify_deleted_file(self):
        """
        Notify user from external file removal if autoReloadChangedFiles is
        False then reload the changed file in the editor
        """
        self.file_deleted.emit(self.editor)
