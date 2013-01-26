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
Contains the promoted widgets used in the Qt Designer ui
"""
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtCore import QRect
from PySide.QtGui import QTextEdit
from PySide.QtGui import QTextOption
from PySide.QtGui import QFont
from PySide.QtGui import QKeyEvent
from PySide.QtGui import QTextCursor
from PySide.QtGui import QMenu
from PySide.QtGui import QPaintEvent
from PySide.QtGui import QMouseEvent
from PySide.QtGui import QTextDocument
from PySide.QtGui import QPlainTextEdit
from PySide.QtGui import QWheelEvent
from pygments.token import Token
from pcef.style import StyledObject


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


class QPlainCodeEdit(QPlainTextEdit, StyledObject):
    """
    The code editor text edit. This is a specialized QPlainTextEdit made to
    expose additional signals, styling and methods. It also provides a custom
    context menu and methods to add actions, separators and sub-menus.

    Most of the code editor functionnalities are provided by installing modes on
    the PCEF instance.

    Additional signals:
        - dirtyChanged(bool)
        - keyPressed(QKeyEvent)
        - mousePressed(QMouseEvent)
        - mouseReleased(QMouseEvent)
        - prePainting(QPaintEvent)
        - postPainting(QPaintEvent)
        - visibleBlocksChanged()
        - newTextSet()

    """
    #: Stylesheet
    QSS = """QPlainTextEdit
    {
        background-color: %(b)s;
        color: %(t)s;
        selection-background-color: %(bs)s;
        selection-color: %(ts)s;
    }
    """

    #---------------------------------------------------------------------------
    # Signals
    #---------------------------------------------------------------------------
    #: Emitted when the dirty state of the document changed
    dirtyChanged = Signal(bool)
    #: Emitted when a key is pressed
    keyPressed = Signal(QKeyEvent)
    #: Emitted when a key is released
    keyReleased = Signal(QKeyEvent)
    #: emitted when a mouse button is pressed
    mousePressed = Signal(QMouseEvent)
    #: emitted when a mouse button is released
    mouseReleased = Signal(QMouseEvent)
    #: emitted on a wheel event
    mouseWheelActivated = Signal(QWheelEvent)
    #: Emitted before painting the core widget
    prePainting = Signal(QPaintEvent)
    #: Emitted after painting the core widget
    postPainting = Signal(QPaintEvent)
    #: Emitted when the list of visible blocks changed
    visibleBlocksChanged = Signal()
    #: Emitted when setPlainText is invoked
    newTextSet = Signal()

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    def __get_dirty(self):
        return self._dirty

    def __set_dirty(self, dirty):
        if dirty != self._dirty:
            self._dirty = dirty
            self.dirtyChanged.emit(dirty)

    #: Tells whether the editor is dirty(changes have been made to the document)
    dirty = property(__get_dirty, __set_dirty)

    #---------------------------------------------------------------------------
    # Methods
    #---------------------------------------------------------------------------
    def __init__(self, parent=None):
        QPlainTextEdit.__init__(self, parent)
        StyledObject.__init__(self)
        self._completer = None
        self.filename = None
        self._dirty = False
        self._context_menu = QMenu()
        self.selections = []
        self.fm = self.fontMetrics()

        doc = self.document()
        assert isinstance(doc, QTextDocument)
        self.textChanged.connect(self._onTextChanged)
        self.blockCountChanged.connect(self._onBlocksChanged)
        self.verticalScrollBar().valueChanged.connect(self._onBlocksChanged)
        self.newTextSet.connect(self._onBlocksChanged)
        self.cursorPositionChanged.connect(self._onBlocksChanged)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.numBlocks = -1

        #: Shortcuts for sharing the filename currently edited.
        #  This is only set when using the openFileInEditor function.
        self.filename = None
        self.updateStyling()

        #: weakref to the editor
        self.editor = None

    def addAction(self, action):
        """
        Adds an action to the text edit context menu
        :param action: QAction
        """
        QTextEdit.addAction(self, action)
        self._context_menu.addAction(action)

    def addSeparator(self):
        """
        Adds a seperator to the context menu
        """
        self._context_menu.addSeparator()

    def addDecoration(self, decoration):
        """
        Add a text decoration
        :param decoration: pcef.base.TextDecoration
        """
        self.selections.append(decoration)
        self.setExtraSelections(self.selections)

    def removeDecoration(self, decoration):
        """
        Remove text decoration.
        :param decoration: The decoration to remove
        """
        try:
            self.selections.remove(decoration)
            self.setExtraSelections(self.selections)
        except ValueError:
            pass

    def setShowWhitespaces(self, show):
        """
        Shows/Hides whitespaces.
        :param show: True to show whitespaces, False to hide them
        """
        doc = self.document()
        options = doc.defaultTextOption()
        if show:
            options.setFlags(options.flags() | QTextOption.ShowTabsAndSpaces)
        else:
            options.setFlags(options.flags() & ~QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(options)

    def indent(self, nbSpaces):
        """
        Indent current line or selection
        """
        cursor = self.textCursor()
        assert isinstance(cursor, QTextCursor)
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
            cursor.insertText(" " * nbSpaces)
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.setPosition(cursor.position() + 1)
        cursor.setPosition(sel_start + nbSpaces)
        if has_selection:
            cursor.setPosition(sel_end + (nb_lines * nbSpaces),
                               QTextCursor.KeepAnchor)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def unIndent(self, nbSpaces):
        """
        Unindent current line or selection by tab_size
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
            if cursor.selectedText().startswith(" " * nbSpaces):
                cursor.movePosition(QTextCursor.StartOfLine)
                [cursor.deleteChar() for _ in range(nbSpaces)]
                pos = pos - nbSpaces
                cpt += 1
            else:
                cursor.clearSelection()
                # next line
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.setPosition(cursor.position() + 1)
        if cpt:
            cursor.setPosition(sel_start - nbSpaces)
        else:
            cursor.setPosition(sel_start)
        if has_selection:
            cursor.setPosition(sel_end - (cpt * nbSpaces),
                               QTextCursor.KeepAnchor)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def updateStyling(self):
        """
        Update widget style when the global style changed.
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
        assert isinstance(event, QKeyEvent)
        event.setAccepted(False)
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
            event.setAccepted(True)
        self.keyPressed.emit(event)
        if not event.isAccepted():
            event.setAccepted(True)
            QPlainTextEdit.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """
        Performs indentation if tab key presed, else emits the keyPressed signal
        :param event: QKeyEvent
        """
        assert isinstance(event, QKeyEvent)
        event.setAccepted(False)
        self.keyReleased.emit(event)
        if not event.isAccepted():
            event.setAccepted(True)
            QPlainTextEdit.keyReleaseEvent(self, event)

    def mousePressEvent(self, event):
        """
        Emits mousePressed signal.
        :param event: QMouseEvent
        """
        event.setAccepted(False)
        self.mousePressed.emit(event)
        if not event.isAccepted():
            event.setAccepted(True)
            QPlainTextEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Emits mouseReleased signal.
        :param event: QMouseEvent
        """
        event.setAccepted(False)
        self.mouseReleased.emit(event)
        if not event.isAccepted():
            event.setAccepted(True)
            QPlainTextEdit.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        """
        Emits the mouseWheelActivated signal.
        :param event: QMouseEvent
        """
        event.setAccepted(False)
        self.mouseWheelActivated.emit(event)
        if not event.isAccepted():
            event.setAccepted(True)
            QPlainTextEdit.wheelEvent(self, event)

    def contextMenuEvent(self, event):
        """ Shows our own context menu """
        self._context_menu.exec_(event.globalPos())

    def resizeEvent(self, event):
        """ Updates visible blocks on resize """
        self._onBlocksChanged()
        QPlainTextEdit.resizeEvent(self, event)

    def _onTextChanged(self):
        """ Sets dirty to true """
        self.dirty = True

    def setPlainText(self, txt):
        """ Sets the text edit content and emits newTextSet signal.
        :param txt: New text to display
        """
        QPlainTextEdit.setPlainText(self, txt)
        self.newTextSet.emit()

    def _onBlocksChanged(self):
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
        for i in range(start + 1, end):
            self.document().findBlockByNumber(i).setVisible(not fold)
            self.update()
        self._onBlocksChanged()

