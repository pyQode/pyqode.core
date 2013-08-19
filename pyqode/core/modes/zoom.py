#!/usr/bin/env python
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
from pyqode.core import constants
from pyqode.core.mode import Mode
from pyqode.qt import QtCore


class ZoomMode(Mode):
    """
    Zoom in/out mode. (the editor font is increased/decreased)
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
