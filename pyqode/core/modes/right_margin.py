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
