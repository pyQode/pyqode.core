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
This module contains the symbol matcher mode
"""
from PyQt4 import QtGui, QtCore

from pyqode.core.editor import Mode
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.textblockuserdata import TextBlockUserData


class SymbolMatcherMode(Mode):
    """
    Do symbols matches highlighting (parenthesis, braces, ...).

    .. note:: This mode requires the document to be filled with
        :class:`pyqode.core.TextBlockUserData`, i.e. a
        :class:`pyqode.core.SyntaxHighlighter` must be installed on
        the editor instance.

    """
    # todo why isn't there style settings for unmatched parenthesis?

    @property
    def match_background(self):
        return self.editor.style.value("matchedBraceBackground")

    @match_background.setter
    def match_background(self, value):
        self.editor.style.set_value("matchedBraceBackground", value)

    @property
    def match_foreground(self):
        return self.editor.style.value("matchedBraceForeground")

    @match_foreground.setter
    def match_foreground(self, value):
        self.editor.style.set_value("matchedBraceForeground", value)

    def __init__(self):
        Mode.__init__(self)
        self._decorations = []

    def _on_install(self, editor):
        Mode._on_install(self, editor)
        self.editor.style.add_property("matchedBraceBackground",
                                       QtGui.QColor("#B4EEB4"))
        self.editor.style.add_property("matchedBraceForeground",
                                       QtGui.QColor("#FF0000"))

    def _on_style_changed(self, section, key):
        if not key or key in ["matchedBraceBackground",
                              "matchedBraceForeground"]:
            self._refresh_decorations()

    def _clear_decorations(self):
        for d in self._decorations:
            self.editor.remove_decoration(d)
        self._decorations[:] = []

    def symbol_pos(self, cursor, character='(', type=0):
        retval = None, None
        original_cursor = self.editor.textCursor()
        self.editor.setTextCursor(cursor)
        block = cursor.block()
        mapping = {0: block.userData().parentheses,
                   1: block.userData().square_brackets,
                   2: block.userData().braces}
        self.match_braces(mapping[type], block.position())
        for d in self._decorations:
            if d.character == character:
                retval = d.line, d.column
                break
        self.editor.setTextCursor(original_cursor)
        self._clear_decorations()
        return retval

    def _refresh_decorations(self):
        for d in self._decorations:
            self.editor.remove_decoration(d)
            if d.match:
                # d.setForeground(QtGui.QBrush(QtGui.QColor("#FF8647")))
                f = self.editor.style.value("matchedBraceForeground")
                if f:
                    d.set_foreground(f)
                b = self.editor.style.value("matchedBraceBackground")
                if b:
                    d.set_background(b)
                else:
                    d.set_background(QtGui.QColor("transparent"))
            else:
                d.set_foreground(QtCore.Qt.red)
            self.editor.add_decoration(d)

    def _on_state_changed(self, state):
        if state:
            self.editor.cursorPositionChanged.connect(self.do_symbols_matching)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self.do_symbols_matching)

    def match_parentheses(self, parentheses, cursor_pos):
        for i, info in enumerate(parentheses):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "(" and info.position == pos:
                self._create_decoration(
                    cursor_pos + info.position,
                    self.match_left_parenthesis(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == ")" and info.position == pos - 1:
                self._create_decoration(
                    cursor_pos + info.position,
                    self.match_right_parenthesis(
                        self.editor.textCursor().block(), i - 1, 0))

    def match_left_parenthesis(self, current_block, i, cpt):
        try:
            data = current_block.userData()
            parentheses = data.parentheses
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "(":
                    cpt += 1
                    continue
                if info.character == ")" and cpt == 0:
                    self._create_decoration(current_block.position() +
                                            info.position)
                    return True
                elif info.character == ")":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self.match_left_parenthesis(current_block, 0, cpt)
            return False
        except RuntimeError:  # recursion limit exceeded when working with
                              # big files
            return False

    def match_right_parenthesis(self, current_block, i, nb_right_paren):
        try:
            data = current_block.userData()
            parentheses = data.parentheses
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == ")":
                    nb_right_paren += 1
                    continue
                if info.character == "(":
                    if nb_right_paren == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right_paren -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.parentheses
                return self.match_right_parenthesis(
                    current_block, len(parentheses) - 1, nb_right_paren)
            return False
        except RuntimeError:
            # recursion limit exceeded when working in big files
            return False

    def match_square_brackets(self, brackets, current_pos):
        for i, info in enumerate(brackets):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "[" and info.position == pos:
                self._create_decoration(
                    current_pos + info.position,
                    self.match_left_bracket(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "]" and info.position == pos - 1:
                self._create_decoration(
                    current_pos + info.position, self.match_right_bracket(
                        self.editor.textCursor().block(), i - 1, 0))

    def match_left_bracket(self, current_block, i, cpt):
        try:
            data = current_block.userData()
            parentheses = data.square_brackets
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "[":
                    cpt += 1
                    continue
                if info.character == "]" and cpt == 0:
                    self._create_decoration(
                        current_block.position() + info.position)
                    return True
                elif info.character == "]":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self.match_left_bracket(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def match_right_bracket(self, current_block, i, nb_right):
        try:
            data = current_block.userData()
            parentheses = data.square_brackets
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "]":
                    nb_right += 1
                    continue
                if info.character == "[":
                    if nb_right == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.square_brackets
                return self.match_right_bracket(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def match_braces(self, braces, cursor_position):
        for i, info in enumerate(braces):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "{" and info.position == pos:
                self._create_decoration(
                    cursor_position + info.position,
                    self.match_left_brace(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "}" and info.position == pos - 1:
                self._create_decoration(
                    cursor_position + info.position, self.match_right_brace(
                        self.editor.textCursor().block(), i - 1, 0))

    def match_left_brace(self, current_block, i, cpt):
        try:
            data = current_block.userData()
            parentheses = data.braces
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "{":
                    cpt += 1
                    continue
                if info.character == "}" and cpt == 0:
                    self._create_decoration(
                        current_block.position() + info.position)
                    return True
                elif info.character == "}":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self.match_left_brace(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def match_right_brace(self, current_block, i, nb_right):
        try:
            data = current_block.userData()
            parentheses = data.braces
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "}":
                    nb_right += 1
                    continue
                if info.character == "{":
                    if nb_right == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.braces
                return self.match_right_brace(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def do_symbols_matching(self):
        for d in self._decorations:
            self.editor.remove_decoration(d)
        self._decorations[:] = []
        data = self.editor.textCursor().block().userData()
        if data and isinstance(data, TextBlockUserData):
            pos = self.editor.textCursor().block().position()
            self.match_parentheses(data.parentheses, pos)
            self.match_square_brackets(data.square_brackets, pos)
            self.match_braces(data.braces, pos)

    def _create_decoration(self, pos, match=True):
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)
        d = TextDecoration(cursor, draw_order=10)
        d.line = cursor.blockNumber() + 1
        d.column = cursor.columnNumber()
        d.character = cursor.selectedText()
        d.match = match
        if match:
            # d.setForeground(QtGui.QBrush(QtGui.QColor("#FF8647")))
            f = self.editor.style.value("matchedBraceForeground")
            if f:
                d.set_foreground(f)
            b = self.editor.style.value("matchedBraceBackground")
            if b:
                d.set_background(b)
        else:
            d.set_foreground(QtCore.Qt.red)
        assert isinstance(cursor, QtGui.QTextCursor)
        self._decorations.append(d)
        self.editor.add_decoration(d)
        return cursor
