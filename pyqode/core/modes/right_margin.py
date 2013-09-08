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
This module contains the right margin mode.
"""
from pyqode.core import constants
from pyqode.core.mode import Mode
from pyqode.qt import QtGui


class RightMarginMode(Mode):
    """
    Display the right margin
    """
    #: Mode identifier
    IDENTIFIER = "rightMarginMode"
    DESCRIPTION = "Draw the right margin on the text document"

    def __init__(self):
        Mode.__init__(self)
        #: Defines the margin position. 80 is the default
        self.marginPos = constants.MARGIN_POS
        self.__pen = QtGui.QPen()

    def _onInstall(self, editor):
        """
        Installs the mode on the editor and setup drawing tools

        :param editor: The editor instance
        """
        Mode._onInstall(self, editor)
        color = self.editor.style.addProperty("margin", "#FF0000")
        self.__pen = QtGui.QPen(QtGui.QColor(color))
        self.marginPos = self.editor.settings.addProperty(
            "rightMarginPos", "80")

    def _onSettingsChanged(self, section, key):
        if key == "rightMarginPos" or not key:
            self.marginPos = self.editor.settings.value("rightMarginPos")

    def _onStyleChanged(self, section, key):
        """
        Changes the margin color

        :param section:
        :param key:
        :param value:
        """
        if key == "margin" or not key:
            self.__pen = self.editor.style.value("margin")
            self.editor.markWholeDocumentDirty()
            self.editor.repaint()

    def _onStateChanged(self, state):
        """
        Connects/Disconnects to the painted event of the editor

        :param state: Enable state
        """
        if state:
            self.editor.painted.connect(self.__paintMargin)
            self.editor.repaint()
        else:
            self.editor.painted.disconnect(self.__paintMargin)
            self.editor.repaint()

    def __paintMargin(self, event):
        """ Paints the right margin after editor paint event. """
        font = self.editor.currentCharFormat().font()
        fm = QtGui.QFontMetricsF(font)
        pos = self.marginPos
        offset = self.editor.contentOffset().x() + \
            self.editor.document().documentMargin()
        x80 = round(fm.width(' ') * pos) + offset
        p = QtGui.QPainter(self.editor.viewport())
        p.setPen(self.__pen)
        p.drawLine(x80, 0, x80, 2 ** 16)
