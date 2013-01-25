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
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtGui import QBrush, QPlainTextEdit, QTextCursor
from PySide.QtGui import QColor
from PySide.QtGui import QKeyEvent
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QWheelEvent
from pcef.base import TextDecoration
from pcef.base import Mode
from pcef.config import svconfig
from pcef.tools.highlighter import QPygmentsHighlighter


class RightMarginMode(Mode):
    """
    Display the right margin
    """
    #: Mode identifier
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

    def updateStyling(self):
        """ Updates the margin pen color """
        self.pen = QPen(self.currentStyle.marginColor)

    def __paintMargin(self, event):
        """ Paints the right margin as postPainting step. """
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
    """
    This mode enable syntax highlighting (using the QPygmentsHighlighter)
    """
    #: Mode identifier
    IDENTIFIER = "SyntaxHighlighting"

    def __init__(self):
        self.highlighter = None
        super(SyntaxHighlightingMode, self).__init__(
            self.IDENTIFIER,
            "Apply syntax highlighting to the editor using ")
        self.multiline_triggers = ["/*", "'''", '"""']

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        self.highlighter = QPygmentsHighlighter(editor.textEdit.document())
        # todo the best would be to only rehighlight when there is a multilin oment/string
        editor.textEdit.keyReleased.connect(self.onTextChanged)
        editor.textEdit.blockCountChanged.connect(self.highlighter.rehighlight)
        super(SyntaxHighlightingMode, self).install(editor)

    def onTextChanged(self, event):
        # get current line
        txt = unicode(self.editor.textEdit.textCursor().block().text())
        if event.key() == Qt.Key_Backspace:
            self.highlighter.rehighlight()
            return
        for trigger in self.multiline_triggers:
            if trigger in txt:
                self.highlighter.rehighlight()
                break

    def updateStyling(self):
        """ Updates the pygments style """
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
    """
    This mode highlights the current line.
    """
    #: Mode identifier
    IDENTIFIER = "HighlightLine"

    def __init__(self):
        super(HighlightLineMode, self).__init__(
            self.IDENTIFIER, "Highlight the current line in the editor")
        self._pos = -1
        self._decoration = None
        self.brush = None

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        super(HighlightLineMode, self).install(editor)
        self.editor.textEdit.cursorPositionChanged.connect(
            self.changeActiveLine)
        self.changeActiveLine()

    def updateStyling(self):
        """ Updates the pygments style """
        self.brush = QBrush(QColor(self.currentStyle.activeLineColor))

    @Slot()
    def changeActiveLine(self):
        """ Changes the active line. """
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
    """
    This mode provide editor zoom (the editor font is increased/decreased)
    """
    #: Mode identifier
    IDENTIFIER = "EditorZoom"

    def __init__(self):
        super(EditorZoomMode, self).__init__(
            self.IDENTIFIER, "Zoom the editor with ctrl+mouse wheel")
        self.prev_delta = 0

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        super(EditorZoomMode, self).install(editor)
        self.editor.textEdit.mouseWheelActivated.connect(
            self.onWheelEvent)
        self.editor.textEdit.keyPressed.connect(self.onKeyPressed)
        self.default_font_size = svconfig.getGlobalStyle().fontSize

    def updateStyling(self):
        """ Updates the default font size """
        self.default_font_size = svconfig.getGlobalStyle().fontSize

    def onKeyPressed(self, event):
        """
        Resets editor font size to the default font size
        :param event: wheelEvent
        :type event: QKeyEvent
        :return:
        """
        if (event.key() == Qt.Key_0 and
                event.modifiers() & Qt.ControlModifier > 0):
            style = svconfig.getGlobalStyle()
            style.fontSize = self.default_font_size
            event.setAccepted(True)
            svconfig.changeGlobalStyle(style)
            svconfig.changeGlobalStyle(style)

    def onWheelEvent(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event
        if ctrl modifier is on.
        :param event: wheel event
        :type event: QWheelEvent
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
