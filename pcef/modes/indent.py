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
""" Contains smart indent modes """
import re
from PySide.QtCore import Qt
from PySide.QtGui import QTextCursor, QKeyEvent
from pcef.core import Mode

_IDENTIFIER = "Auto indent"
_DESCRIPTION = """ A basic auto indent mode that provides a basic auto
indentation based on the previous line indentation.
"""

class AutoIndentMode(Mode):
    """ A basic auto indent mode that provides a basic auto indentation based on the previous
    line indentation.

    This mode can be extended by overriding the _getIndent method.
    """
    #: Mode identifier
    IDENTIFIER = _IDENTIFIER
    #: Mode description
    DESCRIPTION = _DESCRIPTION

    def __init__(self, identifier=IDENTIFIER, desc=_DESCRIPTION):
        super(AutoIndentMode, self).__init__(identifier, desc)

    def _onStyleChanged(self):
        pass  # style not needed

    def _getIndent(self, tc):
        """
        Return the indentation text (a series of spaces, tabs)

        :param tc: QTextCursor
        """
        pos = tc.position()
        tc.movePosition(QTextCursor.StartOfLine)
        tc.setPosition(tc.position() - 1)
        tc.select(QTextCursor.LineUnderCursor)
        s = tc.selectedText()
        indent = re.match(r"\s*", s).group()
        tc.setPosition(pos)
        return indent

    def _onStateChanged(self, state):
        if state is True:
            self.editor.codeEdit.keyPressed.connect(self.__onKeyPressed)
        else:
            self.editor.codeEdit.keyPressed.disconnect(self.__onKeyPressed)

    def __onKeyPressed(self, keyEvent):
        """
        Auto indent if the released key is the return key.
        :param keyEvent: the key event
        """
        assert isinstance(keyEvent, QKeyEvent)
        if hasattr(keyEvent, "stop") and keyEvent.stop:
            return
        if keyEvent.key() == Qt.Key_Return or keyEvent.key() == Qt.Key_Enter:
            # go next line
            tc = self.editor.codeEdit.textCursor()
            tc.insertText("\n")
            indent = self._getIndent(tc)
            tc.insertText(indent)
            tc.movePosition(QTextCursor.EndOfLine)
            keyEvent.stop = True