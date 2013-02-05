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


class AutoIndentMode(Mode):
    """ A basic auto indent mode that provides a basic auto indentation based on the previous
    line indentation.

    This mode can be extended by overriding the getIndent method.
    """
    IDENTIFIER = "Auto indent"
    DESCRIPTION = """ A basic auto indent mode that provides a basic auto indentation based on the previous
    line indentation.
    """

    def __init__(self):
        super(AutoIndentMode, self).__init__(self.IDENTIFIER, self.DESCRIPTION)

    def onStyleChanged(self):
        pass  # style not needed

    def getIndent(self, tc):
        pos = tc.position()
        tc.movePosition(QTextCursor.StartOfLine)
        tc.setPosition(tc.position() - 1)
        tc.select(QTextCursor.LineUnderCursor)
        s = tc.selectedText()
        indent = re.match(r"\s*", s).group()
        tc.setPosition(pos)
        return indent

    def onStateChanged(self, state):
        if state is True:
            self.editor.codeEdit.keyPressed.connect(self.onKeyPressed)
        else:
            self.editor.codeEdit.keyPressed.disconnect(self.onKeyPressed)

    def onKeyPressed(self, keyEvent):
        """
        Auto indent if the released key is the return key.
        :param keyEvent: the key event
        """
        assert isinstance(keyEvent, QKeyEvent)
        if keyEvent.isAccepted():
            return
        if keyEvent.key() == Qt.Key_Return or keyEvent.key() == Qt.Key_Enter:
            # go next line
            tc = self.editor.codeEdit.textCursor()
            tc.insertText("\n")
            indent = self.getIndent(tc)
            tc.insertText(indent)
            tc.movePosition(QTextCursor.EndOfLine)
            keyEvent.setAccepted(True)