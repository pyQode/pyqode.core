#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
""" Contains the automatic generic indenter """
import re
from pyqode.core.mode import Mode
from pyqode.qt.QtCore import Qt
from pyqode.qt.QtGui import QTextCursor, QKeyEvent


class AutoIndentMode(Mode):
    """
    Generic indenter mode that indents the text when the user press RETURN.

    You can customize this mode by overriding
    :meth:`pyqode.core.AutoIndentMode._getIndent`
    """
    #: Identifier
    IDENTIFIER = "autoIndentMode"
    #: Description
    DESCRIPTION = """ A basic auto indent mode that provides a basic auto
    indentation based on the previous line indentation.
    """

    def __init__(self):
        super(AutoIndentMode, self).__init__()
        self.minIndent = ""

    def _getIndent(self, tc):
        """
        Return the indentation text (a series of spaces or tabs)

        :param tc: QTextCursor
        """
        pos = tc.position()
        # tc.movePosition(QTextCursor.StartOfLine)
        # tc.setPosition(tc.position() - 1)
        tc.movePosition(QTextCursor.StartOfLine)
        tc.select(QTextCursor.LineUnderCursor)
        s = tc.selectedText()
        indent = re.match(r"\s*", s).group()
        tc.setPosition(pos)
        if len(indent) < len(self.minIndent):
            indent = self.minIndent
        return "", indent

    def _onStateChanged(self, state):
        if state is True:
            self.editor.keyPressed.connect(self.__onKeyPressed)
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
            pre, post = self._getIndent(tc)
            tc.insertText("%s\n%s" % (pre, post))
            keyEvent.accept()
