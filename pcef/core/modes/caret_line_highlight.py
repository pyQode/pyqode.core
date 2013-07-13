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
from pcef.core import constants
from pcef.core.mode import Mode
from pcef.core.decoration import TextDecoration
from pcef.qt import QtGui

class CaretLineHighlighterMode(Mode):
    """
    This mode highlights the caret line (active line)
    """
    #: The mode identifier
    IDENTIFIER = "caretLineHighlighter"
    #: The mode description
    DESCRIPTION = "This mode highlights the caret line"

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
            self.editor.newTextSet.connect(self.__updateHighlight)
        else:
            self.editor.cursorPositionChanged.disconnect(self.__updateHighlight)
            self.editor.newTextSet.disconnect(self.__updateHighlight)
            self.clearDeco()

    def install(self, editor):
        """
        Installs the mode on the editor and add a style property:
            - caretLineBackground
        """
        Mode.install(self, editor)
        color = self.editor.style.addProperty("caretLineBackground",
                                              constants.CARET_LINE_BACKGROUND)
        self.__brush = QtGui.QBrush(QtGui.QColor(color))
        self.__updateHighlight()

    def onStyleChanged(self, section, key, value):
        """
        Changes the highlight brush color and refresh highlighting
        """
        if key == "caretLineBackground":
            self.__brush = QtGui.QBrush(QtGui.QColor(value))
            self.__updateHighlight()

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
