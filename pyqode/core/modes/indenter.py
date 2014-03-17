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
"""
Contains the default indenter.
"""
from pyqode.core.editor import Mode
from PyQt4 import QtGui


class IndenterMode(Mode):
    """
    Implements classic indentation/tabulation.

    It inserts/removes tabulations (a series of spaces defined by the
    tabLength settings) at the cursor position if there is no selection,
    otherwise it fully indents/un-indents selected lines.

    To trigger an indentation/un-indentation programatically, you must emit
    :attr:`pyqode.core.QCodeEdit.indentRequested` or
    :attr:`pyqode.core.QCodeEdit.unIndentRequested`.
    """
    #: Mode identifier
    IDENTIFIER = "indenterMode"

    #: Mode description
    DESCRIPTION = "Implements classic indentation"

    def _on_state_changed(self, state):
        if state:
            self.editor.indentRequested.connect(self.indent)
            self.editor.unIndentRequested.connect(self.unindent)
        else:
            self.editor.indentRequested.disconnect(self.indent)
            self.editor.unIndentRequested.disconnect(self.unindent)

    def indent_selection(self, cursor):
        doc = self.editor.document()
        min_indent = self.editor.settings.value("minIndentColumn")
        tab_len = self.editor.settings.value("tabLength")
        cursor.beginEditBlock()
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        if nb_lines == 0:
            nb_lines = 1
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        # indent every lines
        while i < nb_lines:
            txt = block.text()
            indentation = len(txt) - len(txt.lstrip()) - min_indent
            if indentation >= 0:
                nb_space_to_add = tab_len - (indentation % tab_len)
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                [cursor.insertText(" ") for _ in range(nb_space_to_add)]
            block = block.next()
            i += 1
        cursor.endEditBlock()

    def unindent_selection(self, cursor):
        doc = self.editor.document()
        min_indent = self.editor.settings.value("minIndentColumn")
        tab_len = self.editor.settings.value("tabLength")
        cursor.beginEditBlock()
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        while i < nb_lines:
            txt = block.text()
            indentation = len(txt) - len(txt.lstrip()) - min_indent
            if indentation > 0:
                nb_spaces_to_remove = indentation - (indentation - (
                    indentation % tab_len))
                if not nb_spaces_to_remove:
                    nb_spaces_to_remove = tab_len
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                [cursor.deleteChar() for _ in range(nb_spaces_to_remove)]
            block = block.next()
            i += 1
        cursor.endEditBlock()

    def indent(self):
        """
        Indents text at cursor position.
        """
        cursor = self.editor.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        if cursor.hasSelection():
            self.indent_selection(cursor)
        else:
            tab_len = self.editor.settings.value("tabLength")
            cursor.beginEditBlock()
            cursor.insertText(tab_len * " ")
            cursor.endEditBlock()

    def unindent(self):
        """
        Un-indents text at cursor position.
        """
        cursor = self.editor.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        if cursor.hasSelection():
            self.unindent_selection(cursor)
        else:
            tab_len = self.editor.settings.value("tabLength")
            cursor.beginEditBlock()
            # count the number of spaces deletable, stop at tab len
            spaces = 0
            trav_cursor = QtGui.QTextCursor(cursor)
            while spaces < tab_len and not trav_cursor.atBlockStart():
                pos = trav_cursor.position()
                trav_cursor.movePosition(cursor.Left, cursor.KeepAnchor)
                char = trav_cursor.selectedText()
                if char == " ":
                    spaces += 1
                else:
                    break
                trav_cursor.setPosition(pos - 1)
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, spaces)
            [cursor.deleteChar() for _ in range(spaces)]
            cursor.endEditBlock()
