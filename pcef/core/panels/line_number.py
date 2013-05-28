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



class LineNumberPanel(Panel):
    def __init__(self):
        Panel.__init__(self, "LineNumberPanel", "Display line number")

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

    def paintEvent(self, event):
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
        l, c = self.editor.cursorPosition
        width = self.width()
        height = self.editor.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(self.__pen)
                if blockNumber + 1 == l:
                    painter.setFont(bold_font)
                else:
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 pcef.QtCore.Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()