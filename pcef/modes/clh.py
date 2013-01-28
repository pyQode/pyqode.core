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
from pcef.base import TextDecoration
from pcef.base import Mode


class HighlightLineMode(Mode):
    """
    This mode highlights the current line.
    """
    #: Mode identifier
    IDENTIFIER = "Highlight line"

    def __init__(self):
        super(HighlightLineMode, self).__init__(
            self.IDENTIFIER, "Highlight the current line in the editor")
        self._pos = -1
        self._decoration = None
        self.brush = None

    def _onStateChanged(self, state):
        if state is True:
            self.editor.textEdit.cursorPositionChanged.connect(self.changeActiveLine)
            self.changeActiveLine()
        else:
            self.editor.textEdit.cursorPositionChanged.disconnect(self.changeActiveLine)
            self.editor.textEdit.removeDecoration(self._decoration)

    def _onStyleChanged(self):
        """ Updates the pygments style """
        self.brush = QBrush(QColor(self.currentStyle.activeLineColor))
        self.changeActiveLine()

    @Slot()
    def changeActiveLine(self):
        """ Changes the active line. """
        tc = self.editor.textEdit.textCursor()
        pos = tc.blockNumber
        if pos != self._pos:
            self._pos = pos
            # remove previous selection
            self.editor.textEdit.removeDecoration(self._decoration)
            # add new selection
            self._decoration = TextDecoration(tc)
            self._decoration.setBackground(self.brush)
            self._decoration.setFullWidth()
            self.editor.textEdit.addDecoration(self._decoration)
