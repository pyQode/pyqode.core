# -*- coding: utf-8 -*-
"""
This package contains a set of widgets that might be useful when writing
pyqode applications:

    - InteractiveConsole: QTextEdit made for running background process
      interactively. Can be used in an IDE for running programs or to display
      the compiler output,...

    - CodeEditTabWidget: tab widget made to handle CodeEdit instances (or
      any other object that have the same interface).

    - ErrorsTable: a QTableWidget specialised to show CheckerMessage.

    - QPropertyGrid: a simple property grid that works on pure python object
    made up of primitive types (int, float, list, string).
"""
# pylint: disable=unused-import
from pyqode.core.widgets.errors_table import ErrorsTable
from pyqode.core.widgets.interactive import InteractiveConsole
from pyqode.core.widgets.menu_recents import MenuRecentFiles
from pyqode.core.widgets.menu_recents import RecentFilesManager
from pyqode.core.widgets.tabs import TabWidget


__all__ = [
    'ErrorsTable',
    'InteractiveConsole',
    'MenuRecentFiles',
    'RecentFilesManager',
    'TabWidget'
]