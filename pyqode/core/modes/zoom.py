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
from pyqode.core import constants
from pyqode.core.mode import Mode
from pyqode.qt import QtCore


class ZoomMode(Mode):
    """
    This mode make it possible to zoom in/out the editor view.

    Here are the controls:
      * **zoom out**: *ctrl+-* or *ctrl+mouse wheel backward*
      * **zoom in**: *ctrl++* or *ctrl+mouse wheel forward*
      * **reset**: *ctrl + 0*
    """
    #: Mode identifier
    IDENTIFIER = "zoomMode"
    #: Mode description
    DESCRIPTION = "Zoom the editor with ctrl+mouse wheel"

    def __init__(self):
        super(ZoomMode, self).__init__()
        self.prev_delta = 0
        self.default_font_size = constants.FONT_SIZE

    def _onStateChanged(self, state):
        """
        Connects/Disconnects to the mouseWheelActivated and keyPressed event
        """
        if state:
            self.editor.mouseWheelActivated.connect(
                self.__onWheelEvent)
            self.editor.keyPressed.connect(self.__onKeyPressed)
        else:
            self.editor.mouseWheelActivated.disconnect(
                self.__onWheelEvent)
            self.editor.keyPressed.disconnect(self.__onKeyPressed)

    def __onKeyPressed(self, event):
        """
        Resets editor font size to the default font size

        :param event: wheelEvent
        :type event: QKeyEvent
        """
        if int(event.modifiers()) & QtCore.Qt.ControlModifier > 0:
            if event.key() == QtCore.Qt.Key_0:
                self.editor.resetZoom()
                event.accept()
            if event.key() == QtCore.Qt.Key_Plus:
                self.editor.zoomIn()
                event.accept()
            if event.key() == QtCore.Qt.Key_Minus:
                self.editor.zoomOut()
                event.accept()

    def __onWheelEvent(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event
        if ctrl modifier is on.

        :param event: wheel event
        :type event: QWheelEvent
        """
        delta = event.delta()
        if int(event.modifiers()) & QtCore.Qt.ControlModifier > 0:
            if delta < self.prev_delta:
                self.editor.zoomOut()
                event.accept()
            else:
                self.editor.zoomIn()
                event.accept()
