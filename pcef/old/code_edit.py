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
Contains the CodeEdit widget (an extension of the CodeEdit used as a promoted widget by the
:class:`pcef.core.CodeEditorWidget` ui)
"""
from PySide.QtGui import QToolTip, QTextDocument, QTextBlock
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtCore import QRect
from PySide.QtGui import QColor
from PySide.QtGui import QTextCharFormat
from PySide.QtGui import QTextFormat
from PySide.QtGui import QKeyEvent
from PySide.QtGui import QTextEdit, QFocusEvent
from PySide.QtGui import QTextOption
from PySide.QtGui import QFont
from PySide.QtGui import QTextCursor
from PySide.QtGui import QMenu
from PySide.QtGui import QPaintEvent
from PySide.QtGui import QMouseEvent
from PySide.QtGui import QPlainTextEdit
from PySide.QtGui import QWheelEvent
from pygments.token import Token
from pcef.styled_object import StyledObject


def cursorForPosition(codeEdit, line, column, selectEndOfLine=False,
                      selection=None, selectWordUnderCursor=False):
    """
    Return a QTextCursor set to line and column with the specified selection
    :param line:
    :param column:
    """
    tc = QTextCursor(codeEdit.document())
    tc.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
    tc.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line - 1)
    tc.setPosition(tc.position() + column - 1)
    if selectEndOfLine is True:
        tc.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    elif isinstance(selection, int):
        tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, selection)
    elif selectWordUnderCursor is True:
        tc.select(QTextCursor.WordUnderCursor)
    codeEdit.setTextCursor(tc)
    return tc


class TextDecoration(QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration.
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
        QTextEdit.ExtraSelection.__init__(self)
        cursor = QTextCursor(cursorOrBlockOrDoc)
        if startPos is not None:
            cursor.setPosition(startPos)
        if endPos is not None:
            cursor.setPosition(endPos, QTextCursor.KeepAnchor)
        self.cursor = cursor

    def containsCursor(self, textCursor):
        assert isinstance(textCursor, QTextCursor)
        return self.cursor.selectionStart() <= textCursor.position() < \
            self.cursor.selectionEnd()

    def setBold(self):
        """ Uses bold text """
        self.format.setFontWeight(QFont.Bold)

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
        self.format.setProperty(QTextFormat.FullWidthSelection, flag)

    def setSpellchecking(self, color=Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setError(self, color=Qt.red):
        """ Highlights text as a syntax error

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setWarning(self, color=QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)


class VisibleBlock(object):
    """
    This class contains the geometry of currently visible blocks
    """

    def __init__(self, row, block, rect):
        """
        :param row: line number
        :param block: QTextBlock
        :param rect: QRect
        """
        self.row = row
        self.block = block
        (self.left, self.top, self.width, self.height) = rect
        self.rect = QRect(*rect)


