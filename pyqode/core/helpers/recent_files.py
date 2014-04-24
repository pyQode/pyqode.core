# -*- coding: utf-8 -*-
"""
This module contains an helper class to manage the list of recent files
in an IDE.
"""
import os
from PyQt4 import QtCore


class RecentFilesManager:
    """
    Manages a list of recent files. The list of files is stored in your
    application QSettings.

    """
    #: Maximum number of files kept in the list.
    max_recent_files = 5

    def __init__(self, organisation, application):
        self._settings = QtCore.QSettings(organisation, application)

    def clear(self):
        self._settings.setValue('recentFiles', [])

    def get_recent_files(self):
        """
        Gets the list of recent files. (files that do not exists anymore
        are automatically filtered)
        """
        ret_val = []
        files = self._settings.value('recentFiles', [])
        # empty list
        if files is None:
            files = []
        # single file
        if isinstance(files, str):
            files = [files]
        # filter files, remove files that do not exist anymore
        for f in files:
            if os.path.exists(f):
                ret_val.append(f)
        return ret_val

    def open_file(self, file):
        """
        Adds a file to the list (and move it to the top of the list if the
        file already exists)

        """
        files = self.get_recent_files()
        try:
            files.remove(file)
        except ValueError:
            pass
        files.insert(0, file)
        # discard old files
        del files[self.max_recent_files:]
        self._settings.setValue('recentFiles', files)


if __name__ == '__main__':
    manager = RecentFilesManager('pyqode', 'test')
    manager.clear()
    print(manager.get_recent_files())
    manager.open_file(__file__)
    print(manager.get_recent_files())
    manager.open_file(QtCore.__file__)
    print(manager.get_recent_files())
    manager.open_file(os.__file__)
    print(manager.get_recent_files())
    manager.open_file(__file__)
    print(manager.get_recent_files())
