# -*- coding: utf-8 -*-
"""
This module contains the right margin mode.
"""
from pyqode.core.api import TextHelper
from pyqode.core.api import Mode
from pyqode.qt import QtGui


class RightMarginMode(Mode):
    """
    Display a right margin at column 80 by default.

    """
    @property
    def color(self):
        """
        Gets/sets the color of the margin
        """
        return self._color

    @color.setter
    def color(self, value):
        """
        Gets/sets the color of the margin
        """
        self._color = value
        self._pen = QtGui.QPen(self._color)
        TextHelper(self.editor).mark_whole_doc_dirty()
        self.editor.repaint()

    @property
    def position(self):
        """
        Gets/sets the position of the margin
        """
        return self._margin_pos

    @position.setter
    def position(self, value):
        """
        Gets/sets the position of the margin
        """
        self._margin_pos = value

    def __init__(self):
        Mode.__init__(self)
        self._margin_pos = 79
        self._color = QtGui.QColor('red')
        self._pen = QtGui.QPen(self._color)

    def on_state_changed(self, state):
        """
        Connects/Disconnects to the painted event of the editor

        :param state: Enable state
        """
        if state:
            self.editor.painted.connect(self._paint_margin)
            self.editor.repaint()
        else:
            self.editor.painted.disconnect(self._paint_margin)
            self.editor.repaint()

    def _paint_margin(self, event):
        """ Paints the right margin after editor paint event. """
        font = QtGui.QFont(self.editor.font_name, self.editor.font_size)
        metrics = QtGui.QFontMetricsF(font)
        pos = self._margin_pos
        offset = self.editor.contentOffset().x() + \
            self.editor.document().documentMargin()
        x80 = round(metrics.width(' ') * pos) + offset
        painter = QtGui.QPainter(self.editor.viewport())
        painter.setPen(self._pen)
        painter.drawLine(x80, 0, x80, 2 ** 16)
