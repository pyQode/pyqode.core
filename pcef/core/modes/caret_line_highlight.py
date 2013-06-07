#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the care line highlighter mode
"""
import pcef
from pcef.core.mode import Mode
from pcef.core.decoration import TextDecoration


class CaretLineHighlighterMode(Mode):
    """
    This mode highlights the caret line (active line)
    """
    #: The mode identifier
    IDENTIFIER = "caretLineHighlighter"
    #: The mode description
    _DESCRIPTION = "This mode highlights the caret line"

    def __init__(self):
        Mode.__init__(self)
        self.__decoration = None
        self.__brush = None
        self.__pos = -1

    def onStateChanged(self, state):
        """
        On state changed we (dis)connect to the cursorPositionChanged signal
        """
        if state:
            self.editor.cursorPositionChanged.connect(self.__updateHighlight)
        else:
            self.editor.cursorPositionChanged.disconnect(self.__updateHighlight)

    def install(self, editor):
        """
        Installs the mode on the editor and add a style property:
            - caretLineBackground
        """
        Mode.install(self, editor)
        color = self.editor.style.addProperty("caretLineBackground", "#E4EDF8")
        self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(color))
        self.__updateHighlight()

    def onStyleChanged(self, section, key, value):
        """
        Changes the highlight brush color and refresh highlighting
        """
        if key == "caretLineBackground":
            self.__brush = pcef.QtGui.QBrush(pcef.QtGui.QColor(value))
            # force refresh
            self.__pos = -1
            self.__updateHighlight()

    def __updateHighlight(self):
        """
        Updates the current line decoration
        """
        l, c = self.editor.cursorPosition
        if l != self.__pos:
            self.__pos = l
            if self.__decoration:
                self.editor.removeDecoration(self.__decoration)
            self.__decoration = TextDecoration(self.editor.textCursor())
            self.__decoration.setBackground(self.__brush)
            self.__decoration.setFullWidth()
            self.editor.addDecoration(self.__decoration)
