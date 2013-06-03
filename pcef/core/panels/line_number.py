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
import pcef
from pcef import constants
from pcef.core.panel import Panel


class Block:
    def __init__(self, left, top, width, height, line_nbr):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.line_nbr = line_nbr
        self.__selecting = False
        self.__sel_start = 0

    def __repr__(self):
        return "{0} - [{1}, {2}]".format(self.line_nbr, self.top, self.height)


class LineNumberPanel(Panel):
    """
    The liner number panel displays the document line numbers.
    """
    IDENTIFIER = "LineNumberPanel"
    _DESCRIPTION = "Display line number"

    def install(self, editor):
        """
        Adds style properties to the editor and setup default brushe/pen
        """
        Panel.install(self, editor)
        self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(
            self.editor.style.value("panelBackground")))
        self.__pen = pcef.QtGui.QPen(pcef.QtGui.QColor(
            self.editor.style.value("panelForeground")))

    def onStyleChanged(self, section, key, value):
        """
        Repaints widget if the our style properties changed.

        :param section:
        :param key:
        :param value:
        """
        if key == "panelBackground":
            self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(value))
            self.editor.repaint()
        elif key == "panelForeground":
            self.__pen = pcef.QtGui.QPen(pcef.QtGui.QColor(value))
            self.editor.repaint()

    def onStateChanged(self, state):
        """
        Nothing to do here, we do everything in the widget events.

        :param state: Enable state
        """
        pass

    def sizeHint(self):
        """
        Returns the panel size hint (as the panel is on the left, we only need to
        compute the width
        :return:
        """
        return pcef.QtCore.QSize(self.lineNumberAreaWidth() + 5, 50)

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
        assert isinstance(e, pcef.QtGui.QMouseEvent)
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

        :return:
        """
        # fill background
        painter = pcef.QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.__brush)
        # get style options (font, size)
        width = self.width()
        height = self.editor.fontMetrics().height()
        font = self.editor.font()
        bold_font = pcef.QtGui.QFont(font)
        bold_font.setBold(True)
        # get selection range
        sel_start, sel_end = self.editor.selectionRange()
        # draw every visible blocks
        for top, blockNumber in self.editor.visibleBlocks:
                painter.setPen(self.__pen)
                if sel_start <= blockNumber <= sel_end or \
                   (sel_start == sel_end and sel_start == blockNumber +1):
                    painter.setFont(bold_font)
                else:
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 pcef.QtCore.Qt.AlignRight, str(blockNumber))