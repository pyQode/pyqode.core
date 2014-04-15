# -*- coding: utf-8 -*-
"""
Contains the default indenter.
"""
from pyqode.core import settings
from pyqode.core.frontend import Mode
from PyQt4 import QtGui


class IndenterMode(Mode):
    """
    Implements classic indentation/tabulation.

    It inserts/removes tabulations (a series of spaces defined by the
    tabLength settings) at the cursor position if there is no selection,
    otherwise it fully indents/un-indents selected lines.

    To trigger an indentation/un-indentation programatically, you must emit
    :attr:`pyqode.core.QCodeEdit.indent_requested` or
    :attr:`pyqode.core.QCodeEdit.unindent_requested`.
    """
    def _on_state_changed(self, state):
        if state:
            self.editor.indent_requested.connect(self.indent)
            self.editor.unindent_requested.connect(self.unindent)
        else:
            self.editor.indent_requested.disconnect(self.indent)
            self.editor.unindent_requested.disconnect(self.unindent)

    def indent_selection(self, cursor):
        doc = self.editor.document()
        min_indent = settings.min_indent_column
        tab_len = settings.tab_length
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
                if settings.use_spaces_instead_of_tabs:
                    [cursor.insertText(" ") for _ in range(nb_space_to_add)]
                else:
                    cursor.insertText('\t')
            block = block.next()
            i += 1
        cursor.endEditBlock()

    def unindent_selection(self, cursor):
        doc = self.editor.document()
        min_indent = settings.min_indent_column
        tab_len = settings.tab_length
        cursor.beginEditBlock()
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        while i < nb_lines:
            txt = block.text()
            if settings.use_spaces_instead_of_tabs:
                indentation = len(txt) - len(txt.lstrip()) - min_indent
            else:
                indentation = len(txt) - len(txt.replace('\t', ''))
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
            # simply insert indentation at the cursor position
            tab_len = settings.tab_length
            cursor.beginEditBlock()
            if settings.use_spaces_instead_of_tabs:
                cursor.insertText(tab_len * " ")
            else:
                cursor.insertText('\t')
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
            tab_len = settings.tab_length
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
