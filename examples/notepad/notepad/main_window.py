"""
This module contains the main window implementation.
"""
from PyQt4 import QtGui
from pyqode.core import frontend
from pyqode.core.frontend import widgets

from .editor import GenericCodeEdit

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()

        # setup window properties
        self.setWindowTitle('notepad')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # central widget setup
        self.tab_widget = widgets.TabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # setup menu and toolbar
        menu_bar = QtGui.QMenuBar(self)
        menu_file = QtGui.QMenu('File', menu_bar)
        action_new = QtGui.QAction('New', menu_file)
        action_new.triggered.connect(self.create_new)
        menu_file.addAction(action_new)

        action_open = QtGui.QAction('Open', menu_file)
        action_open.triggered.connect(self.open_requested)
        menu_file.addAction(action_open)

        self.recent_files_manager = widgets.RecentFilesManager(
            'pyqode', 'notepad')
        self.recent_files_manager.clear()
        menu_recents = widgets.MenuRecentFiles(
            self.recent_files_manager, menu_file, title='Recents')
        menu_recents.open_requested.connect(self.open_file)
        menu_file.addMenu(menu_recents)
        self.menu_recents = menu_recents

        menu_bar.addMenu(menu_file)
        self.setMenuBar(menu_bar)

        self.open_file(__file__)

    def closeEvent(self, QCloseEvent):
        self.tab_widget.closeEvent(QCloseEvent)


    def create_new(self):
        print('new')

    def open_file(self, filename):
        if filename:
            index = self.tab_widget.index_from_filename(filename)
            if index == -1:
                editor = GenericCodeEdit(self)
                frontend.open_file(editor, filename)
                self.tab_widget.add_code_edit(editor)
                self.recent_files_manager.open_file(filename)
                self.menu_recents.update_actions()
            else:
                self.tab_widget.setCurrentIndex(index)

    def open_requested(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open')
        self.open_file(filename)
