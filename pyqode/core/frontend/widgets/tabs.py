# -*- coding: utf-8 -*-
"""
This module contains the implementation of a tab widget specialised to
show code editor tabs.
"""
import logging
import os
import sys
import pyqode.core
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDialog, QTabBar, QTabWidget

from pyqode.core import frontend
from pyqode.core.frontend.ui.dlg_unsaved_files_ui import Ui_Dialog
from pyqode.core.frontend.modes import FileWatcherMode


def _logger():
    return logging.getLogger(__name__)


class DlgUnsavedFiles(QDialog, Ui_Dialog):
    """
    This dialog shows the list of unsaved file in the CodeEditTabWidget.

    Use can choose to:
        - cancel: nothing changed, no tab will be closed
        - save all/save selected: save the selected files or all files
        - discard all changes: nothing will be saved but all tabs will be
        closed.

    """
    def __init__(self, parent, files=None):
        if files is None:
            files = []
        QtGui.QDialog.__init__(self, parent)
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.bt_save_all = self.buttonBox.button(
            QtGui.QDialogButtonBox.SaveAll)
        self.bt_save_all.clicked.connect(self.accept)
        self.discarded = False
        self.bt_discard = self.buttonBox.button(QtGui.QDialogButtonBox.Discard)
        self.bt_discard.clicked.connect(self._set_discarded)
        self.bt_discard.clicked.connect(self.accept)
        for f in files:
            self._add_file(f)
        self.listWidget.itemSelectionChanged.connect(
            self._on_selection_changed)
        self._on_selection_changed()

    def _add_file(self, filePath):
        icon = QtGui.QFileIconProvider().icon(QtCore.QFileInfo(filePath))
        item = QtGui.QListWidgetItem(icon, filePath)
        self.listWidget.addItem(item)

    def _set_discarded(self):
        self.discarded = True

    def _on_selection_changed(self):
        nbItems = len(self.listWidget.selectedItems())
        if nbItems == 0:
            self.bt_save_all.setText("Save")
            self.bt_save_all.setEnabled(False)
        else:
            self.bt_save_all.setEnabled(True)
            self.bt_save_all.setText("Save selected")
            if nbItems == self.listWidget.count():
                self.bt_save_all.setText("Save all")


class ClosableTabBar(QTabBar):
    """
    Custom QTabBar that can be closed using a mouse middle click.
    """
    def __init__(self, parent):
        QtGui.QTabBar.__init__(self, parent)
        self.setTabsClosable(True)

    def mousePressEvent(self, qMouseEvent):
        QtGui.QTabBar.mousePressEvent(self, qMouseEvent)
        if qMouseEvent.button() == QtCore.Qt.MiddleButton:
            self.parentWidget().tabCloseRequested.emit(self.tabAt(
                qMouseEvent.pos()))


