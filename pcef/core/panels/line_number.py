#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
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
from pcef.core.panel import Panel


class LineNumberPanel(Panel):
    def __init__(self, parent=None):
        Panel.__init__(self, "LineNumberPanel", "Display line number", parent)

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
        return pcef.QtCore.QSize(self.lineNumberAreaWidth(), 50)

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
        painter.fillRect(event.rect(), pcef.QtCore.Qt.lightGray)
        block = self.editor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(pcef.QtCore.Qt.black)
                painter.setFont(self.editor.font())
                painter.drawText(0, top, self.width(),
                                 self.editor.fontMetrics().height(),
                                 pcef.QtCore.Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()