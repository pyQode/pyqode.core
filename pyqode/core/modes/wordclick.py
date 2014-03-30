# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from pyqode.core.editor import Mode
from pyqode.core.api.decoration import TextDecoration


class WordClickMode(Mode, QtCore.QObject):
    """
    This mode adds support for document word click.

    It will highlight the click-able word when the user press control and move
    the mouse over a word.

    :attr:`pyqode.core.WordClickMode.word_clicked` is emitted when the word is
    clicked by the user (while keeping control pressed).
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
        if state:
            self.editor.mouse_moved.connect(self._on_mouse_moved)
            self.editor.mouse_pressed.connect(self._on_mouse_pressed)
        else:
            self.editor.mouse_moved.disconnect(self._on_mouse_moved)
            self.editor.mouse_pressed.disconnect(self._on_mouse_pressed)

    def _select_word_under_mouse_cursor(self):
        # todo this already exists in QCodeEdit, check if there are any
        # differences
        tc = self.editor.select_word_under_mouse_cursor()
        if (self._previous_cursor_start != tc.selectionStart() and
                self._previous_cursor_end != tc.selectionEnd()):
            self._remove_decoration()
            self._add_decoration(tc)
        self._previous_cursor_start = tc.selectionStart()
        self._previous_cursor_end = tc.selectionEnd()

    def _on_mouse_moved(self, e):
        if e.modifiers() & QtCore.Qt.ControlModifier:
            self._select_word_under_mouse_cursor()
        else:
            self._remove_decoration()
            self.editor.set_cursor(QtCore.Qt.IBeamCursor)
            self._previous_cursor_start = -1
            self._previous_cursor_end = -1

    def _on_mouse_pressed(self, e):
        if e.button() == 1 and self._deco:
            tc = self.editor.select_word_under_mouse_cursor()
            if tc and tc.selectedText():
                self.word_clicked.emit(tc)

    def _add_decoration(self, tc):
        #assert self._deco is None
        if self._deco is None:
            if tc.selectedText():
                self._deco = TextDecoration(tc)
                self._deco.set_foreground(QtCore.Qt.blue)
                self._deco.set_as_underlined()
                self.editor.add_decoration(self._deco)
                self.editor.set_cursor(QtCore.Qt.PointingHandCursor)
            else:
                self.editor.set_cursor(QtCore.Qt.IBeamCursor)

    def _remove_decoration(self):
        if self._deco is not None:
            self.editor.remove_decoration(self._deco)
            self._deco = None
