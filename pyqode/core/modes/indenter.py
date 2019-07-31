# -*- coding: utf-8 -*-
"""
Contains the default indenter.
"""
import logging
from pyqode.core.api import TextHelper
from pyqode.core.api.mode import Mode
from pyqode.qt import QtGui


def _logger():
    return logging.getLogger(__name__)


def debug(msg, *args):
    return _logger().log(5, msg, *args)


class IndenterMode(Mode):
    """ Implements classic indentation/tabulation (Tab/Shift+Tab)

    It inserts/removes tabulations (a series of spaces defined by the
    tabLength settings) at the cursor position if there is no selection,
    otherwise it fully indents/un-indents selected lines.

    To trigger an indentation/un-indentation programatically, you must emit
    :attr:`pyqode.core.api.CodeEdit.indent_requested` or
    :attr:`pyqode.core.api.CodeEdit.unindent_requested`.
    """
    def __init__(self):
        super(IndenterMode, self).__init__()

    @property
    def _indent_char(self):

        if self.editor.use_spaces_instead_of_tabs:
            return ' '
        return '\t'

    @property
    def _single_indent(self):

        if self.editor.use_spaces_instead_of_tabs:
            return self.editor.tab_length * ' '
        return '\t'

    def on_state_changed(self, state):
        if state:
            self.editor.indent_requested.connect(self.indent)
            self.editor.unindent_requested.connect(self.unindent)
        else:
            self.editor.indent_requested.disconnect(self.indent)
            self.editor.unindent_requested.disconnect(self.unindent)

    def indent_selection(self, cursor):
        """
        Indent selected text

        :param cursor: QTextCursor
        """
        doc = self.editor.document()
        cursor.beginEditBlock()
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        c = self.editor.textCursor()
        if c.atBlockStart() and c.position() == c.selectionEnd():
            nb_lines += 1
        block = doc.findBlock(cursor.selectionStart())
        i = 0
        # indent every lines
        while i < nb_lines:
            cursor = QtGui.QTextCursor(block)
            cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
            cursor.insertText(self._single_indent)
            block = block.next()
            i += 1
        cursor.endEditBlock()

    def unindent_selection(self, cursor):
        """
        Un-indents selected text

        :param cursor: QTextCursor
        """
        doc = self.editor.document()
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        if nb_lines == 0:
            nb_lines = 1
        block = doc.findBlock(cursor.selectionStart())
        assert isinstance(block, QtGui.QTextBlock)
        i = 0
        debug('unindent selection: %d lines', nb_lines)
        start_pos = block.position()
        while i < nb_lines:
            cursor.setPosition(block.position(), cursor.MoveAnchor)
            txt = block.text()
            debug('line to unindent: %s', txt)
            debug('self.editor.use_spaces_instead_of_tabs: %r',
                  self.editor.use_spaces_instead_of_tabs)
            indentation = len(txt) - len(txt.lstrip(self._indent_char))
            debug('unindent line %d: %d characters', i, indentation)
            cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
            for _ in range(len(self._single_indent)):
                txt = block.text()
                if len(txt) and txt[0] == self._indent_char:
                    cursor.deleteChar()
            end_pos = block.position() + block.length()
            block = block.next()
            i += 1
        # Restore selection
        cursor.setPosition(start_pos, cursor.MoveAnchor)
        cursor.setPosition(end_pos, cursor.KeepAnchor)
        return cursor

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
            tab_len = self.editor.tab_length
            cursor.beginEditBlock()
            if self.editor.use_spaces_instead_of_tabs:
                nb_space_to_add = tab_len - cursor.positionInBlock() % tab_len
                cursor.insertText(nb_space_to_add * " ")
            else:
                cursor.insertText('\t')
            cursor.endEditBlock()

    def count_deletable_spaces(self, cursor, max_spaces):
        # count the number of spaces deletable, stop at tab len
        max_spaces = abs(max_spaces)
        if max_spaces > self.editor.tab_length:
            max_spaces = self.editor.tab_length
        spaces = 0
        trav_cursor = QtGui.QTextCursor(cursor)
        while spaces < max_spaces or trav_cursor.atBlockStart():
            pos = trav_cursor.position()
            trav_cursor.movePosition(cursor.Left, cursor.KeepAnchor)
            char = trav_cursor.selectedText()
            if char == self._indent_char:
                spaces += 1
            else:
                break
            trav_cursor.setPosition(pos - 1)
        return spaces

    def unindent(self):
        """
        Un-indents text at cursor position.
        """

        debug('unindent')
        cursor = self.editor.textCursor()
        debug('cursor has selection %r', cursor.hasSelection())
        if cursor.hasSelection():
            cursor.beginEditBlock()
            self.unindent_selection(cursor)
            cursor.endEditBlock()
            self.editor.setTextCursor(cursor)
        else:
            tab_len = self.editor.tab_length
            indentation = cursor.positionInBlock()
            max_spaces = tab_len - (indentation - (indentation % tab_len))
            spaces = self.count_deletable_spaces(cursor, max_spaces)
            debug('deleting %d space before cursor' % spaces)
            cursor.beginEditBlock()
            if spaces:
                # delete spaces before cursor
                for _ in range(spaces):
                    cursor.deletePreviousChar()
            else:
                # un-indent whole line
                debug('un-indent whole line')
                cursor = self.unindent_selection(cursor)
            cursor.endEditBlock()
            self.editor.setTextCursor(cursor)
            debug(cursor.block().text())
