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
"""
Contains the default indenter.
"""
from pyqode.core.mode import Mode
from pyqode.qt import QtGui


class IndenterMode(Mode):
    """
    Implements classic indentation. It inserts/removes tabulations (a series of
    spaces defined by the tabLength settings) at the cursor position if there is
    no selection otherwise it fully indents/un-indents selected lines.
    """
    IDENTIFIER = "indenterMode"
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