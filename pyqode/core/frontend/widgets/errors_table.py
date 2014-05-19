# -*- coding: utf-8 -*-
"""
Contains a custom QTableWidget for easier displaying of CheckerMessages
"""
from pyqode.core.frontend.utils import memoized
from pyqode.core.frontend.modes.checker import CheckerMessage
from pyqode.qt import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidget


COL_TYPE = 1
COL_FILE_NAME = 2
COL_LINE_NBR = 3
COL_MSG = 4
COL_PATH = 5


class ErrorsTable(QTableWidget):
    """
    Extends a QtWidgets.QTableWidget to easily show
    :class:`pyqode.core.frontend.modes.CheckerMessage`.

    You add messages to the table using

    :meth:`pyqode.core.frontend.widgets.ErrorsTable.add_message`.

    You clear the table using :meth:`pyqode.core.frontend.widgets.ErrorsTable`.
    """
    # pylint: disable=too-many-public-methods
    #: Signal emitted when a message is activated, the clicked signal is passed
    #: as a parameter
    msg_activated = QtCore.Signal(CheckerMessage)

    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ["Nr", "Type", "File name", "Line", "Description", "File path"])
        self.horizontalHeader().setResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setResizeMode(
            COL_MSG, QtWidgets.QHeaderView.Stretch)
        self.setMinimumSize(900, 200)
        self.itemActivated.connect(self._on_item_activated)
        self.setSelectionMode(self.SingleSelection)
        self.setSelectionBehavior(self.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.context_mnu = QtWidgets.QMenu()
        self._a_copy_desc = QtWidgets.QAction("Copy", self)
        self._a_copy_desc.triggered.connect(
            self._copy_cell_text)
        self.context_mnu.addAction(self._a_copy_desc)

    def _copy_cell_text(self):
        """
        Copies the description of the selected message to the clipboard
        """
        txt = self.currentItem().text()
        QtWidgets.QApplication.clipboard().setText(txt)

    def _show_context_menu(self, pos):
        """ Shows the context menu """
        self.context_mnu.exec_(self.mapToGlobal(pos))

    def clear(self, *args, **kwargs):
        """
        Clears the tables and the message list
        """
        QtWidgets.QTableWidget.clear(self, *args, **kwargs)
        self.setRowCount(0)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ["Nr", "Type", "File name", "Line", "Description", "File path"])

    @staticmethod
    @memoized
    def make_icon(icon):
        """
        Make icon from icon filename/tuple (if you want to use a theme)
        """
        if isinstance(icon, tuple):
            return QtWidgets.QIcon.fromTheme(
                icon[0], QtWidgets.QIcon(icon[1]))
        elif isinstance(icon, str):
            return QtWidgets.QIcon(icon)
        else:
            return None

    def add_message(self, msg):
        """
        Adds a checker message to the table.

        :param msg: The message to add
        :type msg: pyqode.core.frontend.modes.CheckerMessage
        """
        row = self.rowCount()
        self.insertRow(row)

        # Nr
        item = QtWidgets.QTableWidgetItem(str(row + 1).zfill(3))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, 0, item)

        # type
        item = QtWidgets.QTableWidgetItem(self.make_icon(msg.icon),
                                      msg.status_string)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, COL_TYPE, item)

        # filename
        item = QtWidgets.QTableWidgetItem(
            QtCore.QFileInfo(msg.path).fileName())
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, COL_FILE_NAME, item)

        # line
        if msg.line <= 0:
            item = QtWidgets.QTableWidgetItem("----")
        else:
            item = QtWidgets.QTableWidgetItem(str(msg.line).zfill(4))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, COL_LINE_NBR, item)

        # desc
        item = QtWidgets.QTableWidgetItem(msg.description)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, COL_MSG, item)

        # filename
        item = QtWidgets.QTableWidgetItem(msg.path)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, msg)
        self.setItem(row, COL_PATH, item)

    def _on_item_activated(self, item):
        """
        Emits the message activated signal
        """
        msg = item.data(QtCore.Qt.UserRole)
        self.msg_activated.emit(msg)
