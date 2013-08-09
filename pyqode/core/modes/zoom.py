#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyQode - Python/Qt Code Editor widget
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains the mode that control the editor zoom.
"""
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
