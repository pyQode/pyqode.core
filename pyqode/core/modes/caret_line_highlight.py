# -*- coding: utf-8 -*-
"""
This module contains the care line highlighter mode
"""
from PyQt4 import QtGui

from pyqode.core.api import constants
from pyqode.core.editor import Mode
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.system import drift_color


class CaretLineHighlighterMode(Mode):
    """
    This mode highlights the caret line (active line).
    """
    @property
    def background(self):
        return self.editor.style.value("caretLineBackground")

    @background.setter
    def background(self, value):
        self.editor.style.set_value("caretLineBackground", value)

    def __init__(self):
        Mode.__init__(self)
        self._decoration = None
        self._brush = None
        self._pos = -1

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
        color = self.editor.style.add_property(
            "caretLineBackground",
            drift_color(constants.EDITOR_BACKGROUND, 110))
        self._brush = QtGui.QBrush(QtGui.QColor(color))
        self._update_highlight()

    def _on_style_changed(self, section, key):
        """
        Changes the highlight brush color and refresh highlighting
        """
        if key == "caretLineBackground":
            self._brush = QtGui.QBrush(
                self.editor.style.value("caretLineBackground"))
            self._update_highlight()
        if not key or key == "background":
            b = self.editor.style.value("background")
            factor = 104
            if b.lightness() < 128:
                factor = 150
            if b.lightness() == 0:
                b = QtGui.QColor("#101010")
            self._brush = QtGui.QBrush(
                self.editor.style.value("caretLineBackground"))
            self._update_highlight()
            self.editor.style.set_value("caretLineBackground",
                                        drift_color(b, factor))

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
