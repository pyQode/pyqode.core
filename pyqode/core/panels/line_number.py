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
This module contains the line number panel
"""
from pyqode.core.editor import Panel
from PyQt4 import QtCore, QtGui


class LineNumberPanel(Panel):
    """
    The liner number panel displays the document line numbers.
    """
    def __init__(self):
        Panel.__init__(self)
        self.scrollable = True
        self._selecting = False
        self._sel_start = -1

    def _on_install(self, editor):
        Panel._on_install(self, editor)

    def sizeHint(self):
        """
        Returns the panel size hint (as the panel is on the left, we only need
        to compute the width
        """
        return QtCore.QSize(self.line_number_area_width(), 50)

    def line_number_area_width(self):
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
        space = 3 + self.editor.fontMetrics().width("9") * digits
        return space

    def mousePressEvent(self, e):
        """
        Starts selecting
        """
        self._selecting = True
        self._sel_start = e.pos().y()
        start = end = self.editor.line_nbr_from_position(self._sel_start)
        self.editor.select_full_lines(start, end)

    def cancel_selection(self):
        self._selecting = False
        self._sel_start = -1

    def mouseReleaseEvent(self, e):
        """ Cancels selection """
        self.cancel_selection()

    def leaveEvent(self, event):
        """
        Cancels selection
        """
        self.cancel_selection()

    def mouseMoveEvent(self, e):
        """
        Updates end of selection if we are currently selecting
        """
        if self._selecting:
            end_pos = e.pos().y()
            start_line = self.editor.line_nbr_from_position(self._sel_start)
            end_line = self.editor.line_nbr_from_position(end_pos)
            self.editor.select_full_lines(start_line, end_line)

    def paintEvent(self, event):
        """
        Paints the line numbers
        """
        Panel.paintEvent(self, event)
        self._lineColorU = self.palette().color(
            QtGui.QPalette.Disabled, QtGui.QPalette.WindowText)
        self._lineColorS = self.palette().color(
            QtGui.QPalette.Normal, QtGui.QPalette.WindowText)
        if self.isVisible():
            painter = QtGui.QPainter(self)
            # get style options (font, size)
            width = self.width()
            height = self.editor.fontMetrics().height()
            font = self.editor.font()
            bold_font = self.editor.font()
            bold_font.setBold(True)
            pen = QtGui.QPen(self._lineColorU)
            pen_selected = QtGui.QPen(self._lineColorS)
            painter.setFont(font)
            # get selection range
            sel_start, sel_end = self.editor.selection_range()
            has_sel = sel_start != sel_end
            cl = self.editor.cursor_position[0]
            # draw every visible blocks
            for top, blockNumber, block in self.editor.visible_blocks:
                if ((has_sel and sel_start <= blockNumber <= sel_end) or
                        (not has_sel and cl == blockNumber)):
                    painter.setPen(pen_selected)
                    painter.setFont(bold_font)
                else:
                    painter.setPen(pen)
                    painter.setFont(font)
                painter.drawText(0, top, width, height,
                                 QtCore.Qt.AlignRight, str(blockNumber))
