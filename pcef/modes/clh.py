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
""" Contains the Current Line Highlighter mode. """
from PySide.QtCore import Slot
from PySide.QtGui import QBrush
from PySide.QtGui import QColor
from pcef.core import TextDecoration
from pcef.core import Mode


class HighlightLineMode(Mode):
    """
    This mode highlights the current line.

    Line color is defined by :attr:`pcef.style.Style.activeLineColor`
    """
    #: Mode identifier
    IDENTIFIER = "Highlight line"

    #: Mode description
    DESCRIPTION = "Highlight the current line in the editor"

    def __init__(self):
        super(HighlightLineMode, self).__init__(
            self.IDENTIFIER, self.DESCRIPTION)
        self.__pos = -1
        self.__decoration = None
        self.__brush = None

    def _onStateChanged(self, state):
        """ Connects/Disconnects to/from CodeEdit signals """
        if state is True:
            self.editor.codeEdit.cursorPositionChanged.connect(self.changeActiveLine)
            self.changeActiveLine()
        else:
            self.editor.codeEdit.cursorPositionChanged.disconnect(self.changeActiveLine)
            self.editor.codeEdit.removeDecoration(self.__decoration)

    def _onStyleChanged(self):
        """ Updates the pygments style """
        self.__brush = QBrush(QColor(self.currentStyle.activeLineColor))
        self.__pos = -1
        self.changeActiveLine()

    @Slot()
    def changeActiveLine(self):
        """ Updates the active line decoration """
        tc = self.editor.codeEdit.textCursor()
        pos = tc.blockNumber()
        if pos != self.__pos:
            self.__pos = pos
            # remove previous selection
            self.editor.codeEdit.removeDecoration(self.__decoration)
            # add new selection
            self.__decoration = TextDecoration(tc)
            self.__decoration.setBackground(self.__brush)
            self.__decoration.setFullWidth()
            self.editor.codeEdit.addDecoration(self.__decoration)
