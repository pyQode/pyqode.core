# -*- coding: utf-8 -*-
"""
This module contains the WordClickMode
"""
from PyQt4 import QtCore, QtGui
from pyqode.core import frontend
from pyqode.core.frontend import TextDecoration, Mode


class WordClickMode(Mode, QtCore.QObject):
    """
    This mode adds support for document word click.

    It will highlight the click-able word when the user press control and move
    the mouse over a word.

    :attr:`pyqode.core.frontend.modes.WordClickMode.word_clicked` is emitted
    when the word is clicked by the user (while keeping control pressed).
    """
    #: Signal emitted when a word is clicked. The parameter is a
    #: QTextCursor with the clicked word set as the selected text.
    word_clicked = QtCore.pyqtSignal(QtGui.QTextCursor)

    def __init__(self):
        QtCore.QObject.__init__(self)
        Mode.__init__(self)
        self._previous_cursor_start = -1
        self._previous_cursor_end = -1
        self._deco = None

    def _on_state_changed(self, state):
        """
        Connects/disconnects slots to/from signals when the mode state
        changed.
        """
        if state:
            self.editor.mouse_moved.connect(self._on_mouse_moved)
            self.editor.mouse_pressed.connect(self._on_mouse_pressed)
        else:
            self.editor.mouse_moved.disconnect(self._on_mouse_moved)
            self.editor.mouse_pressed.disconnect(self._on_mouse_pressed)

    def _select_word_under_mouse_cursor(self):
        """ Selects the word under the mouse cursor. """
        cursor = frontend.word_under_mouse_cursor(self.editor)
        if (self._previous_cursor_start != cursor.selectionStart() and
                self._previous_cursor_end != cursor.selectionEnd()):
            self._remove_decoration()
            self._add_decoration(cursor)
        self._previous_cursor_start = cursor.selectionStart()
        self._previous_cursor_end = cursor.selectionEnd()

    def _on_mouse_moved(self, event):
        """ mouse moved callback """
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self._select_word_under_mouse_cursor()
        else:
            self._remove_decoration()
            self.editor.set_mouse_cursor(QtCore.Qt.IBeamCursor)
            self._previous_cursor_start = -1
            self._previous_cursor_end = -1

    def _on_mouse_pressed(self, event):
        """ mouse pressed callback """
        if event.button() == 1 and self._deco:
            cursor = frontend.word_under_mouse_cursor(self.editor)
            if cursor and cursor.selectedText():
                self.word_clicked.emit(cursor)

    def _add_decoration(self, cursor):
        """
        Adds a decoration for the word under ``cursor``.
        """
        if self._deco is None:
            if cursor.selectedText():
                self._deco = TextDecoration(cursor)
                self._deco.set_foreground(QtCore.Qt.blue)
                self._deco.set_as_underlined()
                frontend.add_decoration(self.editor, self._deco)
                self.editor.set_mouse_cursor(QtCore.Qt.PointingHandCursor)
            else:
                self.editor.set_mouse_cursor(QtCore.Qt.IBeamCursor)

    def _remove_decoration(self):
        """
        Removes the word under cursor's decoration
        """
        if self._deco is not None:
            frontend.remove_decoration(self.editor, self._deco)
            self._deco = None