class CodeEdit(QPlainTextEdit, StyledObject):
    """
    The code editor text edit. This is a specialized QPlainTextEdit made to
    expose additional signals, styling and methods. It also provides a custom
    context menu and methods to add actions, separators and sub-menus.

    Most of the code editor functionnalities are provided by installing modes on
    the PCEF instance.

    Additional signals:
        - dirtyChanged(bool)
        - focusedIn(QFocusEvent)
        - keyPressed(QKeyEvent)
        - keyReleased(QKeyEvent)
        - mousePressed(QMouseEvent)
        - mouseReleased(QMouseEvent)
        - newTextSet()
        - prePainting(QPaintEvent)
        - postPainting(QPaintEvent)
        - visibleBlocksChanged()

    """
    QSS = """QPlainTextEdit
    {
        background-color: %(b)s;
        color: %(t)s;
        selection-background-color: %(bs)s;
        selection-color: %(ts)s;
        border: none;
        border-radius: 0px;
    }
    """

    #---------------------------------------------------------------------------
    # Signals
    #---------------------------------------------------------------------------
    #: Signal emitted when the dirty state of the document changed
    dirtyChanged = Signal(bool)
    #: Signal emitted when a key is pressed
    keyPressed = Signal(QKeyEvent)
    #: Signal emitted when a key is released
    keyReleased = Signal(QKeyEvent)
    #: Signal emitted when a mouse button is pressed
    mousePressed = Signal(QMouseEvent)
    #: Signal emitted when a mouse button is released
    mouseReleased = Signal(QMouseEvent)
    #: Signal emitted on a wheel event
    mouseWheelActivated = Signal(QWheelEvent)
    #: Signal emitted before painting the core widget
    prePainting = Signal(QPaintEvent)
    #: Signal emitted after painting the core widget
    postPainting = Signal(QPaintEvent)
    #: Signal emitted at the end of the keyPressed event
    postKeyPressed = Signal(QKeyEvent)
    #: Signal emitted when the list of visible blocks changed
    visibleBlocksChanged = Signal()
    #: Signal emitted when setPlainText is invoked
    newTextSet = Signal()
    #: Signal emitted when focusInEvent is is called
    focusedIn = Signal(QFocusEvent)
    #: Signal emitted when the text is saved with pcef.saveFileFromEditor.
    #  The signal is emitted with the complete file path
    textSaved = Signal(str)

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    def __get_dirty(self):
        return self.__dirty

    def __set_dirty(self, dirty):
        if dirty != self.__dirty:
            self.__dirty = dirty
            self.dirtyChanged.emit(dirty)

    @property
    def contextMenu(self):
        return self.__context_menu

    #: Tells whether the editor is dirty(changes have been made to the document)
    dirty = property(__get_dirty, __set_dirty)

    #---------------------------------------------------------------------------
    # Methods
    #---------------------------------------------------------------------------
    def __init__(self, parent=None):
        """
        Creates the widget.

        :param parent: Optional parent widget
        """
        QPlainTextEdit.__init__(self, parent)
        StyledObject.__init__(self)
        #: Tag member used to remeber the filename of the edited text if any
        self.tagFilename = None
        #: Tag member used to remeber the filename of the edited text if any
        self.tagEncoding = 'utf8'
        #: Weakref to the editor
        self.editor = None

        self.__originalText = ""

        #: dirty flag
        self.__dirty = False
        #: our custom context menu
        self.__context_menu = QMenu()
        #: The list of active extra-selections (TextDecoration)
        self.__selections = []
        self.__numBlocks = -1

        self.visible_blocks = []

        #: Shortcut to the fontMetrics
        self.fm = self.fontMetrics()

        self.textChanged.connect(self.__onTextChanged)
        self.blockCountChanged.connect(self.__onBlocksChanged)
        self.verticalScrollBar().valueChanged.connect(self.__onBlocksChanged)
        self.newTextSet.connect(self.__onBlocksChanged)
        self.cursorPositionChanged.connect(self.__onBlocksChanged)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setMouseTracking(True)

        self._onStyleChanged()

    def addAction(self, action):
        """
        Adds an action to the text edit context menu

        :param action: QAction
        """
        QTextEdit.addAction(self, action)
        self.__context_menu.addAction(action)

    def addSeparator(self):
        """
        Adds a separator to the context menu
        """
        self.__context_menu.addSeparator()

    def addDecoration(self, decoration):
        """
        Add a text decoration

        :param decoration: Text decoration
        :type decoration: pcef.core.TextDecoration
        """
        self.__selections.append(decoration)
        self.__selections = sorted(self.__selections, key=lambda sel: sel.draw_order)
        self.setExtraSelections(self.__selections)

    def removeDecoration(self, decoration):
        """
        Remove text decoration.

        :param decoration: The decoration to remove
        :type decoration: pcef.core.TextDecoration
        """
        try:
            self.__selections.remove(decoration)
            self.setExtraSelections(self.__selections)
        except ValueError:
            pass

    def setShowWhitespaces(self, show):
        """
        Shows/Hides whitespaces.

        :param show: True to show whitespaces, False to hide them
        :type show: bool
        """
        doc = self.document()
        options = doc.defaultTextOption()
        if show:
            options.setFlags(options.flags() | QTextOption.ShowTabsAndSpaces)
        else:
            options.setFlags(options.flags() & ~QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(options)

    def indent(self, size):
        """
        Indent current line or selection

        :param size: indent size in spaces
        :type size: int
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        has_selection = True
        if not cursor.hasSelection():
            cursor.select(QTextCursor.LineUnderCursor)
            has_selection = False
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        cursor.setPosition(cursor.selectionStart())
        for i in range(nb_lines):
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(" " * size)
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.setPosition(cursor.position() + 1)
        cursor.setPosition(sel_start + size)
        if has_selection:
            cursor.setPosition(sel_end + (nb_lines * size),
                               QTextCursor.KeepAnchor)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def unIndent(self, size):
        """
        Un-indent current line or selection by tab_size
        """
        cursor = self.textCursor()
        assert isinstance(cursor, QTextCursor)
        cursor.beginEditBlock()
        pos = cursor.position()
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        has_selection = True
        if not cursor.hasSelection():
            cursor.select(QTextCursor.LineUnderCursor)
            has_selection = False
        nb_lines = len(cursor.selection().toPlainText().splitlines())
        cursor.setPosition(cursor.selectionStart())
        cpt = 0
        for i in range(nb_lines):
            cursor.select(QTextCursor.LineUnderCursor)
            if cursor.selectedText().startswith(" " * size):
                cursor.movePosition(QTextCursor.StartOfLine)
                [cursor.deleteChar() for _ in range(size)]
                pos = pos - size
                cpt += 1
            else:
                cursor.clearSelection()
                # next line
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.setPosition(cursor.position() + 1)
        if cpt:
            cursor.setPosition(sel_start - size)
        else:
            cursor.setPosition(sel_start)
        if has_selection:
            cursor.setPosition(sel_end - (cpt * size),
                               QTextCursor.KeepAnchor)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def updateOriginalText(self):
        self.__originalText = self.toPlainText()

    def _onStyleChanged(self):
        """
        Updates widget style when style changed.
        """
        self.setFont(QFont(self.currentStyle.fontName,
                           self.currentStyle.fontSize))
        self.fm = self.fontMetrics()
        qss = self.QSS % {
            'b': self.currentStyle.backgroundColor,
            't': self.currentStyle.tokenColor(Token),
            "bs": self.currentStyle.selectionBackgroundColor,
            "ts": self.currentStyle.selectionTextColor}
        self.setShowWhitespaces(self.currentStyle.showWhitespaces)
        self.setStyleSheet(qss)

    def paintEvent(self, event):
        """
        Emits prePainting and postPainting signals

        :param event: QPaintEvent
        """
        self.prePainting.emit(event)
        QPlainTextEdit.paintEvent(self, event)
        self.postPainting.emit(event)

    def keyPressEvent(self, event):
        """
        Performs indentation if tab key presed, else emits the keyPressed signal

        :param event: QKeyEvent
        """
        # assert isinstance(event, QKeyEvent)
        event.stop = False
        # replace tabs by space
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            assert isinstance(cursor, QTextCursor)
            if not cursor.hasSelection():
                # insert tab at cursor pos
                cursor.insertText(" " * self.editor().TAB_SIZE)
            else:
                # indent whole selection
                self.indent(self.editor().TAB_SIZE)
            event.stop = True
        self.keyPressed.emit(event)
        if not event.stop:
            QPlainTextEdit.keyPressEvent(self, event)
        self.postKeyPressed.emit(event)

    def keyReleaseEvent(self, event):
        """
        Performs indentation if tab key pressed, else emits the keyPressed signal

        :param event: QKeyEvent
        """
        assert isinstance(event, QKeyEvent)
        event.stop = False
        self.keyReleased.emit(event)
        if not event.stop:
            QPlainTextEdit.keyReleaseEvent(self, event)

    def focusInEvent(self, event):
        """
        Emits the focusedIn signal
        :param event:
        :return:
        """
        self.focusedIn.emit(event)
        QPlainTextEdit.focusInEvent(self, event)

    def mousePressEvent(self, event):
        """
        Emits mousePressed signal

        :param event: QMouseEvent
        """
        event.stop = False
        self.mousePressed.emit(event)
        if not event.stop:
            QPlainTextEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Emits mouseReleased signal.

        :param event: QMouseEvent
        """
        event.stop = False
        self.mouseReleased.emit(event)
        if not event.stop:
            QPlainTextEdit.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        """
        Emits the mouseWheelActivated signal.

        :param event: QMouseEvent
        """
        event.stop = False
        self.mouseWheelActivated.emit(event)
        if not event.stop:
            QPlainTextEdit.wheelEvent(self, event)

    def mouseMoveEvent(self, event):
        assert isinstance(event, QMouseEvent)
        c = self.cursorForPosition(event.pos())
        for sel in self.__selections:
            if sel.containsCursor(c) and sel.tooltip:
                QToolTip.showText(self.mapToGlobal(event.pos()), sel.tooltip, self)
                break
        QPlainTextEdit.mouseMoveEvent(self, event)

    def contextMenuEvent(self, event):
        """ Shows our own context menu """
        self.__context_menu.exec_(event.globalPos())

    def resizeEvent(self, event):
        """ Updates visible blocks on resize """
        self.__onBlocksChanged()
        QPlainTextEdit.resizeEvent(self, event)

    def __onTextChanged(self):
        """ Sets dirty to true """
        if self.toPlainText() != self.__originalText:
            # self.__originalText = self.toPlainText()
            self.dirty = True
        else:
            self.dirty = False

    def setPlainText(self, txt):
        """ Sets the text edit content and emits newTextSet signal.
        :param txt: New text to display
        """
        self.__originalText = txt
        QPlainTextEdit.setPlainText(self, txt)
        self.newTextSet.emit()

    def __onBlocksChanged(self):
        """
        Updates the list of visible blocks and emits visibleBlocksChanged
        signal.
        """
        visible_blocks = []
        block = self.firstVisibleBlock()
        row = block.blockNumber() + 1
        width = self.width()
        w = width - 2
        h = self.fm.height()
        bbox = self.blockBoundingGeometry(block)
        top = bbox.translated(self.contentOffset()).top()
        bottom = top + bbox.height()
        zoneTop = 0  # event.rect().top()
        zoneBottom = self.height()  # event.rect().bottom()
        visible_blocks_append = visible_blocks.append
        while block.isValid() and top <= zoneBottom:
            if block.isVisible() and bottom >= zoneTop:
                visible_blocks_append(
                    VisibleBlock(row, block, (0, top, w, h))
                )
            block = block.next()
            row += 1
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
        self.visible_blocks = visible_blocks
        self.visibleBlocksChanged.emit()

    def fold(self, start, end, fold=True):
        """ Fold/Unfold a block of text delimitted by start/end line numbers
        :param start: Start folding line (this line is not fold, only the next
        ones)
        :param end: End folding line.
        :param fold: True to fold, False to unfold
        """
        doc = self.document()
        assert isinstance(doc, QTextDocument)
        for i in range(start + 1, end):
            block = self.document().findBlockByNumber(i)
            assert isinstance(block, QTextBlock)
            block.setVisible(not fold)
            doc.markContentsDirty(block.position(), block.length())
        self.update()
        self.viewport().repaint()
        self.__onBlocksChanged()
