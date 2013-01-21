#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the base class for editor modes and a few builtin modes
"""
from PySide.QtCore import Slot, Qt
from PySide.QtGui import QPainter, QPen, QBrush, QColor, QWheelEvent, QInputEvent, QKeyEvent
from pcef.config import svconfig
from pcef.tools.highlighter import QPygmentsHighlighter
from pcef.base import TextDecoration, Mode


class RightMarginMode(Mode):
    IDENTIFIER = "RightMargin"

    def __init__(self):
        Mode.__init__(self, self.IDENTIFIER, "Draw the right margin on the "
                                             "document")
        #: Defines the margin position
        self.marginPos = 80

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        super(RightMarginMode, self).install(editor)
        editor.textEdit.postPainting.connect(self.__paintMargin)

    def _updateStyling(self):
        self.pen = QPen(self.currentStyle.marginColor)

    def __paintMargin(self, event):
        if self.enabled:
            rect = event.rect()
            fm = self.editor.textEdit.fm
            pos = self.marginPos
            offset = self.editor.textEdit.contentOffset().x() + \
                self.editor.textEdit.document().documentMargin()
            x80 = round(fm.averageCharWidth() * pos) + offset
            p = QPainter(self.editor.textEdit.viewport())
            p.setPen(self.pen)
            p.drawLine(x80, rect.top(), x80, rect.bottom())


class SyntaxHighlightingMode(Mode):
    IDENTIFIER = "SyntaxHighlighting"

    def __init__(self):
        self.highlighter = None
        super(SyntaxHighlightingMode, self).__init__(
            self.IDENTIFIER,
            "Apply syntax highlighting to the editor using ")

    def install(self, editor):
        self.highlighter = QPygmentsHighlighter(editor.textEdit.document())
        super(SyntaxHighlightingMode, self).install(editor)

    def _updateStyling(self):
        if self.highlighter is not None:
            self.highlighter.style = self.currentStyle.pygmentsStyle

    def setLexerFromFilename(self, fn="file.py"):
        """
        Change the highlighter lexer on the fly by supplying the filename
        to highlight

        .. note::
            A fake filename is enough to get the correct lexer based on the
            extension).

        .. note::
            The default lexer is the Python lexer

        :param fn: str -- Filename
        """
        assert self.highlighter is not None, "SyntaxHighlightingMode not " \
                                             "installed"
        self.highlighter.setLexerFromFilename(fn)


class HighlightLineMode(Mode):
    IDENTIFIER = "HighlightLine"

    def __init__(self):
        super(HighlightLineMode, self).__init__(
            self.IDENTIFIER, "Highlight the current line in the editor")
        self._pos = -1
        self._decoration = None
        self.brush = None

    def install(self, editor):
        super(HighlightLineMode, self).install(editor)
        self.editor.textEdit.cursorPositionChanged.connect(
            self._updateCursorPos)
        self._updateCursorPos()

    def _updateStyling(self):
        self.brush = QBrush(QColor(self.currentStyle.activeLineColor))

    @Slot()
    def _updateCursorPos(self):
        tc = self.editor.textEdit.textCursor()
        pos = tc.blockNumber
        if pos != self._pos:
            self._pos = pos
            # remove previous selection
            self.editor.textEdit.removeDecoration(self._decoration)
            # add new selection
            self._decoration = TextDecoration(tc)
            self._decoration.setBackground(self.brush)
            self._decoration.setFullWidth()
            self.editor.textEdit.addDecoration(self._decoration)


class EditorZoomMode(Mode):
    IDENTIFIER = "EditorZoom"

    def __init__(self):
        super(EditorZoomMode, self).__init__(
            self.IDENTIFIER, "Zoom the editor with ctrl+mouse wheel")
        self.prev_delta = 0

    def install(self, editor):
        super(EditorZoomMode, self).install(editor)
        self.editor.textEdit.mouseWheelActivated.connect(
            self.onWheelEvent)
        self.editor.textEdit.keyPressed.connect(self.onKeyPressed)
        self.default_font_size = svconfig.getGlobalStyle().fontSize

    def onKeyPressed(self, event):
        """
        Resets editor font size to the default font size
        :param event: wheelEvent
        :type event: QKeyEvent
        :return:
        """
        if event.key() == Qt.Key_0 and event.modifiers() & Qt.ControlModifier > 0:
            style = svconfig.getGlobalStyle()
            style.fontSize = self.default_font_size
            event.setAccepted(True)
            svconfig.changeGlobalStyle(style)
            svconfig.changeGlobalStyle(style)

    def onWheelEvent(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event if ctrl modifier is on.
        :param event: wheelEvent
        :type event: QWheelEvent
        :return:
        """
        delta = event.delta()
        if event.modifiers() & Qt.ControlModifier > 0:
            style = svconfig.getGlobalStyle()
            if delta < self.prev_delta:
                style.fontSize -= 1
            else:
                style.fontSize += 1
            if style.fontSize <= 0:
                style.fontSize = 1
            event.setAccepted(True)
            svconfig.changeGlobalStyle(style)