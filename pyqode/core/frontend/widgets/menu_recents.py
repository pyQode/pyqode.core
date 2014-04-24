"""
Provides a menu that display the list of recent files and a RecentFilesManager
which use your application's QSettings to store the list of recent files.

"""
import os
from PyQt4 import QtCore, QtGui


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


class MenuRecentFiles(QtGui.QMenu):
    """
    Menu that manage the list of recent files.

    To use the menu, simply pass connect to the open_requested signal.

    """
    #: Signal emitted when the user clicked on a recent file action.
    #: The parameter is the path of the file to open.
    open_requested = QtCore.pyqtSignal(str)

    def __init__(self, recent_files_manager, parent, title='Recent files'):
        """
        :param organisation: name of your organisation as used for your own
                             QSettings
        :param application: name of your application as used for your own
                            QSettings
        :param parent: parent object
        """
        super().__init__(title, parent)
        #: Recent files manager
        self.manager = recent_files_manager
        #: List of recent files actions
        self.recent_files_actions = []
        self.update_actions()

    def update_actions(self):
        self.clear()
        self.recent_files_actions[:] = []
        for f in self.manager.get_recent_files():
            action = QtGui.QAction(self)
            action.setText(os.path.split(f)[1])
            action.setData(f)
            action.triggered.connect(self._on_action_triggered)
            self.addAction(action)
            self.recent_files_actions.append(action)
        self.addSeparator()
        action_clear = QtGui.QAction('Clear list', self)
        action_clear.triggered.connect(self._clear_recent_files)
        self.addAction(action_clear)

    def _clear_recent_files(self):
        self.manager.clear()
        self.update_actions()

    def _on_action_triggered(self):
        action = self.sender()
        assert isinstance(action, QtGui.QAction)
        path = action.data()
        self.open_requested.emit(path)
        self.update_actions()
