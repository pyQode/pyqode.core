#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
""" Contains the automatic generic indenter """
import re
from pyqode.core.mode import Mode
from pyqode.qt.QtCore import Qt
from pyqode.qt.QtGui import QTextCursor, QKeyEvent


class AutoIndentMode(Mode):
    """ A basic auto indent mode that provides a basic auto indentation based 
    on the previous line indentation.

    This mode can be extended by overriding the _getIndent method.
    """
    #: Mode identifier
    IDENTIFIER = "autoIndentMode"
    DESCRIPTION = """ A basic auto indent mode that provides a basic auto
    indentation based on the previous line indentation.
    """

    def __init__(self):
        super(AutoIndentMode, self).__init__()
        self.minIndent = 0

    def _getIndent(self, tc):
        """
        Return the indentation text (a series of spaces, tabs)

        :param tc: QTextCursor
        """
        pos = tc.position()
        # tc.movePosition(QTextCursor.StartOfLine)
        # tc.setPosition(tc.position() - 1)
        tc.movePosition(QTextCursor.StartOfLine)
        tc.setPosition(tc.position() - 1)
        tc.select(QTextCursor.LineUnderCursor)
        s = tc.selectedText()
        indent = re.match(r"\s*", s).group()
        tc.setPosition(pos)
        if len(indent) < self.minIndent:
            indent = self.minIndent
        return indent

    def _onStateChanged(self, state):
        if state is True:
            self.editor.postKeyPressed.connect(self.__onKeyPressed)
        else:
            self.editor.postKeyPressed.disconnect(self.__onKeyPressed)

    def __onKeyPressed(self, keyEvent):
        """
        Auto indent if the released key is the return key.
        :param keyEvent: the key event
        """
        if keyEvent.isAccepted():
            return
        if keyEvent.key() == Qt.Key_Return or keyEvent.key() == Qt.Key_Enter:
            tc = self.editor.textCursor()
            indent = self._getIndent(tc)
            tc.insertText(indent)
