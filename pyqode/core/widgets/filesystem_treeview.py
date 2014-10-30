"""
This module contains the file system tree view.
"""
import logging
import os
import shutil
from pyqode.qt import QtCore, QtGui, QtWidgets


def _logger():
    return logging.getLogger(__name__)


class FilterProxyModel(QtCore.QSortFilterProxyModel):
    """
    Excludes ``ignored_directories`` and ``ignored_extensions`` from the file
    system model
    """
    def __init__(self):
        super().__init__()
        #: The list of directories to exclude
        self.ignored_directories = ['__pycache__', 'build', 'dist']
        #: The list of file extension to exclude
        self.ignored_extensions = ['.pyc', '.pyd', '.so', '.dll', '.exe',
                                   '.egg-info', '.coverage']

    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        Filters model indices based on the list of ``ignored_directories``
        and ``ignored_extensions``.
        """
        index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
        finfo = self.sourceModel().fileInfo(index0)
        fn = finfo.fileName()
        extension = '.%s' % finfo.suffix()
        if fn in self.ignored_directories:
            _logger().debug('excluding directory: %s', finfo.filePath())
            return False
        if extension in self.ignored_extensions:
            _logger().debug('excluding file: %s', finfo.filePath())
            return False
        _logger().debug('accepting %s', finfo.filePath())
        return True


class FileSystemTreeView(QtWidgets.QTreeView):
    """
    Extends QtWidgets.QTreeView with a filterable file system model.

    To exclude directories or extension, just set
    :attr:`FilterProxyModel.ignored_directories` and
    :attr:`FilterProxyModel.ignored_extensions`.

    Provides methods to retrieve file info from model index.

    .. note:: There is no context menu for copying/moving files, and so on as
        this is usually application specific.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fs_model_source = QtWidgets.QFileSystemModel()
        self.fs_model_proxy = FilterProxyModel()
        self.fs_model_proxy.setSourceModel(self.fs_model_source)
        self.setModel(self.fs_model_proxy)
        self.context_menu = None
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def add_to_ignored_directories(self, *directories):
        """
        Adds the specified directories to the list of ignored directories.

        This must be done before calling set_root_path!

        :param directories: the directories to ignore
        """
        for d in directories:
            self.fs_model_proxy.ignored_directories.append(d)

    def add_to_ignored_extensions(self, *extensions):
        """
        Adds the specified extensions to the list of ignored directories.

        This must be done before calling set_root_path!

        :param extensions: the extensions to ignore

        .. note:: extension must have the dot: '.py' and not 'py'
        """
        for d in extensions:
            self.fs_model_proxy.ignored_extensions.append(d)

    def set_context_menu(self, context_menu):
        self.context_menu = context_menu
        self.context_menu.tree_view = self
        for action in self.context_menu.actions():
            self.addAction(action)

    def set_root_path(self, path):
        """
        Sets the root path to watch
        :param path: root path - str
        """
        if os.path.isfile(path):
            path = os.path.abspath(os.path.join(path, os.pardir))
        index = self.fs_model_source.setRootPath(path)
        root_index = self.fs_model_proxy.mapFromSource(index)
        self.setRootIndex(root_index)

    def filePath(self, index):
        """
        Gets the file path of the item at the specified ``index``.

        :param index: item index - QModelIndex
        :return: str
        """
        return self.fs_model_source.filePath(self.fs_model_proxy.mapToSource(index))

    def fileInfo(self, index):
        """
        Gets the file info of the item at the specified ``index``.

        :param index: item index - QModelIndex
        :return: QFileInfo
        """
        return self.fs_model_source.fileInfo(self.fs_model_proxy.mapToSource(index))

    def _show_context_menu(self, point):
        if self.context_menu:
            self.context_menu.exec_(self.mapToGlobal(point))


class UrlListMimeData(QtCore.QMimeData):
    def __init__(self, copy=True):
        super().__init__()
        self.copy = copy

    def set_list(self, urls):
        lst = []
        for url in urls:
            lst.append(url)
        self.setData(self.format(self.copy), '\n'.join(lst))

    @classmethod
    def list_from(cls, mime_data, copy=True):
        string = bytes(mime_data.data(cls.format(copy))).decode('utf-8')
        lst = string.split('\n')
        urls = []
        for val in lst:
            urls.append(val)
        return urls

    def formats(self):
        return [self.format(self.copy)]

    @classmethod
    def format(cls, copy=True):
        return 'text/tv-copy-url-list' if copy else 'text/tv-cut-url-list'


