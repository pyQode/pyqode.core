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
This module contains the definition of a panel mode
"""
from pyqode.core.mode import Mode
from pyqode.qt import QtGui


class Panel(QtGui.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a widget.

    Panels are drawn in the QCodeEdit viewport margins.
    """

    @property
    def scrollable(self):
        """
        A scrollable panel will follow the editor's scrollbars. Left and right
        panels follow the vertical scrollbar. Top and bottom panels follow the
        horizontal scrollbar.
        """
        return self.__scrollable

    @scrollable.setter
    def scrollable(self, value):
        """ Sets the scrollable flag. """
        self.__scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        #: Panel order into the zone it is installed. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.zoneOrder = -1
        self.__scrollable = False
        #: The background brush (automatically updated when panelBackground
        #: change)
        self.backgroundBrush = None
        #: The foreground pen (automatically updated when panelForeground
        #: changed)
        self.foregroundPen = None

    def _onInstall(self, editor):
        """
        Extends the Mode.install method to set the editor instance
        as the parent widget.

        Also adds the panelBackground and panel foreground.

        :param editor: pyqode.core.QCodeEdit instance
        """
        Mode._onInstall(self, editor)
        self.setParent(editor)
        self.editor.refreshPanels()
        self.backgroundBrush = QtGui.QBrush(QtGui.QColor(
            self.palette().window().color()))
        self.foregroundPen = QtGui.QPen(QtGui.QColor(
            self.palette().windowText().color()))

    def _onStateChanged(self, state):
        """ Shows/Hides the Panel

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if not self.editor.isVisible():
            return
        if state is True:
            self.show()
        else:
            self.hide()

    def paintEvent(self, event):
        if self.isVisible():
            # fill background
            self.backgroundBrush = QtGui.QBrush(QtGui.QColor(
                self.palette().window().color()))
            self.foregroundPen = QtGui.QPen(QtGui.QColor(
                self.palette().windowText().color()))
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self.backgroundBrush)

    def showEvent(self, *args, **kwargs):
        self.editor.refreshPanels()

    def setVisible(self, visible):
        QtGui.QWidget.setVisible(self, visible)
        self.editor.refreshPanels()
