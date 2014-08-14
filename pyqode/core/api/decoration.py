"""
This module contains the text decoration API.

"""
from pyqode.qt import QtWidgets, QtCore, QtGui


class TextDecoration(QtWidgets.QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration. The text decoration is an
    utility class that adds a few utility methods over Qt's ExtraSelection.

    In addition to the helper methods, a tooltip can be added to a decoration.
    (useful for errors marks and so on...)

    Text decoration expose 1 **clicked** signal stored in a separate QObject:
        :attr:`pyqode.core.api.TextDecoration.signals`

    .. code-block:: python

        deco = TextDecoration()
        deco.signals.clicked.connect(a_slot)

        def a_slot(decoration):
            print(decoration)
    """
    class _TextDecorationSignals(QtCore.QObject):
        """
        Holds the signals for a TextDecoration (since we cannot make it a
        QObject, we need to store its signals in an external QObject).
        """
        #: Signal emitted when a TextDecoration has been clicked.
        clicked = QtCore.Signal(object)

    def __init__(self, cursor_or_bloc_or_doc, start_pos=None, end_pos=None,
                 start_line=None, end_line=None, draw_order=0, tooltip=None,
                 full_width=False):
        """
        Creates a text decoration

        :param cursor_or_bloc_or_doc: Selection
        :type cursor_or_bloc_or_doc: QTextCursor or QTextBlock or QTextDocument

        :param start_pos: Selection start pos
        :param end_pos: Selection end pos

        .. note:: Use the cursor selection if startPos and endPos are none.
        """
        super().__init__()
        self.signals = self._TextDecorationSignals()
        self.draw_order = draw_order
        self.tooltip = tooltip
        self.cursor = QtGui.QTextCursor(cursor_or_bloc_or_doc)
        if full_width:
            self.set_full_width(full_width)
        if start_pos is not None:
            self.cursor.setPosition(start_pos)
        if end_pos is not None:
            self.cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        if start_line is not None:
            self.cursor.movePosition(self.cursor.Start, self.cursor.MoveAnchor)
            self.cursor.movePosition(self.cursor.Down, self.cursor.MoveAnchor,
                                     start_line - 1)
        if end_line is not None:
            self.cursor.movePosition(self.cursor.Down, self.cursor.KeepAnchor,
                                     end_line - start_line)

    def contains_cursor(self, cursor):
        """
        Checks if the textCursor is in the decoration

        :param cursor: The text cursor to test
        :type cursor: QtGui.QTextCursor
        """
        start = self.cursor.selectionStart()
        end = self.cursor.selectionEnd()
        if cursor.atBlockEnd():
            end -= 1
        return start <= cursor.position() <= end

    def set_as_bold(self):
        """ Uses bold text """
        self.format.setFontWeight(QtGui.QFont.Bold)

    def set_foreground(self, color):
        """ Sets the foreground color.
        :param color: Color
        :type color: QtGui.QColor
        """
        self.format.setForeground(color)

    def set_background(self, brush):
        """
        Sets the background brush.

        :param brush: Brush
        :type brush: QtGui.QBrush
        """
        self.format.setBackground(brush)

    def set_outline(self, color):
        """
        Uses an outline rectangle.

        :param color: Color of the outline rect
        :type color: QtGui.QColor
        """
        self.format.setProperty(QtGui.QTextFormat.OutlinePen,
                                QtGui.QPen(color))

    def select_line(self):
        """
        Select the entire line but starts at the first non whitespace character
        and stops at the non-whitespace character.
        :return:
        """
        self.cursor.movePosition(self.cursor.StartOfBlock)
        text = self.cursor.block().text()
        lindent = len(text) - len(text.lstrip())
        rindent = len(text) - len(text.rstrip())
        self.cursor.setPosition(self.cursor.block().position() + lindent)
        self.cursor.movePosition(self.cursor.EndOfBlock,
                                 self.cursor.KeepAnchor)

    def set_full_width(self, flag=True, clear=True):
        """
        Enables FullWidthSelection (the selection does not stops at after the
        character instead it goes up to the right side of the widget).

        :param flag: True to use full width selection.
        :type flag: bool

        :param clear: True to clear any previous selection. Default is True.
        :type clear: bool
        """
        if clear:
            self.cursor.clearSelection()
        self.format.setProperty(QtGui.QTextFormat.FullWidthSelection, flag)

    def set_as_underlined(self, color=QtCore.Qt.blue):
        """
        Underlines the text
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SingleUnderline)
        self.format.setUnderlineColor(color)

    def set_as_spell_check(self, color=QtCore.Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def set_as_error(self, color=QtCore.Qt.red):
        """ Highlights text as a syntax error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def set_as_warning(self, color=QtGui.QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)
