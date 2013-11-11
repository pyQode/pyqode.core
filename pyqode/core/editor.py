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
This module contains the definition of the QCodeEdit
"""
import sys
import weakref
from pyqode.core import logger
from pyqode.core import constants
from pyqode.core.constants import PanelPosition
from pyqode.core.properties import PropertyRegistry
from pyqode.core.system import DelayJobRunner
from pyqode.core.decoration import TextDecoration
from pyqode.qt import QtGui, QtCore


class QCodeEdit(QtGui.QPlainTextEdit):
    """
    Base class for any pyqode editor widget.

    Extends :py:class:`QPlainTextEdit` by adding an extension system (
    modes and panels), a rich property system for styles and settings
    (see :class:`pyqode.core.PropertyRegistry`) and by adding a series of
    additional signal and methods.

    **Settings** :attr:`pyqode.core.QCodeEdit.settings`

    ======================= ====================== ======= ====================== ==============
    Key                     Section                Type    Default value          Description
    ======================= ====================== ======= ====================== ==============
    showWhiteSpaces         General                bool    False                  Display visual whitespaces
    tabLength               General                int     4                      Tab length (number of spaces)
    useSpacesInsteadOfTab   General                bool    True                   Use spaces instead of spaces (be warry of this, most modes still use spaces heavily for internal computations)
    minIndentColumn         General                int     0                      Min column indent (some languages such as cobol requires to indent code at min col 7)
    saveOnFrameDeactivation General                bool    True                   Auto save when editor loose focus.
    ======================= ====================== ======= ====================== ==============

    **Style** :attr:`pyqode.core.QCodeEdit.style`

    ====================== ====================== ======= ====================== ==============
    Key                    Section                Type    Default value          Description
    ====================== ====================== ======= ====================== ==============
    font                   General                string  OS Dependant           Font: *monospace* on GNU/Linux, *Consolas* on Windows and *Monaco* on Darwin
    fontSize               General                int     10                     Font size
    background             General                QColor  #FFFFFF                Editor background color
    foreground             General                QColor  #000000                Editor foreground color
    whiteSpaceForeground   General                QColor  #dddddd                Color of the whitespaces
    selectionBackground    General                QColor  OS dependant           QtGui.QPalette.highlight().color()
    selectionForeground    General                QColor  OS dependant           QtGui.QPalette.highlightedText().color()
    ====================== ====================== ======= ====================== ==============

    **Signals:**
        - :attr:`pyqode.core.QCodeEdit.painted`
        - :attr:`pyqode.core.QCodeEdit.newTextSet`
        - :attr:`pyqode.core.QCodeEdit.painted`
        - :attr:`pyqode.core.QCodeEdit.textSaved`
        - :attr:`pyqode.core.QCodeEdit.textSaving`
        - :attr:`pyqode.core.QCodeEdit.dirtyChanged`
        - :attr:`pyqode.core.QCodeEdit.keyPressed`
        - :attr:`pyqode.core.QCodeEdit.keyReleased`
        - :attr:`pyqode.core.QCodeEdit.mousePressed`
        - :attr:`pyqode.core.QCodeEdit.mouseReleased`
        - :attr:`pyqode.core.QCodeEdit.mouseWheelActivated`
        - :attr:`pyqode.core.QCodeEdit.postKeyPressed`
        - :attr:`pyqode.core.QCodeEdit.focusedIn`
        - :attr:`pyqode.core.QCodeEdit.mouseMoved`
        - :attr:`pyqode.core.QCodeEdit.indentRequested`
        - :attr:`pyqode.core.QCodeEdit.unIndentRequested`

    .. note:: QCodeEdit has been designed to work with files (:meth:`pyqode.core.QCodeEdit.openFile`
              , :meth:`pyqode.core.QCodeEdit.saveToFile`), not plain text.
              Well, you can still use some plain text but many modes and panels
              that rely heavily on the current file name/path won't work
              properly (e.g. the syntax highlighter mode uses the file name
              extension to automatically adapt the lexer so you will need to do
              it manually depending on the nature of the text/code to edit).
    """
    #: Paint hook
    painted = QtCore.Signal(QtGui.QPaintEvent)
    #: Signal emitted when a new text is set on the widget
    newTextSet = QtCore.Signal()
    #: Signal emitted when the text is saved to file
    textSaved = QtCore.Signal(str)
    #: Signal emitted before the text is saved to file
    textSaving = QtCore.Signal(str)
    #: Signal emitted when the dirty state changed
    dirtyChanged = QtCore.Signal(bool)
    #: Signal emitted when a key is pressed
    keyPressed = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when a key is released
    keyReleased = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when a mouse button is pressed
    mousePressed = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted when a mouse button is released
    mouseReleased = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted on a wheel event
    mouseWheelActivated = QtCore.Signal(QtGui.QWheelEvent)
    #: Signal emitted at the end of the keyPressed event
    postKeyPressed = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when focusInEvent is is called
    focusedIn = QtCore.Signal(QtGui.QFocusEvent)
    #: Signal emitted when the mouseMoved
    mouseMoved = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted when the user press the TAB key
    indentRequested = QtCore.Signal()
    #: Signal emitted when the user press the BACK-TAB (Shift+TAB) key
    unIndentRequested = QtCore.Signal()

    @property
    def showWhiteSpaces(self):
        """
        Shows/Hides white spaces highlighting.

        Gets/sets self.settings.value("showWhiteSpaces")
        """
        return self.settings.value("showWhiteSpaces")

    @showWhiteSpaces.setter
    def showWhiteSpaces(self, value):
        assert isinstance(value, bool)
        self.settings.setValue("showWhiteSpaces", value)

    @property
    def saveOnFrameDeactivation(self):
        """
        Enables auto save on focus out.

        Gets/sets self.settings.value("saveOnFrameDeactivation")
        """
        return self.settings.value("saveOnFrameDeactivation")

    @saveOnFrameDeactivation.setter
    def saveOnFrameDeactivation(self, value):
        assert isinstance(value, bool)
        self.settings.setValue("saveOnFrameDeactivation", value)

    @property
    def editorFont(self):
        """
        The editor font.

        Gets/sets self.style.value("font")
        """
        return self.style.value("font")

    @editorFont.setter
    def editorFont(self, value):
        self.style.setValue("font", value)

    @property
    def fontSize(self):
        """
        The editor font size.

        Gets/sets self.style.value("fontSize")
        """
        return self.style.value("fontSize")

    @fontSize.setter
    def fontSize(self, value):
        self.style.setValue("fontSize", value)

    @property
    def background(self):
        """
        The editor background color.

        Gets/sets self.style.value("background")
        """
        return self.style.value("background")

    @background.setter
    def background(self, value):
        self.style.setValue("background", value)

    @property
    def foreground(self):
        """
        The editor foreground color.

        Gets/sets self.style.value("foreground")
        """
        return self.style.value("foreground")

    @foreground.setter
    def foreground(self, value):
        self.style.setValue("foreground", value)

    @property
    def whiteSpaceForeground(self):
        """
        The editor white spaces' foreground color.

        Gets/sets self.style.value("whiteSpaceForeground")
        """
        return self.style.value("whiteSpaceForeground")

    @whiteSpaceForeground.setter
    def whiteSpaceForeground(self, value):
        self.style.setValue("whiteSpaceForeground", value)

    @property
    def selectionBackground(self):
        """
        The editor selection's background color.

        Gets/sets self.style.value("selectionBackground")
        """
        return self.style.value("selectionBackground")

    @selectionBackground.setter
    def selectionBackground(self, value):
        self.style.setValue("selectionBackground", value)

    @property
    def selectionForeground(self):
        """
        The editor selection's foreground color.

        Gets/sets self.style.value("selectionForeground")
        """
        return self.style.value("selectionForeground")

    @selectionForeground.setter
    def selectionForeground(self, value):
        self.style.setValue("selectionForeground", value)

    @property
    def currentLineText(self):
        return self.lineText(self.cursorPosition[0])

    @property
    def dirty(self):
        """
        Gets/sets the dirty flag.

        :type: bool
        """
        return self.__dirty

    @dirty.setter
    def dirty(self, value):
        if self.__dirty != value:
            self.__dirty = value
            self.dirtyChanged.emit(value)

    @property
    def cursorPosition(self):
        """
        Returns the text cursor position (line, column).

        .. note:: The line number is 1 based while the column number is 0 based.

        :return: The cursor position (line, column)
        :rtype: tuple(int, int)
        """
        return (self.textCursor().blockNumber() + 1,
                self.textCursor().columnNumber())

    @property
    def fileName(self):
        """
        Returns the file name (see :meth:`QtCore.QFileInfo.fileName`)

        :rtype: str
        """
        return QtCore.QFileInfo(self.filePath).fileName()

    @property
    def filePath(self):
        """
        Gets/Sets the current file path. This property is used by many modes to
        work properly. It is automatically set by the
        :meth:`pyqode.core.QCodeEdit.openFile` and
        :meth:`pyqode.core.QCodeEdit.saveToFile` methods.

        If you need to work with plain text, be sure to adapt file path
        accordingly (the extension is enough)

        :type: str
        """
        return self.__filePath

    @filePath.setter
    def filePath(self, value):
        self.__filePath = value

    @property
    def fileEncoding(self):
        """
        Returns last encoding used to open the file

        :rtype: str
        """
        return self.__fileEncoding

    @property
    def visibleBlocks(self):
        """
        Returns the list of visible blocks.

        Each element in the list is a tuple made up of the line top position,
        the line number (already 1 based), and the QTextBlock itself.

        :return: A list of tuple(top position, line number, block)
        :rtype: List of tuple(int, int, QtGui.QTextBlock)
        """
        return self.__blocks

    @property
    def style(self):
        """
        Gets/Sets the editor style properties.

        :type: pyqode.core.QPropertyRegistry
        """
        return self.__style

    @style.setter
    def style(self, value):
        self.__style.update(value)

    @property
    def settings(self):
        """
        Gets/Sets the editor settings properties.

        :type: pyqode.core.QPropertyRegistry
        """
        return self.__settings

    @settings.setter
    def settings(self, value):
        self.__settings.update(value)

    def __init__(self, parent=None, createDefaultActions=True):
        """
        :param parent: Parent widget

        :param createDefaultActions: Specify if the default actions (copy,
                                     paste, ...) must be created.
                                     Default is True.
        """
        QtGui.QPlainTextEdit.__init__(self, parent)
        self._lastMousePos = None
        self.__cachedCursorPos = (-1, -1)
        self.__modifiedLines = set()
        self.__cleaning = False
        self.__marginSizes = (0, 0, 0, 0)
        self.top = self.left = self.right = self.bottom = -1
        self.setCenterOnScroll(True)

        #: The list of visible blocks, update every paintEvent
        self.__blocks = []

        self.__parenthesisSelections = []

        self.__tooltipRunner = DelayJobRunner(self, nbThreadsMax=1, delay=700)
        self.__previousTooltipBlockNumber = -1

        #: The list of actions, (none is a separator)
        self.__actions = []
        if createDefaultActions:
            self.__createDefaultActions()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # panels and modes
        self.__modes = {}
        self.__panels = {PanelPosition.TOP: {},
                         PanelPosition.LEFT: {},
                         PanelPosition.RIGHT: {},
                         PanelPosition.BOTTOM: {}}

        #: Path of the current file
        self.__filePath = None
        #: Encoding of the current file
        self.__fileEncoding = None
        #: Original text, used to compute the control flag
        self.__originalText = ""

        #: Dirty flag; tells if the widget text content is different from the
        #: file content
        self.__dirty = False

        self.__initSettings()
        self.__initStyle()

        #: The list of active extra-selections (TextDecoration)
        self.__selections = []

        # connect slots
        self.blockCountChanged.connect(self.__updateViewportMargins)
        self.textChanged.connect(self.__ontextChanged)
        self.updateRequest.connect(self.__updatePanels)
        self.blockCountChanged.connect(self.update)
        self.cursorPositionChanged.connect(self.update)
        self.selectionChanged.connect(self.update)

        self.setMouseTracking(True)

        self.mnu = None

    def __del__(self):
        pass
        # todo fix it
        # self.uninstallAll()

    def uninstallAll(self):
        while len(self.__modes):
            k = list(self.__modes.keys())[0]
            self.uninstallMode(k)
        while len(self.__panels):
            zone = list(self.__panels.keys())[0]
            while len(self.__panels[zone]):
                k = self.__panels[zone].keys()[0]
                self.uninstallPanel(k, zone)
            self.__panels.pop(zone, None)

    def showContextMenu(self, pt):
        self.mnu = QtGui.QMenu()
        self.mnu.addActions(self.__actions)
        self.mnu.popup(self.mapToGlobal(pt))

    @QtCore.Slot()
    def delete(self):
        """ Deletes the selected text """
        self.textCursor().removeSelectedText()

    def lineCount(self):
        """ Returns the document line count """
        return self.document().blockCount()

    def gotoLine(self, line=None, move=True, column=None):
        """
        Moves the text cursor to the specifed line.

        If line is None, a QInputDialog will pop up to ask the line number to
        the user.

        :param line: The line number to go (1 based)
        :param move: True to move the cursor. False will return the cursor
                     without setting it on the editor.
        :param column: Optional column number. Introduced in version 1.1
        :return: The new text cursor
        :rtype: QtGui.QTextCursor
        """
        if line is None or isinstance(line, bool):
            line, result = QtGui.QInputDialog.getInt(
                self, "Go to line", "Line number:", 1, 1, self.lineCount())
            if not result:
                return
            if not line:
                line = 1
        tc = self.textCursor()
        tc.movePosition(tc.Start, tc.MoveAnchor)
        tc.movePosition(tc.Down, tc.MoveAnchor, line-1)
        if column:
            tc.movePosition(tc.Right, tc.MoveAnchor, column)
        if move:
            self.setTextCursor(tc)
        return tc

    def selectedText(self):
        """ Returns the selected text. """
        return self.textCursor().selectedText()

    def selectWordUnderCursor(self, selectWholeWord=False, tc=None):
        """
        Selects the word under cursor using the separators defined in the
        the constants module.

        :param selectWholeWord: If set to true the whole word is selected, else
                                the selection stops at the cursor position.

        :param tc: Custom text cursor (e.g. from a QTextDocument clone)

        :return The QTextCursor that contains the selected word.
        """
        if not tc:
            tc = self.textCursor()
        word_separators = constants.WORD_SEPARATORS
        end_pos = start_pos = tc.position()
        while not tc.atStart():
            # tc.movePosition(tc.Left, tc.MoveAnchor, 1)
            tc.movePosition(tc.Left, tc.KeepAnchor, 1)
            try:
                ch = tc.selectedText()[0]
                word_separators = constants.WORD_SEPARATORS
                st = tc.selectedText()
                if (st in word_separators and (st != "n" and st != "t")
                        or ch.isspace()):
                    break  # start boundary found
            except IndexError:
                break  # nothing selectable
            start_pos = tc.position()
            tc.setPosition(start_pos)
        if selectWholeWord:
            tc.setPosition(end_pos)
            while not tc.atEnd():
                # tc.movePosition(tc.Left, tc.MoveAnchor, 1)
                tc.movePosition(tc.Right, tc.KeepAnchor, 1)
                ch = tc.selectedText()[0]
                st = tc.selectedText()
                if (st in word_separators and (st != "n" and st != "t")
                        or ch.isspace()):
                    break  # end boundary found
                end_pos = tc.position()
                tc.setPosition(end_pos)
        tc.setPosition(start_pos)
        tc.setPosition(end_pos, tc.KeepAnchor)
        return tc

    def selectWordUnderMouseCursor(self):
        """
        Selects the word under the **mouse** cursor.

        :return: A QTextCursor with the word under mouse cursor selected.
        """
        tc = self.cursorForPosition(self._lastMousePos)
        tc = self.selectWordUnderCursor(True, tc)
        #print(tc.selectedText())
        return tc

    def detectEncoding(self, data):
        """
        Detects file encoding.

        This implementation tries to use chardet to detect encoding.

        :param data: Data from which we want to detect the encoding.
        :type data: bytes

        :return: The detected encoding. Returns the result of
                 :meth:`pyqode.core.QCodeEdit.getDefaultEncoding` if chardet is
                 not available.
        """
        try:
            import chardet
            if sys.version_info[0] == 3:
                encoding = chardet.detect(bytes(data))['encoding']
            else:
                encoding = chardet.detect(data)['encoding']
        except ImportError:
            logger.warning("chardet not available, using utf8 by default")
            encoding = self.getDefaultEncoding()
        return encoding

    @staticmethod
    def getDefaultEncoding():
        """ Returns the result of :py:func:`sys.getfilesystemencoding` """
        return sys.getfilesystemencoding()

    def readFile(self, filePath, replaceTabsBySpaces=True, encoding=None,
                 detectEncoding=False):
        # encoding = "utf-8"
        with open(filePath, 'rb') as f:
            data = f.read()
            if not encoding and detectEncoding:
                try:
                    encoding = self.detectEncoding(data)
                except UnicodeEncodeError:
                    QtGui.QMessageBox.warning(self, "Failed to open file",
                                              "Failed to open file, encoding "
                                              "could not be detected properly")
            if not encoding:
                encoding = self.getDefaultEncoding()
            content = data.decode(encoding)
        if replaceTabsBySpaces:
            content = content.replace(
                "\t", " " * self.settings.value("tabLength"))
        return content, encoding

    def openFile(self, filePath, replaceTabsBySpaces=True, encoding=None,
                 detectEncoding=False):
        """
        Helper method to open a file in the editor.

        :param filePath: The file path to open
        :type filePath: str

        :param replaceTabsBySpaces: True to replace tabs by spaces
               (settings.value("tabSpace") * " ")
        :type replaceTabsBySpaces: bool

        :param encoding: The encoding to use. If no encoding is provided and
                         detectEncoding is false, pyqode will try to decode the
                         content using the system default encoding.
        :type encoding: str

        :param detectEncoding: If true and no encoding is specified, pyqode will
                               try to detect encoding using chardet.
        :type detectEncoding: bool
        """
        content, encoding = self.readFile(filePath, replaceTabsBySpaces,
                                          encoding, detectEncoding)
        self.__filePath = filePath
        self.__fileEncoding = encoding
        self.setPlainText(content)
        self.dirty = False

    def lineText(self, lineNbr):
        """
        Gets the current line text.

        :param lineNbr: The line number of the text to get

        :return: Entire line's text
        :rtype: str
        """
        tc = self.textCursor()
        tc.movePosition(tc.Start)
        tc.movePosition(tc.Down, tc.MoveAnchor, lineNbr - 1)
        tc.select(tc.LineUnderCursor)
        return tc.selectedText()

    def setLineText(self, lineNbr, text):
        """
        Replace the text of a single line by the supplied text.

        :param lineNbr: The line number of the text to remove
        :type: lineNbr: int

        :param text: Replacement text
        :type: text: str
        """
        tc = self.textCursor()
        tc.movePosition(tc.Start)
        tc.movePosition(tc.Down, tc.MoveAnchor, lineNbr - 1)
        tc.select(tc.LineUnderCursor)
        tc.insertText(text)

    def removeLastLine(self):
        """
        Removes the last line of the document.
        """
        tc = self.textCursor()
        tc.movePosition(tc.End, tc.MoveAnchor)
        tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
        tc.movePosition(tc.End, tc.KeepAnchor)
        tc.removeSelectedText()
        tc.deletePreviousChar()
        self.setTextCursor(tc)

    def cleanupDocument(self):
        """
        Removes trailing whitespaces and ensure one single blank line at the end
        of the QTextDocument. (call setPlainText to update the text).
        """
        value = self.verticalScrollBar().value()
        pos = self.cursorPosition
        atBlockEnd = self.textCursor().atBlockEnd()

        self.textCursor().beginEditBlock()

        # cleanup whitespaces
        self.__cleaning = True
        eaten = 0
        for line in self.__modifiedLines:
            for j in range(-1, 2):
                if line + j != pos[0]:
                    txt = self.lineText(line + j)
                    stxt = txt.rstrip()
                    self.setLineText(line + j, stxt)

        if self.lineText(self.lineCount()):
            self.appendPlainText("\n")
        else:
            # remove last blank line (except one)
            i = 0
            while True:
                l = self.lineText(self.lineCount() - i)
                if l:
                    break
                i += 1
            for j in range(i-1):
                self.removeLastLine()

        self.__cleaning = False
        self.__originalText = self.toPlainText()

        # restore cursor and scrollbars
        tc = self.textCursor()
        tc.movePosition(tc.Start)
        tc.movePosition(tc.Down, tc.MoveAnchor, pos[0] - 1)
        tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
        p = tc.position()
        tc.select(tc.LineUnderCursor)
        if tc.selectedText():
            tc.setPosition(p)
            offset = pos[1] - eaten
            tc.movePosition(tc.Right, tc.MoveAnchor, offset)
        else:
            tc.setPosition(p)
        self.setTextCursor(tc)
        self.verticalScrollBar().setValue(value)

        self.textCursor().endEditBlock()

    @QtCore.Slot()
    def saveToFile(self, filePath=None, encoding=None, force=False):
        """
        Saves the plain text to a file.

        :param filePath: Optional file path. If None, we use the current file
                         path (set by openFile).
        :type filePath: str or None

        :param encoding: Optional encoding. If None, the method will use the
                         last encoding used to open/save the file.

        :return: The operation status as a bool (True for success)
        """
        if not self.dirty and not force:
            return True
        self.textSaving.emit(filePath)
        if len(self.toPlainText()):
            self.cleanupDocument()
        if not filePath:
            if self.filePath:
                filePath = self.filePath
            else:
                return False
        if encoding:
            self.__fileEncoding = encoding
        try:
            content = self.__encodePlainText(self.fileEncoding)
        except UnicodeEncodeError:
            content = self.__encodePlainText(self.getDefaultEncoding())
        with open(filePath, "wb") as f:
            f.write(content)
        self.dirty = False
        self.__filePath = filePath
        self.textSaved.emit(filePath)
        return True

    def installMode(self, mode):
        """
        Installs a mode on the editor.

        The mode is set as an object attribute using the mode's name as the key.

        :param mode: The mode instance to install.
        :type mode: pyqode.core.Mode
        """
        self.__modes[mode.name] = mode
        mode._onInstall(self)
        setattr(self, mode.name, mode)

    def uninstallMode(self, name):
        """
        Uninstalls a previously installed mode.

        :param name: The name of the mode to uninstall

        :return:
        """
        m = self.mode(name)
        if m:
            m._onUninstall()
            self.__modes.pop(name, None)
        self.__dict__.pop(name, None)

    def mode(self, name):
        """
        Gets a mode by name.

        .. deprecated:: 1.0
            Use :py:func:`getattr` instead. This method will be remove in the
            next version.

        :raise: KeyError if the mode has not been installed.

        :param name: The name of the mode to get
        :type name: str

        :rtype: pyqode.Mode
        """
        return self.__modes[name]

    def modes(self):
        """
        Returns the dictionary of modes.
        """
        return self.__modes

    def installPanel(self, panel, position=PanelPosition.LEFT):
        """
        Installs a panel on on the editor. You must specify the position of the
        panel (panels are rendered in one of the four document margins, see
        :class:`pyqode.core.PanelPosition`.

        The panel is set as an object attribute using the panel's name as the
        key.

        :param panel: The panel instance to install
        :param position: The panel position

        :type panel: pyqode.core.Panel
        :type position: int
        """
        panel.zoneOrder = len(self.__panels[position])
        self.__panels[position][panel.name] = panel
        panel._onInstall(self)
        self.__updateViewportMargins()
        setattr(self, panel.name, panel)

    def uninstallPanel(self, name, zone):
        """
        Uninstalls a previously installed panel.

        :param name: The name of the panel to uninstall

        :return:
        """
        m = self.__panels[zone][name]
        if m:
            try:
                m._onUninstall()
            except (RuntimeError, AttributeError):
                pass
            self.__panels[zone].pop(name, None)
        self.__dict__.pop(name, None)

    def panels(self):
        """
        Returns the panels dictionary.

        :return: A dictionary of :class:`pyqode.core.Panel`
        :rtype: dict
        """
        return self.__panels

    def addDecoration(self, decoration):
        """
        Adds a text decoration.

        :param decoration: Text decoration
        :type decoration: pyqode.core.TextDecoration
        """
        if decoration not in self.__selections:
            self.__selections.append(decoration)
            self.__selections = sorted(self.__selections,
                                       key=lambda sel: sel.draw_order)
            self.setExtraSelections(self.__selections)

    def removeDecoration(self, decoration):
        """
        Remove text decoration.

        :param decoration: The decoration to remove
        :type decoration: pyqode.core.TextDecoration
        """
        try:
            self.__selections.remove(decoration)
            self.setExtraSelections(self.__selections)
        except ValueError:
            pass

    def clearDecorations(self):
        """
        Clears all text decorations
        """
        self.__selections[:] = []
        self.setExtraSelections(self.__selections)

    def marginSize(self, position=PanelPosition.LEFT):
        """
        Gets the size of a specific margin.

        :param position: Margin position. See :class:`pyqode.core.PanelPosition`

        :return: The size of the specified margin
        :rtype: float
        """
        return self.__marginSizes[position]

    def selectFullLines(self, start, end, applySelection=True):
        """
        Select entire lines between start and end.

        :param start: Start line number (1 based)
        :type start: int
        :param end: End line number (1 based)
        :type end: int

        :param applySelection: True to apply the selection before returning the
                               QTextCursor
        :type applySelection: bool

        :return A QTextCursor that holds the requested selection
        """
        if start and end:
            tc = self.textCursor()
            tc.movePosition(QtGui.QTextCursor.Start,
                            QtGui.QTextCursor.MoveAnchor)
            tc.movePosition(QtGui.QTextCursor.Down,
                            QtGui.QTextCursor.MoveAnchor, start - 1)
            if end > start:  # Going down
                tc.movePosition(QtGui.QTextCursor.Down,
                                QtGui.QTextCursor.KeepAnchor,
                                end - start)
                tc.movePosition(QtGui.QTextCursor.EndOfLine,
                                QtGui.QTextCursor.KeepAnchor)
            elif end < start:  # going up
                # don't miss end of line !
                tc.movePosition(QtGui.QTextCursor.EndOfLine,
                                QtGui.QTextCursor.MoveAnchor)
                tc.movePosition(QtGui.QTextCursor.Up,
                                QtGui.QTextCursor.KeepAnchor,
                                start - end)
                tc.movePosition(QtGui.QTextCursor.StartOfLine,
                                QtGui.QTextCursor.KeepAnchor)
            else:
                tc.movePosition(QtGui.QTextCursor.EndOfLine,
                                QtGui.QTextCursor.KeepAnchor)
            if applySelection:
                self.setTextCursor(tc)

    def selectionRange(self):
        """
        Returns the selected lines boundaries (start line, end line)

        :return: tuple(int, int)
        """
        doc = self.document()
        start = doc.findBlock(
            self.textCursor().selectionStart()).blockNumber() + 1
        end = doc.findBlock(
            self.textCursor().selectionEnd()).blockNumber() + 1
        if start != end and self.textCursor().columnNumber() == 0:
            end -= 1
        return start, end

    def linePos(self, line_number):
        """
        Gets the line pos on the Y-Axis (at the center of the line) from a
        line number (1 based).

        :param line_number: The line number for which we want to know the
                            position in pixels.

        :return: The center position of the line.
        :rtype: int or None
        """
        block = self.document().findBlockByNumber(line_number)
        if block:
            return int(self.blockBoundingGeometry(block).translated(
                self.contentOffset()).top())
        return None

    def lineNumber(self, y_pos):
        """
        Returns the line number from the y_pos

        :param y_pos: Y pos in the QCodeEdit

        :return: Line number (1 based)
        :rtype: int
        """
        height = self.fontMetrics().height()
        for top, l, block in self.__blocks:
            if top <= y_pos <= top + height:
                return l
        return None

    def resetZoom(self):
        """
        Resets the zoom value.
        """
        self.style.setValue("fontSize", constants.FONT_SIZE)

    def markWholeDocumentDirty(self):
        """
        Marks the whole document as dirty to force a full refresh. **SLOW**
        """
        tc = self.textCursor()
        tc.select(tc.Document)
        self.document().markContentsDirty(tc.selectionStart(),
                                          tc.selectionEnd())

    def zoomIn(self, increment=1):
        """
        Zooms in the editor.

        The effect is achieved by increasing the editor font size by the
        increment value.

        Panels that needs to be resized depending on the font size need to
        implement onStyleChanged.
        """
        self.style.setValue("fontSize",
                            self.style.value("fontSize") + increment)
        self.markWholeDocumentDirty()

    def zoomOut(self, increment=1):
        """
        Zooms out the editor.

        The effect is achieved by decreasing the editor font size by the
        increment value.

        Panels that needs to be resized depending on the font size need to
        implement onStyleChanged and trigger an update.
        """
        value = self.style.value("fontSize") - increment
        if value <= 0:
            value = increment
        self.style.setValue("fontSize", value)
        self.markWholeDocumentDirty()

    def getLineIndent(self):
        """
        Returns the current line indentation

        :return: Number of spaces that makes the indentation level of the
                 current line
        """
        original_cursor = self.textCursor()
        cursor = QtGui.QTextCursor(original_cursor)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                            QtGui.QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        indentation = len(line) - len(line.lstrip())
        self.setTextCursor(original_cursor)
        return indentation

    def setShowWhitespaces(self, show):
        """
        Shows/Hides whitespaces.

        :param show: True to show whitespaces, False to hide them
        :type show: bool
        """
        doc = self.document()
        options = doc.defaultTextOption()
        if show:
            options.setFlags(options.flags() |
                             QtGui.QTextOption.ShowTabsAndSpaces)
        else:
            options.setFlags(options.flags() &
                             ~QtGui.QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(options)

    @QtCore.Slot()
    def duplicateLine(self):
        """
        Duplicates the line under the cursor. If multiple lines are selected,
        only the last one is duplicated.
        """
        tc = self.textCursor()
        tc.select(tc.LineUnderCursor)
        line = tc.selectedText()
        tc.movePosition(tc.Down, tc.MoveAnchor)
        tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
        tc.insertText(line + "\n")
        tc.movePosition(tc.Left, tc.MoveAnchor)
        self.setTextCursor(tc)
        self.__doHomeKey()

    @QtCore.Slot()
    def indent(self):
        """
        Indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.QCodeEdit.indentRequested` signal, the
        :class:`pyqode.core.IndenterMode` will perform the actual indentation.
        """
        self.indentRequested.emit()

    @QtCore.Slot()
    def unIndent(self):
        """
        Un-indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.QCodeEdit.unIndentRequested` signal, the
        :class:`pyqode.core.IndenterMode` will perform the actual
        un-indentation.
        """
        self.unIndentRequested.emit()

    def setCursor(self, cursor):
        """
        Changes the viewport cursor

        :param cursor: the nex mouse cursor to set.
        :type cursor: QtGui.QCursor
        """
        self.viewport().setCursor(cursor)
        QtGui.QApplication.processEvents()

    def refreshPanels(self):
        """ Refreshes the editor panels. """
        self.__resizePanels()
        self.__updateViewportMargins()
        self.__updatePanels(self.contentsRect(), 0)
        self.update()

    def resizeEvent(self, e):
        """
        Overrides resize event to resize the editor's panels.

        :param e: resize event
        """
        QtGui.QPlainTextEdit.resizeEvent(self, e)
        self.__resizePanels()

    def paintEvent(self, e):
        """
        Overrides paint event to update the list of visible blocks and emit
        the painted event.

        :param e: paint event
        """
        self.updateVisibleBlocks(e)
        QtGui.QPlainTextEdit.paintEvent(self, e)
        self.painted.emit(e)

    def keyPressEvent(self, event):
        """
        Overrides the keyPressEvent to emit the keyPressed signal.

        Also takes care of indenting and handling smarter home key.

        :param event: QKeyEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        replace = self.settings.value("useSpacesInsteadOfTab")
        if replace and event.key() == QtCore.Qt.Key_Tab:
            self.indent()
            event.accept()
        elif replace and event.key() == QtCore.Qt.Key_Backtab:
            self.unIndent()
            event.accept()
        elif event.key() == QtCore.Qt.Key_Home:
            self.__doHomeKey(
                event, int(event.modifiers()) & QtCore.Qt.ShiftModifier)
        elif (event.key() == QtCore.Qt.Key_D and
              event.modifiers() & QtCore.Qt.ControlModifier):
            self.duplicateLine()
            event.accept()
        self.keyPressed.emit(event)
        state = event.isAccepted()
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
        event.setAccepted(state)
        self.postKeyPressed.emit(event)

    def keyReleaseEvent(self, event):
        """
        Overrides keyReleaseEvent to emit the keyReleased signal.

        :param event: QKeyEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        self.keyReleased.emit(event)
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.keyReleaseEvent(self, event)

    def focusInEvent(self, event):
        """
        Overrides focusInEvent to emits the focusedIn signal

        :param event: QFocusEvent
        """
        self.focusedIn.emit(event)
        QtGui.QPlainTextEdit.focusInEvent(self, event)
        self.repaint()
        QtGui.QApplication.processEvents()

    def focusOutEvent(self, QFocusEvent):
        if self.settings.value("saveOnFrameDeactivation"):
            self.saveToFile()

    def mousePressEvent(self, event):
        """
        Overrides mousePressEvent to emits mousePressed signal

        :param event: QMouseEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        self.mousePressed.emit(event)
        c = self.cursorForPosition(event.pos())
        for sel in self.__selections:
            if sel.cursor.blockNumber() == c.blockNumber():
                sel.signals.clicked.emit(sel)
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Emits mouseReleased signal.

        :param event: QMouseEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        self.mouseReleased.emit(event)
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        """
        Emits the mouseWheelActivated signal.

        :param event: QMouseEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        self.mouseWheelActivated.emit(event)
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.wheelEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouseMovedEvent to display any decoration tooltip and emits
        the mouseMoved event.
        """
        c = self.cursorForPosition(event.pos())
        self._lastMousePos = event.pos()
        blockFound = False
        for sel in self.__selections:
            if sel.cursor.blockNumber() == c.blockNumber() and sel.tooltip:
                if self.__previousTooltipBlockNumber != c.blockNumber():
                    self.__tooltipRunner.requestJob(
                        self.showTooltip, False,
                        self.mapToGlobal(event.pos()), sel.tooltip[0: 1024])
                self.__previousTooltipBlockNumber = c.blockNumber()
                blockFound = True
                break
        if not blockFound:
            if self.__previousTooltipBlockNumber != -1:
                QtGui.QToolTip.hideText()
            self.__previousTooltipBlockNumber = -1
            self.__tooltipRunner.cancelRequests()
        self.mouseMoved.emit(event)
        QtGui.QPlainTextEdit.mouseMoveEvent(self, event)

    def showTooltip(self, pos, tooltip):
        """
        Show a tool tip at the specified position

        :param pos: Tooltip position

        :param tooltip: Tooltip text
        """
        QtGui.QToolTip.showText(pos, tooltip[0: 1024], self)
        self.__previousTooltipBlockNumber = -1

    def showEvent(self, QShowEvent):
        """ Overrides showEvent to update the viewport margins """
        QtGui.QPlainTextEdit.showEvent(self, QShowEvent)
        self.__updateViewportMargins()

    def setPlainText(self, txt):
        """
        Overrides the setPlainText method to keep track of the original text.

        Emits the newTextSet signal.

        :param txt: The new text to set.
        """
        QtGui.QPlainTextEdit.setPlainText(self, txt)
        self.__originalText = txt
        self.__modifiedLines.clear()
        self.__onSettingsChanged("", "")
        self.newTextSet.emit()
        self.redoAvailable.emit(False)
        self.undoAvailable.emit(False)
        title = QtCore.QFileInfo(self.filePath).fileName()
        self.setDocumentTitle(title)
        self.setWindowTitle(title)

    def addAction(self, action):
        """
        Adds an action to the editor's context menu.

        :param action: QtGui.QAction
        """
        self.__actions.append(action)
        QtGui.QPlainTextEdit.addAction(self, action)

    def actions(self):
        """
        Returns the list of actions/seprators of the context menu.
        :return:
        """
        return self.__actions

    def addSeparator(self):
        """
        Adds a seprator to the editor's context menu.

        :return: The sepator that has been added.
        :rtype: QtGui.QAction
        """
        action = QtGui.QAction(self)
        action.setSeparator(True)
        self.__actions.append(action)
        return action

    def removeAction(self, action):
        """
        Removes an action/separator from the editor's context menu.

        :param action: Action/seprator to remove.
        """
        self.__actions.remove(action)

    def __createDefaultActions(self):
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-undo",
                                  QtGui.QIcon(constants.ACTION_UNDO[0])),
            "Undo", self)
        a.setShortcut(constants.ACTION_UNDO[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.undo)
        self.undoAvailable.connect(a.setEnabled)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-redo",
                                  QtGui.QIcon(constants.ACTION_REDO[0])),
            "Redo", self)
        a.setShortcut(constants.ACTION_REDO[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.redo)
        self.redoAvailable.connect(a.setEnabled)
        self.addAction(a)
        self.addSeparator()
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme(
                "edit-copy", QtGui.QIcon(constants.ACTION_COPY[0])),
            "Copy", self)
        a.setShortcut(constants.ACTION_COPY[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.copy)
        self.copyAvailable.connect(a.setEnabled)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-cut",
                                  QtGui.QIcon(constants.ACTION_CUT[0])),
            "Cut", self)
        a.setShortcut(constants.ACTION_CUT[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.cut)
        self.copyAvailable.connect(a.setEnabled)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-paste",
                                  QtGui.QIcon(constants.ACTION_PASTE[0])),
            "Paste", self)
        a.setShortcut(constants.ACTION_PASTE[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.paste)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-delete",
                                  QtGui.QIcon(constants.ACTION_DELETE[0])),
            "Delete", self)
        a.setShortcut(constants.ACTION_DELETE[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.delete)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-select-all",
                                  QtGui.QIcon(constants.ACTION_SELECT_ALL[0])),
            "Select all", self)
        a.setShortcut(constants.ACTION_SELECT_ALL[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.selectAll)
        self.addAction(a)
        self.addSeparator()
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("format-indent-more",
                                  QtGui.QIcon(constants.ACTION_INDENT[0])),
            "Indent", self)
        a.setShortcut(constants.ACTION_INDENT[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.indent)
        self.addAction(a)
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("format-indent-less",
                                  QtGui.QIcon(constants.ACTION_UNINDENT[0])),
            "Un-indent", self)
        a.setShortcut(constants.ACTION_UNINDENT[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.unIndent)
        self.addAction(a)
        self.addSeparator()
        a = QtGui.QAction(
            QtGui.QIcon.fromTheme("start-here",
                                  QtGui.QIcon(constants.ACTION_GOTO_LINE[0])),
            "Go to line", self)
        a.setShortcut(constants.ACTION_GOTO_LINE[1])
        a.setIconVisibleInMenu(True)
        a.triggered.connect(self.gotoLine)
        self.addAction(a)

    def __initSettings(self):
        """
        Init the settings PropertyRegistry
        """
        self.__settings = PropertyRegistry()
        self.settings.valueChanged.connect(self.__onSettingsChanged)
        self.settings.addProperty("showWhiteSpaces", False)
        self.settings.addProperty("tabLength", constants.TAB_SIZE)
        self.settings.addProperty("useSpacesInsteadOfTab", True)
        self.settings.addProperty("minIndentColumn", 0)
        self.settings.addProperty("saveOnFrameDeactivation", True)

    def __initStyle(self):
        """
        Init the style PropertyRegistry
        """
        self.__style = PropertyRegistry()
        self.style.valueChanged.connect(self.__resetPalette)
        self.style.addProperty("font", constants.FONT)
        self.style.addProperty("fontSize", constants.FONT_SIZE)
        self.style.addProperty("background", constants.EDITOR_BACKGROUND)
        self.style.addProperty("foreground", constants.EDITOR_FOREGROUND)
        self.style.addProperty("whiteSpaceForeground",
                               constants.EDITOR_WS_FOREGROUND)
        self.style.addProperty("selectionBackground",
                               self.palette().highlight().color())
        self.style.addProperty("selectionForeground",
                               self.palette().highlightedText().color())
        self.__resetPalette("", "")

    def __encodePlainText(self, encoding):
        if sys.version_info[0] == 3:
            content = bytes(self.toPlainText().encode(encoding))
        else:
            content = unicode(self.toPlainText()).encode(encoding)
        return content

    def updateVisibleBlocks(self, event):
        """
        Update the list of visible blocks/lines position.

        :param event: QtGui.QPaintEvent
        """
        self.__blocks[:] = []
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        ebottom_top = 0
        ebottom_bottom = self.height()
        while block.isValid():
            visible = (top >= ebottom_top and bottom <= ebottom_bottom)
            if not visible:
                break
            if block.isVisible():
                self.__blocks.append((top, blockNumber+1, block))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()

    def __computeZonesSizes(self):
        # Left panels
        left = 0
        for panel in self.__panels[PanelPosition.LEFT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            left += sh.width()
        # Right panels
        right = 0
        for panel in self.__panels[PanelPosition.RIGHT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            right += sh.width()
        # Top panels
        top = 0
        for panel in self.__panels[PanelPosition.TOP].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            top += sh.height()
        # Bottom panels
        bottom = 0
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            bottom += sh.height()
        self.top, self.left, self.right, self.bottom = top, left, right, bottom
        return bottom, left, right, top

    def __resizePanels(self):
        """
        Resizes panels geometries
        """
        cr = self.contentsRect()
        vcr = self.viewport().contentsRect()
        s_bottom, s_left, s_right, s_top = self.__computeZonesSizes()
        w_offset = cr.width() - (vcr.width() + s_left + s_right)
        h_offset = cr.height() - (vcr.height() + s_bottom + s_top)
        left = 0
        panels = list(self.__panels[PanelPosition.LEFT].values())
        panels.sort(key=lambda panel: panel.zoneOrder, reverse=True)
        for panel in panels:
            if not panel.isVisible():
                continue
            panel.adjustSize()
            sh = panel.sizeHint()
            panel.setGeometry(cr.left() + left, cr.top() + s_top,
                              sh.width(),
                              cr.height() - s_bottom - s_top - h_offset)
            left += sh.width()
        right = 0
        panels = list(self.__panels[PanelPosition.RIGHT].values())
        panels.sort(key=lambda panel: panel.zoneOrder, reverse=True)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.right() - right - sh.width() - w_offset,
                              cr.top(), sh.width(), cr.height() - h_offset)
            right += sh.width()
        top = 0
        panels = list(self.__panels[PanelPosition.TOP].values())
        panels.sort(key=lambda panel: panel.zoneOrder)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(), cr.top() + top,
                              cr.width() - w_offset,
                              sh.height())
            top += sh.height()
        bottom = 0
        panels = list(self.__panels[PanelPosition.BOTTOM].values())
        panels.sort(key=lambda panel: panel.zoneOrder)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(),
                              cr.bottom() - bottom - sh.height() - h_offset,
                              cr.width() - w_offset, sh.height())
            bottom += sh.height()

    def __updatePanels(self, rect, dy):
        """
        Updates the panel on update request. (Scroll, update clipping rect,...)
        """
        for zones_id, zone in self.__panels.items():
            if zones_id == PanelPosition.TOP or \
               zones_id == PanelPosition.BOTTOM:
                continue
            panels = list(zone.values())
            for panel in panels:
                if not panel.scrollable:
                    continue
                if dy:
                    panel.scroll(0, dy)
                else:
                    l, c = self.cursorPosition
                    ol, oc = self.__cachedCursorPos
                    if l != ol or c != oc:
                        panel.update(0, rect.y(), panel.width(), rect.height())
                    self.__cachedCursorPos = self.cursorPosition
        if rect.contains(self.viewport().rect()):
            self.__updateViewportMargins()

    def __ontextChanged(self):
        """
        Updates dirty flag on text changed.
        """
        if not self.__cleaning:
            self.__modifiedLines.add(self.cursorPosition[0])
            txt = self.toPlainText()
            self.dirty = (txt != self.__originalText)

    def __updateViewportMargins(self):
        """
        Updates the viewport margins depending on the installed panels
        """
        top = 0
        left = 0
        right = 0
        bottom = 0
        for panel in self.__panels[PanelPosition.LEFT].values():
            if panel.isVisible():
                left += panel.sizeHint().width()
        for panel in self.__panels[PanelPosition.RIGHT].values():
            if panel.isVisible():
                right += panel.sizeHint().width()
        for panel in self.__panels[PanelPosition.TOP].values():
            if panel.isVisible():
                top += panel.sizeHint().height()
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            if panel.isVisible():
                bottom += panel.sizeHint().height()
        self.__marginSizes = (top, left, right, bottom)
        self.setViewportMargins(left, top, right, bottom)

    def __resetPalette(self, section, key):
        """ Resets stylesheet. """
        if key == "font" or key == "fontSize" or not key:
            font = self.style.value("font")
            self.setFont(QtGui.QFont(font, self.style.value("fontSize")))
        if (key == "background" or key == "foreground" or
                key == "selectionBackground" or key == "selectionForeground"
                or not key):
            p = self.palette()
            c = self.style.value("background")
            p.setColor(p.Base, c)
            c = self.style.value("foreground")
            p.setColor(p.Text, c)
            c = self.style.value("selectionBackground")
            p.setColor(QtGui.QPalette.Highlight, c)
            c = self.style.value("selectionForeground")
            p.setColor(QtGui.QPalette.HighlightedText, c)
            self.setPalette(p)

    def __onSettingsChanged(self, section, key):
        self.setTabStopWidth(int(self.settings.value("tabLength")) *
                             self.fontMetrics().widthChar(" "))
        self.setShowWhitespaces(self.settings.value("showWhiteSpaces"))

    def __doHomeKey(self, event=None, select=False):
        # get nb char to first significative char
        delta = self.textCursor().positionInBlock() - self.getLineIndent()
        if delta:
            tc = self.textCursor()
            move = QtGui.QTextCursor.MoveAnchor
            if select:
                move = QtGui.QTextCursor.KeepAnchor
            tc.movePosition(
                QtGui.QTextCursor.Left, move, delta)
            self.setTextCursor(tc)
            if event:
                event.accept()
