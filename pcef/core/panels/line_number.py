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
    def __init__(self):
        Panel.__init__(self, "LineNumberPanel", "Display line number")
        self.__blocks = []

    def install(self, editor):
        Panel.install(self, editor)
        bck = self.editor.style.addProperty(
            "background", constants.LINE_NBR_BACKGROUND,
            "LineNumberArea")
        fore = self.editor.style.addProperty("foreground",
                                             constants.LINE_NBR_FOREGROUND,
                                      "LineNumberArea")
        self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(bck))
        self.__pen = pcef.QtGui.QPen(pcef.QtGui.QColor(fore))

    def onStyleChanged(self, section, key, value):
        if section == "LineNumberArea" and key == "background":
            self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(value))
            self.editor.repaint()
        elif section == "LineNumberArea" and key == "foreground":
            self.__pen = pcef.QtGui.QPen(pcef.QtGui.QColor(value))
            self.editor.repaint()

    def onStateChanged(self, state):
        """
        Connect/Disconnects to/from editor signals

        :param state: Enable state
        """
        if state:
            self.editor.updateRequest.connect(self.updateLineNumberArea)
        else:
            self.editor.updateRequest.disconnect(self.updateLineNumberArea)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())
        if rect.contains(self.editor.viewport().rect()):
            self.editor.updateViewportMargins()

    def sizeHint(self):
        return pcef.QtCore.QSize(self.lineNumberAreaWidth() + 5, 50)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.editor.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.editor.fontMetrics().width(u"9") * digits
        return space

    def linePos(self, line_number):
        """
        Gets the line pos on the Y-Axis in pixels (at the center of the line)

        :param line_number: The line number for which we want to know the
                            position in pixels.

        :rtype int or None
        """
        for b in self.__blocks:
            if b.line_nbr == line_number:
                return b.top + b.height / 2.0
        return None

    def checkPos(self, y_pos, top, height):
        if top <= y_pos <= top + height:
            return True
        return False

    def lineNumber(self, y_pos):
        """
        Get the line number from the y_pos
        :param y_pos: Y pos in the QCodeEdit
        """
        for b in self.__blocks:
            if self.checkPos(y_pos, b.top, b.height):
                return b.line_nbr
        return None

    def mousePressEvent(self, e):
        assert isinstance(e, pcef.QtGui.QMouseEvent)
        self.__selecting = True
        self.__sel_start = e.pos().y()

    def mouseReleaseEvent(self, e):
        self.__selecting = False
        self.__sel_start = -1

    def leaveEvent(self, QEvent):
        self.__selecting = False
        self.__sel_start = -1

    def mouseMoveEvent(self, e):
        if self.__selecting:
            end_pos = e.pos().y()
            start_line = self.lineNumber(self.__sel_start)
            end_line = self.lineNumber(end_pos)
            self.editor.selectFullLines(start_line, end_line)

    def paintEvent(self, event):
        assert isinstance(event, pcef.QtGui.QPaintEvent)
        self.__blocks[:] = []
        painter = pcef.QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.__brush)
        block = self.editor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        font = self.editor.font()
        bold_font = pcef.QtGui.QFont(font)
        bold_font.setBold(True)
        sel_start, sel_end = self.editor.selectedLines()
        width = self.width()
        height = self.editor.fontMetrics().height()
        while block.isValid():
            if block.isVisible():
                number = str(blockNumber + 1)
                painter.setPen(self.__pen)
                if sel_start <= blockNumber + 1 <= sel_end or \
                   (sel_start == sel_end and sel_start == blockNumber +1):
                    painter.setFont(bold_font)
                else:
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 pcef.QtCore.Qt.AlignRight, number)
                self.__blocks.append(
                    Block(0, top, width, height, blockNumber+1))
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()