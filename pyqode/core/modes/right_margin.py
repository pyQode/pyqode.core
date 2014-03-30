# -*- coding: utf-8 -*-
"""
This module contains the right margin mode.
"""
from pyqode.core import settings, style
from pyqode.core.editor import Mode
from PyQt4 import QtGui


class RightMarginMode(Mode):
    """
    Display a right margin at column 80 by default.

    """
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._pen = QtGui.QPen(self._color)
        self.editor.mark_whole_doc_dirty()
        self.editor.repaint()

    @property
    def position(self):
        return self._margin_pos

    @position.setter
    def position(self, value):
        self._margin_pos = value

    def __init__(self):
        Mode.__init__(self)
        self._pen = QtGui.QPen()
        self._init_settings()
        self._init_style()

    def _init_settings(self):
        self._margin_pos = settings.right_margin_pos

    def _init_style(self):
        self._color = style.right_margin_color
        self._pen = QtGui.QPen(self._color)

    def refresh_settings(self):
        self._init_settings()
        self.editor.repaint()

    def refresh_style(self):
        self._init_style()
        self._pen = QtGui.QPen(self._color)
        self.editor.mark_whole_doc_dirty()
        self.editor.repaint()

    def _on_state_changed(self, state):
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
        font = self.editor.currentCharFormat().font()
        fm = QtGui.QFontMetricsF(font)
        pos = self._margin_pos
        offset = self.editor.contentOffset().x() + \
            self.editor.document().documentMargin()
        x80 = round(fm.width(' ') * pos) + offset
        p = QtGui.QPainter(self.editor.viewport())
        p.setPen(self._pen)
        p.drawLine(x80, 0, x80, 2 ** 16)
