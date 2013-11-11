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
This module defines text edit decorations
"""
from pyqode.qt import QtCore, QtGui


class TextDecorationSignals(QtCore.QObject):
    clicked = QtCore.Signal(object)


class TextDecoration(QtGui.QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration. The text decoration is an
    utility class that adds a few utility methods over the Qt ExtraSelection.

    In addition to the helper methods, a tooltip can be added to a decoration.
    Usefull for errors marks and so on...

    Text decoration expose 1 **clicked** signal stored in a separate QObject:
    :attr:`pyqode.core.TextDecoration.signals`

    .. code-block:: python

        deco = TextDecoration()
        deco.signals.clicked.connect(a_slot)

        def a_slot(decoration):
            print(decoration)
    """

    def __init__(self, cursorOrBlockOrDoc, startPos=None, endPos=None,
                 startLine=None, endLine=None, draw_order=0, tooltip=None):
        """
        Creates a text decoration

        :param cursorOrBlockOrDoc: Selection
        :type cursorOrBlockOrDoc: QTextCursor or QTextBlock or QTextDocument

        :param startPos: Selection start pos

        :param endPos: Selection end pos

        .. note:: Use the cursor selection if startPos and endPos are none.
        """
        QtGui.QTextEdit.ExtraSelection.__init__(self)
        self.signals = TextDecorationSignals()
        self.draw_order = draw_order
        self.tooltip = tooltip
        cursor = QtGui.QTextCursor(cursorOrBlockOrDoc)
        if startPos is not None:
            cursor.setPosition(startPos)
        if endPos is not None:
            cursor.setPosition(endPos, QtGui.QTextCursor.KeepAnchor)
        if startLine is not None:
            cursor.movePosition(cursor.Start, cursor.MoveAnchor)
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, startLine - 1)
        if endLine is not None:
            cursor.movePosition(cursor.Down, cursor.KeepAnchor,
                                endLine - startLine)
        self.cursor = cursor

    def containsCursor(self, textCursor):
        """
        Checks if the textCursor is in the decoration

        :param textCursor: The text cursor to test
        :type textCursor: QtGui.QTextCursor
        """
        return self.cursor.selectionStart() <= textCursor.position() < \
            self.cursor.selectionEnd()

    def setBold(self):
        """ Uses bold text """
        self.format.setFontWeight(QtGui.QFont.Bold)

    def setForeground(self, color):
        """ Sets the foreground color.
        :param color: Color
        :type color: QtGui.QColor
        """
        self.format.setForeground(color)

    def setBackground(self, brush):
        """
        Sets the background brush.

        :param brush: Brush
        :type brush: QtGui.QBrush
        """
        self.format.setBackground(brush)

    def setOutline(self, color):
        """
        Uses an outline rectangle.

        :param color: Color of the outline rect
        :type color: QtGui.QColor
        """
        self.format.setProperty(QtGui.QTextFormat.OutlinePen,
                                QtGui.QPen(color))

    def setFullWidth(self, flag=True, clear=True):
        """
        Sets full width selection.

        :param flag: True to use full width selection.
        :type flag: bool

        :param clear: True to clear any previous selection. Default is True.
        :type clear: bool
        """
        if clear:
            self.cursor.clearSelection()
        self.format.setProperty(QtGui.QTextFormat.FullWidthSelection, flag)

    def underlined(self, color=QtCore.Qt.blue):
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SingleUnderline)
        self.format.setUnderlineColor(color)

    def setSpellchecking(self, color=QtCore.Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setError(self, color=QtCore.Qt.red):
        """ Highlights text as a syntax error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setWarning(self, color=QtGui.QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)
