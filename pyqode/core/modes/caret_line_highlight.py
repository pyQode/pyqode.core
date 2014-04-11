# -*- coding: utf-8 -*-
"""
This module contains the care line highlighter mode
"""
from PyQt4 import QtGui

from pyqode.core import style
from pyqode.core.api import TextDecoration, Mode
from pyqode.core.api.utils import drift_color


class CaretLineHighlighterMode(Mode):
    """
    This mode highlights the caret line (active line).
    """
    @property
    def background(self):
        return self._color

    @background.setter
    def background(self, value):
        self._color = value
        self._update_highlight()

    def __init__(self):
        Mode.__init__(self)
        self._decoration = None
        self._brush = None
        self._pos = -1
        self._init_style()

    def _init_style(self):
        if style.caret_line_background is None:
            if self.editor:
                self._color = drift_color(self.editor.background, 110)
            else:
                self._color = drift_color(style.background, 110)
        else:
            self._color = style.caret_line_background
        self._brush = QtGui.QBrush(QtGui.QColor(self._color))

    def _on_state_changed(self, state):
        """
        On state changed we (dis)connect to the cursorPositionChanged signal
        """
        if state:
            self.editor.cursorPositionChanged.connect(self._update_highlight)
            self.editor.new_text_set.connect(self._update_highlight)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self._update_highlight)
            self.editor.new_text_set.disconnect(self._update_highlight)
            self._clear_deco()

    def _on_install(self, editor):
        """
        Installs the mode on the editor and add a style property:
            - caretLineBackground
        """
        Mode._on_install(self, editor)
        self._update_highlight()

    def refresh_style(self):
        self._init_style()
        self._update_highlight()

    def _clear_deco(self):
        if self._decoration:
            self.editor.remove_decoration(self._decoration)

    def _update_highlight(self):
        """
        Updates the current line decoration
        """
        self._clear_deco()
        self._decoration = TextDecoration(self.editor.textCursor())
        self._decoration.set_background(self._brush)
        self._decoration.set_full_width()
        self.editor.add_decoration(self._decoration)
