#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module defines text edit decorations
"""
import pcef


class TextDecoration(pcef.QtGui.QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration. The text decoration is an
    utility class that adds a few utility methods over the Qt ExtraSelection.

    In addition to the helper methods, a tooltip can be added to a decoration.
    Usefull for errors marks and so on...
    """

    def __init__(self, cursorOrBlockOrDoc, startPos=None, endPos=None,
                 draw_order=0, tooltip=None):
        """
        Creates a text decoration

        :param cursorOrBlockOrDoc: Selection
        :type cursorOrBlockOrDoc: QTextCursor or QTextBlock or QTextDocument

        :param startPos: Selection start pos

        :param endPos: Selection end pos

        .. note:: Use the cursor selection if startPos and endPos are none.
        """
        self.draw_order = draw_order
        self.tooltip = tooltip
        pcef.QtGui.QTextEdit.ExtraSelection.__init__(self)
        cursor = pcef.QtGui.QTextCursor(cursorOrBlockOrDoc)
        if startPos is not None:
            cursor.setPosition(startPos)
        if endPos is not None:
            cursor.setPosition(endPos, pcef.QtGui.QTextCursor.KeepAnchor)
        self.cursor = cursor

    def containsCursor(self, textCursor):
        assert isinstance(textCursor, pcef.QtGui.QTextCursor)
        return self.cursor.selectionStart() <= textCursor.position() < \
            self.cursor.selectionEnd()

    def setBold(self):
        """ Uses bold text """
        self.format.setFontWeight(pcef.QtGui.QFont.Bold)

    def setForeground(self, color):
        """ Sets the foreground color.
        :param color: QColor """
        self.format.setForeground(color)

    def setBackground(self, brush):
        """ Sets the background color

        :param brush: QBrush
        """
        self.format.setBackground(brush)

    def setFullWidth(self, flag=True):
        """ Sets full width selection

        :param flag: True to use full width selection.
        """
        self.cursor.clearSelection()
        self.format.setProperty(pcef.QtGui.QTextFormat.FullWidthSelection, flag)

    def setSpellchecking(self, color=pcef.QtCore.Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(
            pcef.QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setError(self, color=pcef.QtCore.Qt.red):
        """ Highlights text as a syntax error

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(
            pcef.QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setWarning(self, color=pcef.QtGui.QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(
            pcef.QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)