class TabWidget(QTabWidget):
    """
    QTabWidget specialised to hold CodeEdit instances (or any other
    object that has the same interace).

    It ensures that there is only one open editor tab for a specific file path,
    it adds a few utility methods to quickly manipulate the current editor
    widget.

    It handles tab close requests automatically and show a dialog box when
    a dirty tab widget is being closed. It also adds a convenience QTabBar
    with a "close", "close others" and "close all" menu. (You can add custom
    actions by using the addAction and addSeparator methods).

    It exposes a variety of signal and slots for a better integration with
    your applications( dirty_changed, save_current, save_all, close_all,
    close_current, close_others).

    """
    #: Signal emitted when a tab dirty flag changed
    dirty_changed = QtCore.pyqtSignal(bool)
    #: Signal emitted when the last tab has been closed
    last_tab_closed = QtCore.pyqtSignal()
    #: Signal emitted when a tab has been closed
    tab_closed = QtCore.pyqtSignal(QtGui.QWidget)

    @property
    def active_editor(self):
        """
        Returns the current editor widget or None if the current tab widget is
        not a subclass of CodeEdit or if there is no open tab.
        """
        return self._current

    def __init__(self, parent):
        QtGui.QTabWidget.__init__(self, parent)
        self._current = None
        self.currentChanged.connect(self._on_current_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        tab_bar = ClosableTabBar(self)
        tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._show_tab_context_menu)
        self.setTabBar(tab_bar)
        self.tab_bar = tab_bar
        self._context_mnu = QtGui.QMenu()
        for name, slot in [('Close', self.close),
                           ('Close others', self.close_others),
                           ('Close all', self.close_all)]:
            a = QtGui.QAction(name, self)
            a.triggered.connect(slot)
            self._context_mnu.addAction(a)
            self.addAction(a)
        # keep a list of widgets (to avoid PyQt bug where
        # the C++ class loose the wrapped obj type).
        self._widgets = []

    @QtCore.pyqtSlot()
    def close(self):
        """
        Closes the active editor
        """
        self.tabCloseRequested.emit(self.currentIndex())

    @QtCore.pyqtSlot()
    def close_others(self):
        """
        Closes every editors tabs except the current one.
        """
        cw = self.currentWidget()
        self._try_close_dirty_tabs(exept=cw)
        i = 0
        while self.count() > 1:
            w = self._widgets[i]
            if w != cw:
                self.removeTab(i)
            else:
                i = 1

    @QtCore.pyqtSlot()
    def close_all(self):
        """
        Closes all editors
        """
        if self._try_close_dirty_tabs():
            while self.count():
                widget = self._widgets[0]
                self.removeTab(0)
                self.tab_closed.emit(widget)
            return True
        return False

    @QtCore.pyqtSlot()
    def save_current(self, path=None):
        """
        Save current editor content.

        To save the file as, you just need to specify a path.

        """
        try:
            if not path and not self._current.file_path:
                path = QtGui.QFileDialog.getSaveFileName(
                    self, 'Choose destination path')
                if not path:
                    return False
            frontend.save_to_file(self._current, path)
            # adapt tab title on save as
            if path:
                self.setTabText(self.currentIndex(),
                                QtCore.QFileInfo(path).fileName())
            return True
        except AttributeError:  # not an editor widget
            pass
        return False

    @QtCore.pyqtSlot()
    def save_all(self):
        """
        Save all editors.
        """
        for i in range(self.count()):
            try:
                code_edit = self.widget(i)
                self._save_editor(code_edit)
                self.setTabText(i, code_edit._tab_name)
            except AttributeError:
                pass

    def addAction(self, action):
        """
        Adds an action to the TabBar context menu

        :param action: QAction to add
        """
        self._context_mnu.addAction(action)

    def addSeparator(self):
        """
        Adds a separator to the TabBar context menu.

        :returns The separator action.
        """
        return self._context_mnu.addSeparator()

    def index_from_filename(self, path):
        """
        Checks if the path is already open in an editor tab.

        :returns: The tab index if found or -1
        """
        if path:
            for i, widget in enumerate(self._widgets):
                try:
                    if widget.file_path == path:
                        return i
                except AttributeError:
                    pass  # not an editor widget
        return -1

    def _del_code_edit(self, code_edit):
        frontend.stop_server(code_edit)
        code_edit.deleteLater()
        del code_edit

    def add_code_edit(self, code_edit, name=None, icon=None):
        """
        Adds a code edit tab, sets its text as the editor.file_name and
        sets it as the active tab.

        The widget is only added if there is no other editor tab open with the
        same filename, else the already open tab is set as current.

        :param code_edit: The code editor widget tab to add
        :type code_edit: pyqode.core.frontend.CodeEdit

        :param icon: The tab widget icon. Optional
        :type icon: QtGui.QIcon or None
        """
        index = self.index_from_filename(code_edit.file_path)
        if index != -1:
            # already open, just show it
            self.setCurrentIndex(index)
            # no need to keep this instance
            self._del_code_edit(code_edit)
            return
        if not icon:
            icon = QtGui.QFileIconProvider().icon(
                QtCore.QFileInfo(code_edit.file_path))
        file_name = code_edit.file_name
        if name or not file_name:
            file_name = name
        assert file_name, 'You need to set the code edit name used as tab text'
        if self._name_exists(file_name):
            file_name = self._rename_duplicate_tabs(
                file_name, code_edit.file_path)
        code_edit._tab_name = file_name
        index = self.addTab(code_edit, icon, file_name)
        self.setCurrentIndex(index)
        self.setTabText(index, file_name)
        code_edit.setFocus(True)
        try:
            fw = frontend.get_mode(code_edit, FileWatcherMode)
        except KeyError:
            # not installed
            pass
        else:
            fw.file_deleted.connect(self._on_file_deleted)

    def addTab(self, elem, icon, name):
        """
        Extends QTabWidget.addTab to keep an internal list of added tabs.
        """
        self._widgets.append(elem)
        return super().addTab(elem, icon, name)

    def refresh_settings(self):
        """
        Calls refresh_settings on every code edit
        """
        for code_edit in self._widgets:
            try:
                code_edit.refresh_settings()
            except AttributeError:
                pass

    def refresh_style(self):
        """
        Calls refresh_style on every code edit
        """
        for code_edit in self._widgets:
            try:
                code_edit.refresh_style()
            except AttributeError:
                pass

    def _name_exists(self, name):
        """
        Checks if we already have an opened tab with the same name.
        """
        for i in range(self.count()):
            if self.tabText(i) == name:
                return True
        return False

    def _save_editor(self, code_edit):
        path = None
        if not code_edit.file_path:
            path = QtGui.QFileDialog.getSaveFileName(
                self, 'Choose destination path')
            if path:
                frontend.save_to_file(code_edit, path)
        else:
            frontend.save_to_file(code_edit, path)

    def _rename_duplicate_tabs(self, name, path):
        """
        Rename tabs whose title is the same as the name
        """
        for i in range(self.count()):
            if self.tabText(i) == name:
                file_path = self._widgets[i].file_path
                if file_path:
                    parent_dir = os.path.split(os.path.abspath(
                        os.path.join(file_path, os.pardir)))[1]
                    new_name = os.path.join(parent_dir, name)
                    self.setTabText(i, new_name)
                    self._widgets[i]._tab_name = new_name
                break
        if path:
            parent_dir = os.path.split(os.path.abspath(
                os.path.join(path, os.pardir)))[1]
            return os.path.join(parent_dir, name)
        else:
            return name

    def _on_current_changed(self, index):
        widget = self._widgets[index]
        if self._current:
            # needed if the user set save_on_focus_out to True which change
            # the dirty flag
            self._on_dirty_changed(self._current.dirty)
        self._current = widget
        try:
            if self._current:
                self._current.dirty_changed.connect(self._on_dirty_changed)
                self._on_dirty_changed(self._current.dirty)
                self._current.setFocus()
        except AttributeError:
            pass  # not an editor widget

    def removeTab(self, p_int):
        """
        Removes tab at index ``p_int``.

        This method will emits tab_closed for the removed tab.

        """
        QTabWidget.removeTab(self, p_int)
        widget = self._widgets.pop(p_int)
        if widget == self._current:
            self._current = None
        self.tab_closed.emit(widget)
        self._del_code_edit(widget)

    def _on_tab_close_requested(self, index):
        widget = self._widgets[index]
        try:
            if not widget.dirty:
                self.removeTab(index)
            else:
                dlg = DlgUnsavedFiles(
                    self, files=[widget.file_path if widget.file_path else
                                 widget._tab_name])
                if dlg.exec_() == dlg.Accepted:
                    if not dlg.discarded:
                        self._save_editor(widget)
                    self.removeTab(index)
        except AttributeError as e:
            _logger().warning(e)
            pass  # do nothing, let the user handle this case
        if self.count() == 0:
            self.last_tab_closed.emit()

    def _show_tab_context_menu(self, position):
        self._context_mnu.popup(self.mapToGlobal(position))

    def _try_close_dirty_tabs(self, exept=None):
        """
        Tries to close dirty tabs. Uses DlgUnsavedFiles to ask the user
        what he wants to do.
        """
        widgets, filenames = self._collect_dirty_tabs(exept=exept)
        if not len(filenames):
            return True
        dlg = DlgUnsavedFiles(self, files=filenames)
        if dlg.exec_() == dlg.Accepted:
            if not dlg.discarded:
                for item in dlg.listWidget.selectedItems():
                    filename = item.text()
                    for w in widgets:
                        if w.file_path == filename:
                            break
                    if w != exept:
                        w.save_to_file()
                        self.removeTab(self.indexOf(w))
            return True
        return False

    def _collect_dirty_tabs(self, exept=None):
        """
        Collects the list of dirty tabs
        """
        widgets = []
        filenames = []
        for i in range(self.count()):
            widget = self._widgets[i]
            try:
                if widget.dirty and widget != exept:
                    widgets.append(widget)
                    filenames.append(widget.file_path)
            except AttributeError:
                pass
        return widgets, filenames

    def _on_dirty_changed(self, dirty):
        """
        Adds a star in front of a dirtt tab and emits dirty_changed.
        """
        try:
            title = self._current._tab_name
            index = self.indexOf(self._current)
            if dirty:
                self.setTabText(index, "* " + title)
            else:
                self.setTabText(index, title)
        except AttributeError:
            pass
        self.dirty_changed.emit(dirty)

    def closeEvent(self, event):
        """
        On close, we try to close dirty tabs and only process the close
        event if all dirty tabs were closed by the user.
        """
        if not self.close_all():
            event.ignore()
        else:
            event.accept()

    def _on_file_deleted(self, editor):
        """
        Removes deleted files from the tab widget.
        """
        self.removeTab(self.indexOf(editor))


if __name__ == "__main__":
    from pyqode.core import frontend
    from pyqode.core.frontend import widgets

    def main():
        app = QtGui.QApplication(sys.argv)
        tw = TabWidget(None)
        e = frontend.CodeEdit(tw)
        frontend.open_file(e, __file__)
        tw.add_code_edit(e)

        e = frontend.CodeEdit(tw)
        frontend.open_file(e, pyqode.core.__file__)
        tw.add_code_edit(e)

        e = frontend.CodeEdit(tw)
        frontend.open_file(e, widgets.__file__)
        tw.add_code_edit(e)

        e = frontend.CodeEdit(tw)
        frontend.open_file(e, widgets.__file__)
        tw.add_code_edit(e)

        # not from file, we must set the name ourself
        e = frontend.CodeEdit(tw)
        e.setPlainText("haha", "text/x-python", 'utf-8')
        tw.add_code_edit(e, 'haha')

        e = frontend.CodeEdit(tw)
        e.setPlainText("haha", "text/x-python", 'utf-8')
        tw.add_code_edit(e, 'haha')

        tw.showMaximized()
        app.exec_()

    main()
