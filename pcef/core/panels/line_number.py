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
from pcef.qt import QtCore, QtGui
from pcef.core import constants
from pcef.core.panel import Panel


class LineNumberPanel(Panel):
    """
    The liner number panel displays the document line numbers.
    """
    IDENTIFIER = "lineNumberArea"
    DESCRIPTION = "Display line number"

    def install(self, editor):
        """
        Adds style properties to the editor and setup default brushe/pen
        """
        Panel.install(self, editor)
        self.__brush = QtGui.QBrush(QtGui.QColor(
            self.editor.style.value("panelBackground")))
        self.__pen = QtGui.QPen(QtGui.QColor(
            self.editor.style.value("panelForeground")))

    def onStyleChanged(self, section, key, value):
        """
        Repaints widget if the our style properties changed.

        :param section:
        :param key:
        :param value:
        """
        if key == "panelBackground":
            self.__brush = QtGui.QBrush(QtGui.QColor(value))
            self.editor.repaint()
        elif key == "panelForeground":
            self.__pen = QtGui.QPen(QtGui.QColor(value))
            self.editor.repaint()

    # def onStateChanged(self, state):
    #     """
    #     Nothing to do here, we do everything in the widget events.
    #
    #     :param state: Enable state
    #     """
    #     super(LineNumberPanel, self).onStateChanged(state)

    def sizeHint(self):
        """
        Returns the panel size hint (as the panel is on the left, we only need to
        compute the width
        :return:
        """
        return QtCore.QSize(self.lineNumberAreaWidth() + 5, 50)

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

    def mouseReleaseEvent(self, e):
        """ Cancels selecting"""
        self.__selecting = False
        self.__selStart = -1

    def leaveEvent(self, QEvent):
        """
        Cancels selecting
        """
        self.__selecting = False
        self.__selStart = -1

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
        if self.isVisible():
            # fill background
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self.__brush)
            # get style options (font, size)
            width = self.width()
            height = self.editor.fontMetrics().height()
            font = self.editor.font()
            bold_font = QtGui.QFont(font)
            bold_font.setBold(True)
            # get selection range
            sel_start, sel_end = self.editor.selectionRange()
            has_sel = sel_start != sel_end
            cl = self.editor.cursorPosition[0]
            # draw every visible blocks
            for top, blockNumber in self.editor.visibleBlocks:
                painter.setPen(self.__pen)
                if ((has_sel and sel_start <= blockNumber <= sel_end) or
                        (not has_sel and cl == blockNumber)):
                    painter.setFont(bold_font)
                else:
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 QtCore.Qt.AlignRight, str(blockNumber))
