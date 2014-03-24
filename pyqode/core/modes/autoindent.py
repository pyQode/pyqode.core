#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
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
from pyqode.core.editor import Mode
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QKeyEvent


class AutoIndentMode(Mode):
    """
    Generic indenter mode that indents the text when the user press RETURN.

    You can customize this mode by overriding
    :meth:`pyqode.core.AutoIndentMode._getIndent`
    """
    def __init__(self):
        super(AutoIndentMode, self).__init__()
        self.min_indent = ""

    def _get_indent(self, tc):
        """
        Return the indentation text (a series of spaces or tabs)

        :param tc: QTextCursor

        :returns: Tuple (text before new line, text after new line)
        """
        pos = tc.position()
        # tc.movePosition(QTextCursor.StartOfLine)
        # tc.setPosition(tc.position() - 1)
        tc.movePosition(QTextCursor.StartOfLine)
        tc.select(QTextCursor.LineUnderCursor)
        s = tc.selectedText()
        indent = re.match(r"\s*", s).group()
        tc.setPosition(pos)
        if len(indent) < len(self.min_indent):
            indent = self.min_indent
        return "", indent

    def _on_state_changed(self, state):
        if state is True:
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        """
        Auto indent if the released key is the return key.
        :param event: the key event
        """
        if event.isAccepted():
            return
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            tc = self.editor.textCursor()
            pre, post = self._get_indent(tc)
            tc.insertText("%s\n%s" % (pre, post))

            # eats possible whitespaces
            tc.movePosition(tc.WordRight, tc.KeepAnchor)
            txt = tc.selectedText()
            if txt.startswith(' '):
                new_txt = txt.replace(" ", '')
                if len(txt) > len(new_txt):
                    tc.insertText(new_txt)

            event.accept()
