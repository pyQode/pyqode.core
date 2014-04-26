"""
This module contains the main window implementation.
"""
import mimetypes
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
from pyqode.core import frontend
from pyqode.core import style
from pyqode.core.frontend import modes
from pyqode.core.frontend import widgets
from .editor import GenericCodeEdit
from .ui.main_window_ui import Ui_MainWindow


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Load our UI (made in Qt Designer)
        self.setupUi(self)
        self.setup_recent_files_menu()
        self.setup_actions()
        # setup some specific mimetypes
        mimetypes.add_type('text/xml', '.ui') # qt designer ui forms
        mimetypes.add_type('text/x-rst', '.rst') # rst docs
        mimetypes.add_type('text/x-cython', '.pyx') # cython impl files
        mimetypes.add_type('text/x-cython', '.pxd') # cython def files
        # cobol files
        for ext in ['.cbl', '.cob', '.cpy']:
            mimetypes.add_type('text/x-cobol', ext)
            mimetypes.add_type('text/x-cobol', ext.upper())
        if sys.platform == 'win32':
            # windows systems do not have a mimetypes for most of the codes
            # python, you have to add them all explicitely on windows,
            # otherwise there won't be any syntax highlighting
            mimetypes.add_type('text/x-python', '.py')
            mimetypes.add_type('text/x-python', '.pyw')

    def setup_actions(self):
        """ Connects slots to signals """
        self.actionOpen.triggered.connect(self.on_open)
        self.actionNew.triggered.connect(self.on_new)
        self.actionSave.triggered.connect(self.tabWidget.save_current)
        self.actionSave_as.triggered.connect(self.on_save_as)
        self.actionClose_tab.triggered.connect(self.tabWidget.close)
        self.actionClose_other_tabs.triggered.connect(
            self.tabWidget.close_others)
        self.actionClose_all_tabs.triggered.connect(self.tabWidget.close_all)
        self.actionQuit.triggered.connect(QtGui.QApplication.instance().quit)
        self.tabWidget.dirty_changed.connect(self.on_dirty_changed)
        self.tabWidget.currentChanged.connect(self.on_current_tab_changed)
        self.actionAbout.triggered.connect(self.on_about)

    def setup_recent_files_menu(self):
        """ Setup the recent files menu and manager """
        self.recent_files_manager = widgets.RecentFilesManager(
            'pyqode', 'notepad')
        self.menu_recents = widgets.MenuRecentFiles(
            self.menuFile, title='Recents',
            recent_files_manager=self.recent_files_manager)
        self.menu_recents.open_requested.connect(self.open_file)
        self.menuFile.insertMenu(self.actionSave, self.menu_recents)
        self.menuFile.insertSeparator(self.actionSave)

    def setup_mnu_style(self, editor):
        menu = QtGui.QMenu('Styles', self.menuEdit)
        group = QtGui.QActionGroup(self)
        current_style = frontend.get_mode(
            editor, modes.PygmentsSyntaxHighlighter).pygments_style
        group.triggered.connect(self.on_style_changed)
        for s in sorted(modes.PYGMENTS_STYLES):
            a = QtGui.QAction(menu)
            a.setText(s)
            a.setCheckable(True)
            if s == current_style:
                a.setChecked(True)
            group.addAction(a)
            menu.addAction(a)
        self.menuEdit.addMenu(menu)

    def closeEvent(self, QCloseEvent):
        """
        Delegates the close event to the tabWidget to be sure we do not quit
        the application while there are some still some unsaved tabs.
        """
        self.tabWidget.closeEvent(QCloseEvent)

    @QtCore.pyqtSlot(str)
    def open_file(self, path):
        """
        Creates a new GenericCodeEdit, opens the requested file and adds it
        to the tab widget.

        :param path: Path of the file to open
        """
        if path:
            index = self.tabWidget.index_from_filename(path)
            if index == -1:
                editor = GenericCodeEdit(self)
                frontend.open_file(editor, path)
                self.tabWidget.add_code_edit(editor)
                self.recent_files_manager.open_file(path)
                self.menu_recents.update_actions()
            else:
                self.tabWidget.setCurrentIndex(index)

    @QtCore.pyqtSlot()
    def on_new(self):
        """
        Add a new empty code editor to the tab widget
        """
        self.tabWidget.add_code_edit(GenericCodeEdit(self), 'New document')

    @QtCore.pyqtSlot()
    def on_open(self):
        """
        Shows an open file dialog and open the file if the dialog was
        accepted.

        """
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open')
        if filename:
            self.open_file(filename)

    @QtCore.pyqtSlot()
    def on_save_as(self):
        """
        Save the current editor document as.
        """
        path = self.tabWidget.currentWidget().file_path
        path = os.path.dirname(path) if path else ''
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save', path)
        if filename:
            self.tabWidget.save_current(filename)
            self.recent_files_manager.open_file(filename)
            self.menu_recents.update_actions()

    @QtCore.pyqtSlot(bool)
    def on_dirty_changed(self, dirty):
        """
        Enable/Disable save action depending on the dirty flag of the
        current editor tab.

        :param dirty: Dirty flag
        """
        try:
            path = self.tabWidget.currentWidget().file_path
        except (AttributeError, TypeError):
            self.actionSave.setDisabled(True)
        else:
            self.actionSave.setEnabled(dirty and path is not None)

    def setup_mnu_edit(self, editor):
        self.menuEdit.addActions(editor.actions())
        self.menuEdit.addSeparator()
        self.setup_mnu_style(editor)

    def setup_mnu_modes(self, editor):
        for k, v in sorted(frontend.get_modes(editor).items()):
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.on_mode_state_changed)
            a.mode = v
            self.menuModes.addAction(a)

    def setup_mnu_panels(self, editor):
        for zones, dic in sorted(frontend.get_panels(editor).items()):
            for k, v in dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                a.setCheckable(True)
                a.setChecked(True)
                a.changed.connect(self.on_panel_state_changed)
                a.panel = v
                self.menuPanels.addAction(a)

    @QtCore.pyqtSlot()
    def on_current_tab_changed(self):
        self.menuEdit.clear()
        self.menuModes.clear()
        self.menuPanels.clear()
        editor = self.tabWidget.currentWidget()
        self.menuEdit.setEnabled(editor is not None)
        self.menuModes.setEnabled(editor is not None)
        self.menuPanels.setEnabled(editor is not None)
        self.actionSave_as.setEnabled(editor is not None)
        self.actionClose_tab.setEnabled(editor is not None)
        self.actionClose_all_tabs.setEnabled(editor is not None)
        self.actionClose_other_tabs.setEnabled(
            editor is not None and self.tabWidget.count() > 1)
        if editor:
            self.setup_mnu_edit(editor)
            self.setup_mnu_modes(editor)
            self.setup_mnu_panels(editor)
        else:
            self.actionSave.setDisabled(True)

    @QtCore.pyqtSlot(QtGui.QAction)
    def on_style_changed(self, action):
        style.pygments_style = action.text()
        self.tabWidget.currentWidget().refresh_style()

    def on_panel_state_changed(self):
        action = self.sender()
        action.panel.enabled = action.isChecked()

    def on_mode_state_changed(self):
        action = self.sender()
        action.mode.enabled = action.isChecked()

    def on_about(self):
        QtGui.QMessageBox.about(
            self, 'pyQode notepad',
            'This notepad application is an example of what you can do with '
            'pyqode.core.')
