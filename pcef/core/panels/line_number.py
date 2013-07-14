#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the line number panel
"""
from pcef.core.panel import Panel
from pcef.qt import QtCore, QtGui


class LineNumberPanel(Panel):
    """
    The liner number panel displays the document line numbers.
    """
    IDENTIFIER = "lineNumberArea"
    DESCRIPTION = "Display line number"

    def __init__(self):
        Panel.__init__(self)
        self.scrollable = True

    def install(self, editor):
        Panel.install(self, editor)
        self._lineColorU = self.editor.style.addProperty(
            "lineForeground", self.palette().color(QtGui.QPalette.Disabled,
                                                  QtGui.QPalette.WindowText))
        self._lineColorS = self.editor.style.addProperty(
            "lineForegroundSel", self.palette().color(QtGui.QPalette.Normal,
                                                  QtGui.QPalette.WindowText))

    def onStyleChanged(self, section, key, value):
        Panel.onStyleChanged(self, section, key, value)
        if key == "lineForeground":
            self._lineColorU = self.editor.style.value_from_str(value)
        elif key == "lineForegroundSel":
            self._lineColorS = self.editor.style.value_from_str(value)

    def sizeHint(self):
        """
        Returns the panel size hint (as the panel is on the left, we only need to
        compute the width
        :return:
        """
        return QtCore.QSize(self.lineNumberAreaWidth(), 50)

    def lineNumberAreaWidth(self):
        """
        Computes the lineNumber area width depending on the number of lines
        in the document

        :return: Widtg
        """
        digits = 1
        count = max(1, self.editor.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.editor.fontMetrics().width(u"9") * digits
        return space

    def mousePressEvent(self, e):
        """
        Starts selecting
        """
        assert isinstance(e, QtGui.QMouseEvent)
        self.__selecting = True
        self.__selStart = e.pos().y()
        start = end = self.editor.lineNumber(self.__selStart)
        self.editor.selectFullLines(start, end)

    def cancelSelection(self):
        self.__selecting = False
        self.__selStart = -1

    def mouseReleaseEvent(self, e):
        """ Cancels selection """
        self.cancelSelection()

    def leaveEvent(self, QEvent):
        """
        Cancels selection
        """
        self.cancelSelection()

    def mouseMoveEvent(self, e):
        """
        Updates end of selection if we are currently selecting
        """
        if self.__selecting:
            end_pos = e.pos().y()
            start_line = self.editor.lineNumber(self.__selStart)
            end_line = self.editor.lineNumber(end_pos)
            self.editor.selectFullLines(start_line, end_line)

    def paintEvent(self, event):
        """
        Paints the line numbers
        """
        Panel.paintEvent(self, event)
        if self.isVisible():
            painter = QtGui.QPainter(self)
            # get style options (font, size)
            width = self.width()
            height = self.editor.fontMetrics().height()
            font = self.editor.font()
            bold_font = self.editor.font()
            bold_font.setBold(True)
            pen = QtGui.QPen(self._lineColorU)
            penSelected = QtGui.QPen(self._lineColorS)
            painter.setFont(font)
            # get selection range
            sel_start, sel_end = self.editor.selectionRange()
            has_sel = sel_start != sel_end
            cl = self.editor.cursorPosition[0]
            # draw every visible blocks
            for top, blockNumber in self.editor.visibleBlocks:
                painter.setPen(self.foregroundPen)
                if ((has_sel and sel_start <= blockNumber <= sel_end) or
                        (not has_sel and cl == blockNumber)):
                    painter.setPen(penSelected)
                    painter.setFont(bold_font)
                else:
                    painter.setPen(pen)
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 QtCore.Qt.AlignRight, str(blockNumber))
