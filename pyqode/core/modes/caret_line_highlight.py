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
"""
This module contains the care line highlighter mode
"""
from pyqode.core import constants
from pyqode.core.mode import Mode
from pyqode.core.decoration import TextDecoration
from pyqode.core.system import driftColor
from pyqode.qt import QtGui


class CaretLineHighlighterMode(Mode):
    """
    This mode highlights the caret line (active line).

    Here the properties added by the mode to
    :attr:`pyqode.core.QCodeEdit.style`:

    ====================== ====================== ======= ====================== =====================
    Key                    Section                Type    Default value          Description
    ====================== ====================== ======= ====================== =====================
    caretLineBackground    General                QColor  Computed.              This color is computed based on the background color automatically.
    ====================== ====================== ======= ====================== =====================

    """
    #: The mode identifier
    IDENTIFIER = "caretLineHighlighterMode"
    #: The mode description
    DESCRIPTION = "This mode highlights the caret line"

    @property
    def caretLineBackground(self):
        return self.editor.style.value("caretLineBackground")

    @caretLineBackground.setter
    def caretLineBackground(self, value):
        self.editor.style.setValue("caretLineBackground", value)

    def __init__(self):
        Mode.__init__(self)
        self.__decoration = None
        self.__brush = None
        self.__pos = -1

    def _onStateChanged(self, state):
        """
        On state changed we (dis)connect to the cursorPositionChanged signal
        """
        if state:
            self.editor.cursorPositionChanged.connect(self.__updateHighlight)
            self.editor.newTextSet.connect(self.__updateHighlight)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self.__updateHighlight)
            self.editor.newTextSet.disconnect(self.__updateHighlight)
            self.__clearDeco()

    def _onInstall(self, editor):
        """
        Installs the mode on the editor and add a style property:
            - caretLineBackground
        """
        Mode._onInstall(self, editor)
        color = self.editor.style.addProperty(
            "caretLineBackground", driftColor(constants.EDITOR_BACKGROUND, 104))
        self.__brush = QtGui.QBrush(QtGui.QColor(color))
        self.__updateHighlight()

    def _onStyleChanged(self, section, key):
        """
        Changes the highlight brush color and refresh highlighting
        """
        if key == "caretLineBackground":
            self.__brush = QtGui.QBrush(
                self.editor.style.value("caretLineBackground"))
            self.__updateHighlight()
        if not key or key == "background":
            b = self.editor.style.value("background")
            factor = 104
            if b.lightness() < 128:
                factor = 180
            if b.lightness() == 0:
                b = QtGui.QColor("#101010")
            self.__brush = QtGui.QBrush(
                self.editor.style.value("caretLineBackground"))
            self.__updateHighlight()
            self.editor.style.setValue("caretLineBackground",
                                       driftColor(b, factor))

    def __clearDeco(self):
        if self.__decoration:
            self.editor.removeDecoration(self.__decoration)

    def __updateHighlight(self):
        """
        Updates the current line decoration
        """
        self.__clearDeco()
        self.__decoration = TextDecoration(self.editor.textCursor())
        self.__decoration.setBackground(self.__brush)
        self.__decoration.setFullWidth()
        self.editor.addDecoration(self.__decoration)
