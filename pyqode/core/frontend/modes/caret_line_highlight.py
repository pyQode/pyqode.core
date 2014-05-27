# -*- coding: utf-8 -*-
"""
This module contains the care line highlighter mode
"""
from pyqode.qt import QtGui
from pyqode.core import frontend
from pyqode.core.frontend.utils import drift_color


class CaretLineHighlighterMode(frontend.Mode):
    """
    This mode highlights the caret line (active line).
    """
    @property
    def background(self):
        """
        Background color of the caret line. Default is to use a color slightly
        darker/lighter than the background color. You can override the
        automatic color by setting up this property
        """
        if self._color or not self.editor:
            return self._color
        else:
            return drift_color(self.editor.background, 110)

    @background.setter
    def background(self, value):
        """
        Background color of the caret line
        """
        self._color = value
        self.refresh()

    def __init__(self):
        super().__init__()
        self._decoration = None
        self._pos = -1
        self._color = None

    def _on_state_changed(self, state):
        """
        On state changed we (dis)connect to the cursorPositionChanged signal
        """
        if state:
            self.editor.cursorPositionChanged.connect(self.refresh)
            self.editor.new_text_set.connect(self.refresh)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self.refresh)
            self.editor.new_text_set.disconnect(self.refresh)
            self._clear_deco()

    def _on_install(self, editor):
        """
        Installs the mode on the editor and add a style property:
            - caretLineBackground
        """
        super()._on_install(editor)
        self.refresh()

    def _clear_deco(self):
        """ Clear line decoration """
        if self._decoration:
            frontend.remove_decoration(self.editor, self._decoration)

    def refresh(self):
        """
        Updates the current line decoration
        """
        self._clear_deco()
        if self._color:
            color = self._color
        else:
            color = drift_color(self.editor.background, 110)
        brush = QtGui.QBrush(color)
        self._decoration = frontend.TextDecoration(self.editor.textCursor())
        self._decoration.set_background(brush)
        self._decoration.set_full_width()
        frontend.add_decoration(self.editor, self._decoration)