class FileSystemContextMenu(QtWidgets.QMenu):
    """
    Default context menu for the file system treeview.

    This context menu contains the following actions:
        - Copy
        - Cut
        - Paste
        - Delete
        - Copy path

    .. note:: copy/cut/paste action works only from inside the application
        (e.g. you cannot paste what you copied in the app to the explorer)

    """

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.source = None

        def _icon(theme, rc_path):
            return QtGui.QIcon.fromTheme(theme, QtGui.QIcon(rc_path))

        self.action_copy = QtWidgets.QAction('Copy', self)
        self.action_copy.setShortcut(QtGui.QKeySequence.Copy)
        self.action_copy.setIcon(_icon(
            'edit-copy', ':/pyqode-icons/rc/edit-copy.png'))
        self.addAction(self.action_copy)
        self.action_copy.triggered.connect(self._on_copy_triggered)

        # cut
        self.action_cut = QtWidgets.QAction('Cut', self)
        self.action_cut.setShortcut(QtGui.QKeySequence.Cut)
        self.action_cut.setIcon(_icon(
            'edit-cut', ':/pyqode-icons/rc/edit-cut.png'))
        self.addAction(self.action_cut)
        self.action_cut.triggered.connect(self._on_cut_triggered)

        # Paste
        self.action_paste = QtWidgets.QAction('Paste', self)
        self.action_paste.setShortcut(QtGui.QKeySequence.Paste)
        self.action_paste.setIcon(_icon(
            'edit-paste', ':/pyqode-icons/rc/edit-paste.png'))
        self.action_paste.triggered.connect(self._paste_from_clipboard)
        self.addAction(self.action_paste)

        # Delete
        self.action_delete = QtWidgets.QAction('Delete', self)
        self.action_delete.setShortcut(QtGui.QKeySequence.Delete)
        self.action_delete.setIcon(_icon(
            'edit-delete', ':/pyqode-icons/rc/edit-delete.png'))
        self.action_delete.triggered.connect(self._on_delete_triggered)
        self.addAction(self.action_delete)

        # Copy file path
        self.addSeparator()
        self.action_copy_path = QtWidgets.QAction('Copy path', self)
        self.addAction(self.action_copy_path)
        self.action_copy_path.triggered.connect(self._copy_path)

    def _on_copy_triggered(self):
        self._copy_to_clipboard()

    def _on_cut_triggered(self):
        self._copy_to_clipboard(copy=False)

    def _copy_to_clipboard(self, copy=True):
        urls = self._selected_urls()
        if not urls:
            return
        mime = UrlListMimeData(copy)
        mime.set_list(urls)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setMimeData(mime)

    def _selected_urls(self):
        urls = []
        _logger().debug('gettings urls')
        for proxy_index in self.tree_view.selectedIndexes():
            finfo = self.tree_view.fileInfo(proxy_index)
            urls.append(finfo.canonicalFilePath())
        _logger().info('selected urls %r' % [str(url) for url in urls])
        return urls

    def _paste_from_clipboard(self):
        to = self.tree_view.fileInfo(self.tree_view.currentIndex()).filePath()
        if os.path.isfile(to):
            to = os.path.abspath(os.path.join(to, os.pardir))
        mime = QtWidgets.QApplication.clipboard().mimeData()

        paste_operation = None
        if mime.hasFormat(UrlListMimeData.format(copy=True)):
            paste_operation = True
        elif mime.hasFormat(UrlListMimeData.format(copy=False)):
            paste_operation = False
        if paste_operation is not None:
            self.paste(
                UrlListMimeData.list_from(mime, copy=paste_operation), to,
                copy=paste_operation)

    def paste(self, sources, destination, copy):
        for src in sources:
            _logger().info('%s <%s> to <%s>' % (
                'copying' if copy else 'cutting', src, destination))
            perform_copy = True
            final_dest = os.path.join(destination, os.path.split(src)[1])
            if os.path.exists(final_dest):
                rep = QtWidgets.QMessageBox.question(
                    self.tree_view, 'File exists',
                    'File <%s> already exists. Do you want to erase it?' %
                    final_dest,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No)
                if rep == QtWidgets.QMessageBox.No:
                    perform_copy = False
            if not perform_copy:
                continue
            try:
                shutil.copy(src, destination)
            except (IOError, OSError) as e:
                QtWidgets.QMessageBox.warning(
                    self.tree_view, 'Failed to copy file', str(e))
                _logger().exception('failed to copy %s to %s', src,
                                    destination)
            else:
                _logger().info('file copied %s', src)
            if not copy:
                _logger().info('removing source (cut operation)')
                os.remove(src)

    def _on_delete_triggered(self):
        urls = self._selected_urls()
        rep = QtWidgets.QMessageBox.question(
            self.tree_view, 'Confirm delete',
            'Are you sure about deleting the selected files?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes)
        if rep == QtWidgets.QMessageBox.Yes:
            for fn in urls:
                try:
                    os.remove(fn)
                except OSError as e:
                    QtWidgets.QMessageBox.warning(
                        self.tree_view, 'Failed to remove %s' % fn, str(e))
                    _logger().exception('failed to remove %s', fn)
                else:
                    _logger().info('%s removed', fn)

    def _copy_path(self):
        path = self.tree_view.fileInfo(
            self.tree_view.currentIndex()).filePath()
        QtWidgets.QApplication.clipboard().setText(path)
        _logger().info('path copied: %s' % path)
