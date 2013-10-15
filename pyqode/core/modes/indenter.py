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
"""
Contains the default indenter.
"""
from pyqode.core.mode import Mode
from pyqode.qt import QtGui


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

    def _onStateChanged(self, state):
        if state:
            self.editor.indentRequested.connect(self.indent)
            self.editor.unIndentRequested.connect(self.unIndent)
        else:
            self.editor.indentRequested.disconnect(self.indent)
            self.editor.unIndentRequested.disconnect(self.unIndent)

    def indentSelection(self, cursor):
        doc = self.editor.document()
        minIndent = self.editor.settings.value("minIndentColumn")
        tabLen = self.editor.settings.value("tabLength")
        cursor.beginEditBlock()
        nbLines = len(cursor.selection().toPlainText().splitlines())
        if nbLines == 0:
            nbLines = 1
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        # indent every lines
        while i < nbLines:
            txt = block.text()
            indentation = len(txt) - len(txt.lstrip()) - minIndent
            if indentation >= 0:
                nbSpacesToAdd = tabLen - (indentation % tabLen)
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                [cursor.insertText(" ") for _ in range(nbSpacesToAdd)]
            block = block.next()
            i += 1
        cursor.endEditBlock()

    def unIndentSelection(self, cursor):
        doc = self.editor.document()
        minIndent = self.editor.settings.value("minIndentColumn")
        tabLen = self.editor.settings.value("tabLength")
        cursor.beginEditBlock()
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        while i < nb_lines:
            txt = block.text()
            indentation = len(txt) - len(txt.lstrip()) - minIndent
            if indentation > 0:
                nbSpacesToRemove = indentation - (indentation - (
                    indentation % tabLen))
                if not nbSpacesToRemove:
                    nbSpacesToRemove = tabLen
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                [cursor.deleteChar() for _ in range(nbSpacesToRemove)]
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
            self.indentSelection(cursor)
        else:
            tabLen = self.editor.settings.value("tabLength")
            cursor.beginEditBlock()
            cursor.insertText(tabLen * " ")
            cursor.endEditBlock()

    def unIndent(self):
        """
        Un-indents text at cursor position.
        """
        cursor = self.editor.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        if cursor.hasSelection():
            self.unIndentSelection(cursor)
        else:
            tabLen = self.editor.settings.value("tabLength")
            cursor.beginEditBlock()
            # count the number of spaces deletable, stop at tab len
            spaces = 0
            travCursor = QtGui.QTextCursor(cursor)
            while spaces < tabLen and not travCursor.atBlockStart():
                pos = travCursor.position()
                travCursor.movePosition(cursor.Left, cursor.KeepAnchor)
                char = travCursor.selectedText()
                if char == " ":
                    spaces += 1
                else:
                    break
                travCursor.setPosition(pos - 1)
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, spaces)
            [cursor.deleteChar() for _ in range(spaces)]
            cursor.endEditBlock()