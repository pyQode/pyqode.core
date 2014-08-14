# -*- coding: utf-8 -*-
"""
This module contains the symbol matcher mode
"""
from pyqode.core.api import get_block_symbol_data
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.mode import Mode
from pyqode.qt import QtGui


PAREN = 0
SQUARE = 1
BRACE = 2


class SymbolMatcherMode(Mode):
    """
    Do symbols matches highlighting (parenthesis, braces, ...).

    .. note:: This mode requires the document to be filled with
        :class:`pyqode.core.api.TextBlockUserData`, i.e. a
        :class:`pyqode.core.api.SyntaxHighlighter` must be installed on
        the editor instance.

    """
    @property
    def match_background(self):
        """
        Background color of matching symbols.
        """
        return self._match_background

    @match_background.setter
    def match_background(self, value):
        self._match_background = value
        self._refresh_decorations()

    @property
    def match_foreground(self):
        """
        Foreground color of matching symbols.
        """
        return self._match_foreground

    @match_foreground.setter
    def match_foreground(self, value):
        self._match_foreground = value
        self._refresh_decorations()

    @property
    def unmatch_background(self):
        """
        Background color of non-matching symbols.
        """
        return self._unmatch_background

    @unmatch_background.setter
    def unmatch_background(self, value):
        self._unmatch_background = value
        self._refresh_decorations()

    @property
    def unmatch_foreground(self):
        """
        Foreground color of matching symbols.
        """
        return self._unmatch_foreground

    @unmatch_foreground.setter
    def unmatch_foreground(self, value):
        self._unmatch_foreground = value
        self._refresh_decorations()

    def __init__(self):
        super().__init__()
        self._decorations = []
        self._match_background = QtGui.QBrush(QtGui.QColor('#B4EEB4'))
        self._match_foreground = QtGui.QColor('red')
        self._unmatch_background = QtGui.QBrush(QtGui.QColor('transparent'))
        self._unmatch_foreground = QtGui.QColor('red')

    def _clear_decorations(self):
        for deco in self._decorations:
            self.editor.decorations.remove(deco)
        self._decorations[:] = []

    def symbol_pos(self, cursor, character='(', symbol_type=0):
        """
        Find the corresponding symbol position (line, column).
        """
        retval = None, None
        original_cursor = self.editor.textCursor()
        self.editor.setTextCursor(cursor)
        block = cursor.block()
        data = get_block_symbol_data(self.editor, block)
        mapping = {}
        methods = [self._match_parentheses,
                   self._match_square_brackets,
                   self._match_braces]
        for i in range(3):
            mapping[i] = (methods[i], data[i])
        m, d = mapping[symbol_type]
        m(d, block.position())
        for deco in self._decorations:
            if deco.character == character:
                retval = deco.line, deco.column
                break
        self.editor.setTextCursor(original_cursor)
        self._clear_decorations()
        return retval

    def _refresh_decorations(self):
        for deco in self._decorations:
            self.editor.decorations.remove(deco)
            if deco.match:
                deco.set_foreground(self._match_foreground)
                deco.set_background(self._match_background)
            else:
                deco.set_foreground(self._unmatch_foreground)
                deco.set_background(self._unmatch_background)
            self.editor.decorations.append(deco)

    def on_state_changed(self, state):
        if state:
            self.editor.cursorPositionChanged.connect(self.do_symbols_matching)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self.do_symbols_matching)

    def _match_parentheses(self, parentheses, cursor_pos):
        for i, info in enumerate(parentheses):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "(" and info.position == pos:
                self._create_decoration(
                    cursor_pos + info.position,
                    self._match_left_parenthesis(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == ")" and info.position == pos - 1:
                self._create_decoration(
                    cursor_pos + info.position,
                    self._match_right_parenthesis(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_parenthesis(self, current_block, i, cpt):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[PAREN]
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
                return self._match_left_parenthesis(current_block, 0, cpt)
            return False
        except RuntimeError:
            # recursion limit exceeded when working with big files
            return False

    def _match_right_parenthesis(self, current_block, i, nb_right_paren):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[PAREN]
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
                data = get_block_symbol_data(self.editor, current_block)
                parentheses = data[PAREN]
                return self._match_right_parenthesis(
                    current_block, len(parentheses) - 1, nb_right_paren)
            return False
        except RuntimeError:
            # recursion limit exceeded when working in big files
            return False

    def _match_square_brackets(self, brackets, current_pos):
        for i, info in enumerate(brackets):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "[" and info.position == pos:
                self._create_decoration(
                    current_pos + info.position,
                    self._match_left_bracket(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "]" and info.position == pos - 1:
                self._create_decoration(
                    current_pos + info.position, self._match_right_bracket(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_bracket(self, current_block, i, cpt):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[SQUARE]
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
                return self._match_left_bracket(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def _match_right_bracket(self, current_block, i, nb_right):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[SQUARE]
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
                data = get_block_symbol_data(self.editor, current_block)
                parentheses = data[SQUARE]
                return self._match_right_bracket(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def _match_braces(self, braces, cursor_position):
        for i, info in enumerate(braces):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "{" and info.position == pos:
                self._create_decoration(
                    cursor_position + info.position,
                    self._match_left_brace(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "}" and info.position == pos - 1:
                self._create_decoration(
                    cursor_position + info.position, self._match_right_brace(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_brace(self, current_block, i, cpt):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[BRACE]
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
                return self._match_left_brace(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def _match_right_brace(self, current_block, i, nb_right):
        try:
            data = get_block_symbol_data(self.editor, current_block)
            parentheses = data[BRACE]
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
                data = get_block_symbol_data(self.editor, current_block)
                parentheses = data[BRACE]
                return self._match_right_brace(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def do_symbols_matching(self):
        """
        Performs symbols matching.
        """
        self._clear_decorations()
        current_block = self.editor.textCursor().block()
        data = get_block_symbol_data(self.editor, current_block)
        pos = self.editor.textCursor().block().position()
        self._match_parentheses(data[PAREN], pos)
        self._match_square_brackets(data[SQUARE], pos)
        self._match_braces(data[BRACE], pos)

    def _create_decoration(self, pos, match=True):
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)
        deco = TextDecoration(cursor, draw_order=10)
        deco.line = cursor.blockNumber() + 1
        deco.column = cursor.columnNumber()
        deco.character = cursor.selectedText()
        deco.match = match
        if match:
            deco.set_foreground(self._match_foreground)
            deco.set_background(self._match_background)
        else:
            deco.set_foreground(self._unmatch_foreground)
            deco.set_background(self._unmatch_background)
        self._decorations.append(deco)
        self.editor.decorations.append(deco)
        return cursor
