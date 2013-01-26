#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
""" This module contains the editor zoom mode """
import copy
from PySide.QtCore import Qt
from PySide.QtGui import QKeyEvent
from PySide.QtGui import QWheelEvent
from pcef.base import Mode
from pcef import style


class EditorZoomMode(Mode):
    """
    This mode provide editor zoom (the editor font is increased/decreased)
    """
    #: Mode identifier
    IDENTIFIER = "EditorZoom"

    def __init__(self):
        super(EditorZoomMode, self).__init__(
            self.IDENTIFIER, "Zoom the editor with ctrl+mouse wheel")
        self.prev_delta = 0
        self.default_font_size = style.DEFAULT_FONT_SIZE

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        super(EditorZoomMode, self).install(editor)
        self.editor.textEdit.mouseWheelActivated.connect(
            self.onWheelEvent)
        self.editor.textEdit.keyPressed.connect(self.onKeyPressed)

    def updateStyling(self):
        pass

    def onKeyPressed(self, event):
        """
        Resets editor font size to the default font size
        :param event: wheelEvent
        :type event: QKeyEvent
        :return:
        """
        if (event.key() == Qt.Key_0 and
                event.modifiers() & Qt.ControlModifier > 0):
            style = copy.copy(self.currentStyle)
            style.fontSize = self.default_font_size
            event.setAccepted(True)
            self.editor.currentStyle = style

    def onWheelEvent(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event
        if ctrl modifier is on.
        :param event: wheel event
        :type event: QWheelEvent
        """
        delta = event.delta()
        if event.modifiers() & Qt.ControlModifier > 0:
            style = copy.copy(self.currentStyle)
            self.editor.currentStyle = style
            if delta < self.prev_delta:
                style.fontSize -= 1
            else:
                style.fontSize += 1
            if style.fontSize <= 0:
                style.fontSize = 1
            event.setAccepted(True)
            self.editor.currentStyle = style