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
This module contains the definition of a panel mode
"""
from pyqode.core.mode import Mode
from pyqode.qt import QtGui


class Panel(QtGui.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a QWidget.

    .. note:: A disabled panel will be hidden automatically.
    """

    @property
    def scrollable(self):
        """
        A scrollable panel will follow the editor's scroll-bars. Left and right
        panels follow the vertical scrollbar. Top and bottom panels follow the
        horizontal scrollbar.

        :type: bool
        """
        return self.__scrollable

    @scrollable.setter
    def scrollable(self, value):
        self.__scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        #: Panel order into the zone it is installed to. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.zoneOrder = -1
        self.__scrollable = False
        self._backgroundBrush = None
        self._foregroundPen = None

    def _onInstall(self, editor):
        """
        Extends :meth:`pyqode.core.Mode._onInstall` method to set the editor
        instance as the parent widget.

        .. warning:: Don't forget to call **super** if you override this method!

        :param editor: Editor instance
        :type editor: pyqode.core.QCodeEdit
        """
        Mode._onInstall(self, editor)
        self.setParent(editor)
        self.editor.refreshPanels()
        self._backgroundBrush = QtGui.QBrush(QtGui.QColor(
            self.palette().window().color()))
        self._foregroundPen = QtGui.QPen(QtGui.QColor(
            self.palette().windowText().color()))

    def _onStateChanged(self, state):
        """
        Shows/Hides the Panel

        .. warning:: Don't forget to call **super** if you override this method!

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
            self._backgroundBrush = QtGui.QBrush(QtGui.QColor(
                self.palette().window().color()))
            self._foregroundPen = QtGui.QPen(QtGui.QColor(
                self.palette().windowText().color()))
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self._backgroundBrush)

    def showEvent(self, *args, **kwargs):
        self.editor.refreshPanels()

    def setVisible(self, visible):
        QtGui.QWidget.setVisible(self, visible)
        self.editor.refreshPanels()
