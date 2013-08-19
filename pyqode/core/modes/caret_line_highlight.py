#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
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
    This mode highlights the caret line (active line)
    """
    #: The mode identifier
    IDENTIFIER = "caretLineHighlighterMode"
    #: The mode description
    DESCRIPTION = "This mode highlights the caret line"

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
            self.clearDeco()

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
            self.editor.style.setValue("caretLineBackground",
                                       driftColor(b, factor))

    def clearDeco(self):
        if self.__decoration:
            self.editor.removeDecoration(self.__decoration)

    def __updateHighlight(self):
        """
        Updates the current line decoration
        """
        self.clearDeco()
        self.__decoration = TextDecoration(self.editor.textCursor())
        self.__decoration.setBackground(self.__brush)
        self.__decoration.setFullWidth()
        self.editor.addDecoration(self.__decoration)
