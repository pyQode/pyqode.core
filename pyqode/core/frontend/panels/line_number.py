# -*- coding: utf-8 -*-
"""
This module contains the line number panel
"""
from pyqode.core import frontend
from pyqode.core.frontend import Panel
from PyQt5 import QtCore, QtWidgets, QtGui


class LineNumberPanel(Panel):
    """
    The liner number panel displays the document line numbers.
    """
    def __init__(self):
        Panel.__init__(self)
        self.scrollable = True
        self._selecting = False
        self._sel_start = -1
        self._line_color_u = self.palette().color(
            QtGui.QPalette.Disabled, QtGui.QPalette.WindowText)
        self._line_color_s = self.palette().color(
            QtGui.QPalette.Normal, QtGui.QPalette.WindowText)

    def _on_install(self, editor):
        Panel._on_install(self, editor)

    def sizeHint(self):  # pylint: disable=invalid-name
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

    def mousePressEvent(self, e):  # pylint: disable=invalid-name
        """
        Starts selecting
        """
        self._selecting = True
        self._sel_start = e.pos().y()
        start = end = frontend.line_nbr_from_position(
            self.editor, self._sel_start)
        frontend.select_lines(self.editor, start, end)

    def cancel_selection(self):
        """
        Cancel line selection.
        """
        self._selecting = False
        self._sel_start = -1

    def mouseReleaseEvent(self, event):
        """ Cancels selection """
        # pylint: disable=invalid-name, unused-argument
        self.cancel_selection()

    def leaveEvent(self, event):
        """
        Cancels selection
        """
        # pylint: disable=invalid-name, unused-argument
        self.cancel_selection()

    def mouseMoveEvent(self, e):
        """
        Updates end of selection if we are currently selecting
        """
        # pylint: disable=invalid-name, unused-argument
        if self._selecting:
            end_pos = e.pos().y()
            start_line = frontend.line_nbr_from_position(
                self.editor, self._sel_start)
            end_line = frontend.line_nbr_from_position(self.editor, end_pos)
            frontend.select_lines(self.editor, start_line, end_line)

    def paintEvent(self, event):
        """
        Paints the line numbers
        """
        # pylint: disable=invalid-name, unused-argument, too-many-locals
        Panel.paintEvent(self, event)
        if self.isVisible():
            painter = QtGui.QPainter(self)
            # get style options (font, size)
            width = self.width()
            height = self.editor.fontMetrics().height()
            font = self.editor.font()
            bold_font = self.editor.font()
            bold_font.setBold(True)
            pen = QtGui.QPen(self._line_color_u)
            pen_selected = QtGui.QPen(self._line_color_s)
            painter.setFont(font)
            # get selection range
            sel_start, sel_end = frontend.selection_range(self.editor)
            has_sel = sel_start != sel_end
            cl = frontend.current_line_nbr(self.editor)
            # draw every visible blocks
            # pylint: disable=unused-variable
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
