#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
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
from pyqode.core.decoration import TextDecoration
from pyqode.core.mode import Mode
from pyqode.qt import QtCore, QtGui


class WordClickMode(Mode, QtCore.QObject):
    """
    This mode adds support for document word click.

    It will highlight the click-able word when the user press control and move
    the mouse over a word.

    :attr:`pyqode.core.WordClickMode.wordClicked` is emitted when the word is
    clicked by the user (while keeping control pressed).
    """
    IDENTIFIER = "wordClickMode"
    DESCRIPTION = "Emits wordClicked signal when user click on a word in the " \
                  "document while keeping control pressed"

    #: signal emitted when a word is clicked. The parameter is a QTextCursor
    #: with the clicked word set as the selected text.
    wordClicked = QtCore.Signal(QtGui.QTextCursor)

    def __init__(self):
        QtCore.QObject.__init__(self)
        Mode.__init__(self)
        self._previous_cursor_start = -1
        self._previous_cursor_end = -1
        self._deco = None

    def _onStateChanged(self, state):
        if state:
            self.editor.mouseMoved.connect(self._onMouseMoved)
            self.editor.mousePressed.connect(self._onMousePressed)
        else:
            self.editor.mouseMoved.disconnect(self._onMouseMoved)
            self.editor.mousePressed.disconnect(self._onMousePressed)

    def _selectWordUnderMouseCursor(self):
        tc = self.editor.selectWordUnderMouseCursor()
        if (self._previous_cursor_start != tc.selectionStart() and
                    self._previous_cursor_end != tc.selectionEnd()):
            self._remove_decoration()
            self._add_decoration(tc)
        self._previous_cursor_start = tc.selectionStart()
        self._previous_cursor_end = tc.selectionEnd()

    def _onMouseMoved(self, e):
        if e.modifiers() & QtCore.Qt.ControlModifier:
            self._selectWordUnderMouseCursor()
        else:
            self._remove_decoration()
            self.editor.setCursor(QtCore.Qt.IBeamCursor)
            self._previous_cursor_start = -1
            self._previous_cursor_end = -1

    def _onMousePressed(self, e):
        if e.button() == 1 and self._deco:
            tc = self.editor.selectWordUnderMouseCursor()
            if tc and tc.selectedText():
                self.wordClicked.emit(tc)

    def _add_decoration(self, tc):
        #assert self._deco is None
        if self._deco is None:
            if tc.selectedText():
                self._deco = TextDecoration(tc)
                self._deco.setForeground(QtCore.Qt.blue)
                self._deco.underlined()
                self.editor.addDecoration(self._deco)
                self.editor.setCursor(QtCore.Qt.PointingHandCursor)
            else:
                self.editor.setCursor(QtCore.Qt.IBeamCursor)

    def _remove_decoration(self):
        if self._deco is not None:
            self.editor.removeDecoration(self._deco)
            self._deco = None
