#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
Contains a custom QTableWidget for easier displaying of CheckerMessages
"""
from pyqode.core.frontend.utils import memoized
from pyqode.core.frontend.modes.checker import CheckerMessage
from pyqode.core.frontend.modes.checker import CheckerMessages
from PyQt4 import QtCore, QtGui

from PyQt4.QtGui import QTableWidget


COL_TYPE = 1
COL_FILE_NAME = 2
COL_LINE_NBR = 3
COL_MSG = 4
COL_PATH = 5


class ErrorsTable(QTableWidget):
    """
    Extends a QtGui.QTableWidget to easily show
    :class:`CheckerMessage`.

    You add messages to the table using

    :meth:`pyqode.python.QErrorsTable.addMessage`. You clear the table using
    :meth:`pyqode.python.QErrorsTable.clear`
    """
    #: Signal emitted when a message is activated, the clicked signal is passed
    #: as a parameter
    msg_activated = QtCore.pyqtSignal(CheckerMessage)

    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ["Nr", "Type", "File name", "Line", "Description", "File path"])
        #self.horizontalHeader().showSortIndicator = True
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setResizeMode(COL_MSG, QtGui.QHeaderView.Stretch)
        self.setMinimumSize(900, 200)
        self.itemActivated.connect(self._on_item_activated)
        self.setSelectionMode(self.SingleSelection)
        self.setSelectionBehavior(self.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.contextMenu = QtGui.QMenu()
        self.actionCopyDescription = QtGui.QAction("Copy", self)
        self.actionCopyDescription.triggered.connect(
            self._copy_cell_text)
        self.contextMenu.addAction(self.actionCopyDescription)

    def _copy_cell_text(self):
        """
        Copies the description of the selected message to the clipboard
        """
        txt = self.currentItem().text()
        QtGui.QApplication.clipboard().setText(txt)

    def _show_context_menu(self, pos):
        self.contextMenu.exec_(self.mapToGlobal(pos))

    def clear(self, *args, **kwargs):
        """
        Clears the tables and the message list
        """
        QtGui.QTableWidget.clear(self, *args, **kwargs)
        self.setRowCount(0)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ["Nr", "Type", "File name", "Line", "Description", "File path"])

    @memoized
    def make_icon(self, icon):
        if isinstance(icon, tuple):
            return QtGui.QIcon.fromTheme(
                icon[0], QtGui.QIcon(icon[1]))
        elif isinstance(icon, str):
            return QtGui.QIcon(icon)
        else:
            return None

    def add_message(self, checkerMessage):
        """
        Adds a checker message to the table.

        :param checkerMessage: The message to add
        :type checkerMessage: pyqode.core.frontend.modes.CheckerMessage
        """
        #self._messages.append(checkerMessage)
        row = self.rowCount()
        self.insertRow(row)

        # Nr
        item = QtGui.QTableWidgetItem(str(row + 1).zfill(3))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, 0, item)

        # type
        item = QtGui.QTableWidgetItem(self.make_icon(checkerMessage.icon),
                                      checkerMessage.status_string)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, COL_TYPE, item)

        # filename
        item = QtGui.QTableWidgetItem(
            QtCore.QFileInfo(checkerMessage.path).fileName())
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, COL_FILE_NAME, item)

        # line
        if checkerMessage.line <= 0:
            item = QtGui.QTableWidgetItem("----")
        else:
            item = QtGui.QTableWidgetItem(str(checkerMessage.line).zfill(4))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, COL_LINE_NBR, item)

        # desc
        item = QtGui.QTableWidgetItem(checkerMessage.description)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, COL_MSG, item)

        # filename
        item = QtGui.QTableWidgetItem(checkerMessage.path)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setData(QtCore.Qt.UserRole, checkerMessage)
        self.setItem(row, COL_PATH, item)

    def _on_item_activated(self, item):
        """
        Emits the message activated signal
        """
        msg = item.data(QtCore.Qt.UserRole)
        self.msg_activated.emit(msg)


if __name__ == "__main__":
    import sys

    def print_message(msg):
        print("Message activated: %s" % msg)

    def main():
        app = QtGui.QApplication(sys.argv)
        t = ErrorsTable()
        t.msg_activated.connect(print_message)

        t.add_message(CheckerMessage(
            "A warning message", CheckerMessages.WARNING, 4,
            path="/home/usr/file.py"))

        t.add_message(CheckerMessage(
            "An error message", CheckerMessages.ERROR, 569,
            path="/home/usr/file2.py"))

        t.add_message(CheckerMessage(
            "An info message", CheckerMessages.INFO, 169,
            path="/home/usr/file3.py"))

        t.add_message(CheckerMessage(
            "Tata", CheckerMessages.WARNING, 4,
            path="/home/usr/file3.py"))

        t.add_message(CheckerMessage(
            "Titi", CheckerMessages.ERROR, 4,
            path="/home/usr/file2.py"))

        t.add_message(CheckerMessage(
            "Toto", CheckerMessages.INFO, 4,
            path="/home/usr/file1.py"))
        t.setSortingEnabled(True)
        t.show()
        app.exec_()

    main()
