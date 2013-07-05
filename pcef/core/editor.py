"""
This module contains the definition of the QCodeEdit
"""
import logging
import sys
import pcef
from pcef.qt import QtGui, QtCore
from pcef.core import constants
from pcef.core.constants import PanelPosition, CODE_EDIT_STYLESHEET
from pcef.core.properties import PropertyRegistry


class QCodeEdit(QtGui.QPlainTextEdit):
    """
    This is the core code editor widget which inherits from a QPlainTextEdit

    The code editor provides a series of additional slots specifically suited
    for code edition:
        - keyboard events
        - mouse events
        - save / dirty events

    The widget appearance and behaviour can be customised by adding modes and
    panels (editor extensions).

    Panels are drawn in the document margin by the panel manager.

    The widget also provides a series of convenience methods to:
        - open/save a file
        - manipulate the text cursor / getting text informations (line, col,...)

    The widget exposes a style property which is a dictionary of properties
    (more about this topic in the style section)
    """
    #: Paint hook
    painted = QtCore.Signal(QtGui.QPaintEvent)
    #: Signal emitted when a new text is set on the widget
    newTextSet = QtCore.Signal()
    #: Signal emitted when the text is saved
    textSaved = QtCore.Signal(str)
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

    @property
    def dirty(self):
        """
        Gets the dirty flag
        """
        return self.__dirty

    @dirty.setter
    def dirty(self, value):
        """
        Sets the dirty flag,

        .. note: The dirtyChanged signal is emitted if the new value is
                 different from the current value

        :param value: The new value
        """
        if self.__dirty != value:
            self.__dirty = value
            self.dirtyChanged.emit(value)

    @property
    def cursorPosition(self):
        """
        Returns the text cursor position (line, column)

        :return: The cursor position (line, column)
        :rtype: tuple(int, int)
        """
        return (self.textCursor().blockNumber() + 1,
                self.textCursor().columnNumber())

    @property
    def fileName(self):
        """
        Returns the file name (see QFileInfo.fileName)
        """
        return QtCore.QFileInfo(self.filePath).fileName()

    @property
    def filePath(self):
        """
        Returns the file path
        """
        return self.__filePath

    @property
    def fileEncoding(self):
        """
        Returns last encoding used to open the file
        """
        return self.__fileEncoding

    @property
    def visibleBlocks(self):
        """
        Returns the list of visible blocks/lines

        Each block is a tuple made up of the line top position and the line
        number (already 1 based)

        :return: A list of tuple(top position, line number)
        :rtype List of tuple(int, int)
        """
        return self.__blocks

    def __init__(self, parent=None):
        """
        :param parent: QWidget
        """
        QtGui.QPlainTextEdit.__init__(self, parent)
        self.__blocks = []
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

    def detectEncoding(self, data):
        """
        Try to use chardet to detect encoding.

        :param data: Data from which we want to detect the encoding.
        :type str/bytes

        :return The detected encoding. Return the getDefaultEncoding if chardet
        is not available.
        """
        try:
            import chardet
            if sys.version_info[0] == 3:
                encoding = chardet.detect(bytes(data))['encoding']
            else:
                encoding = chardet.detect(data)['encoding']
        except ImportError:
            logging.getLogger("pcef").warning("chardet not available, "
                                                 "using utf8 by default")
            encoding = self.getDefaultEncoding()
        return encoding

    def getDefaultEncoding(self):
        return sys.getfilesystemencoding()

    def openFile(self, filePath, replaceTabsBySpaces=True, encoding=None):
        """
        Helper method to open a file in the editor.

        :param filePath: The file path to open

        :param replaceTabsBySpaces: True to replace tabs by spaces
               (settings.value("tabSpace") * " ")
        """
        with open(filePath, 'rb') as f:
            data = f.read()
            if not encoding:
                encoding = self.detectEncoding(data)
            content = data.decode(encoding)
        if replaceTabsBySpaces:
            content = content.replace(
                "\t", " " * self.settings.value("tabLength"))
        self.__filePath = filePath
        self.__fileEncoding = encoding
        self.setPlainText(content)
        self.dirty = False

    @QtCore.Slot()
    def saveToFile(self, filePath=None, encoding=None):
        """
        Save to file.

        :param filePath: Optional file path. The file path is assumed to exists.
        It can be None or empty to used the open file name.

        :return: The operation status as a bool (True for success)
        """
        if not filePath:
            if self.filePath:
                filePath = self.filePath
            else:
                return False
        if encoding:
            self.fileEncoding = encoding
        try:
            content = self.__encodePlainText(self.fileEncoding)
        except UnicodeEncodeError:
            content = self.__encodePlainText(self.getDefaultEncoding())
        with open(filePath, "wb") as f:
            f.write(content)
        self.textSaved.emit(filePath)
        self.newTextSet.emit()
        self.dirty = False
        self.__filePath = filePath
        return True

    def installMode(self, mode):
        """
        Installs a mode

        :param mode: The mode instance to install on this widget instance
        """
        self.__modes[mode.name] = mode
        mode.install(self)
        setattr(self, mode.name, mode)

    def uninstallMode(self, name):
        """
        Uninstalls a previously installed mode.

        :param name: The name of the mode to uninstall

        :return:
        """
        m = self.mode(name)
        if m:
            m.uninstall()
            self.__panels.pop(name, None)
        self.__dict__.pop(name, None)

    def mode(self, name):
        """
        Gets a mode by name

        :param name: The name of the mode to get
        :type name: str

        :rtype: pcef.Mode or None
        """
        try:
            return self.__modes[name]
        except KeyError:
            return None

    def modes(self):
        """
        Returns the dictionary of modes
        """
        return self.__modes

    def installPanel(self, panel, position=PanelPosition.LEFT):
        """
        Install a panel on the QCodeEdit

        :param panel: The panel instance to install

        :param position: The panel position

        """
        self.__panels[position][panel.name] = panel
        panel.install(self)
        self.__updateViewportMargins()
        setattr(self, panel.name, panel)

    def panels(self):
        """
        Returns the panels dictionary
        """
        return self.__panels

    def addDecoration(self, decoration):
        """
        Adds a text decoration

        :param decoration: Text decoration
        :type decoration: pcef.TextDecoration
        """
        self.__selections.append(decoration)
        self.__selections = sorted(self.__selections,
                                   key=lambda sel: sel.draw_order)
        self.setExtraSelections(self.__selections)

    def removeDecoration(self, decoration):
        """
        Remove text decoration.

        :param decoration: The decoration to remove
        :type decoration: pcef.TextDecoration
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

    def selectFullLines(self, start, end, applySelection=True):
        """
        Select entire lines between start and end

        :param start: Start line number (1 based)

        :param end: End line number (1 based)

        :param applySelection: True to apply the selection before returning the
                               QTextCursor

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
        Gets the line pos on the Y-Axis in pixels (at the center of the line)

        :param line_number: The line number for which we want to know the
                            position in pixels.

        :rtype int or None
        """
        height = self.fontMetrics().height()
        for top, l in self.__blocks:
            if l == line_number:
                return top + height / 2.0
        return None

    def lineNumber(self, y_pos):
        """
        Get the line number from the y_pos
        :param y_pos: Y pos in the QCodeEdit
        """
        height = self.fontMetrics().height()
        for top, l in self.__blocks:
            if top <= y_pos <= top + height:
                return l
        return None

    def resetZoom(self):
        """
        Resets the zoom value
        """
        self.style.setValue("fontSize", constants.FONT_SIZE)

    def zoomIn(self, increment=1):
        """
        Zoom in the editor.

        The effect is achieved by increasing the editor font size by the
        increment value.

        .. note: Panels that needs to be resized depending on the font size
        should implement onStyleChanged and trigger an update.
        """
        self.style.setValue("fontSize",
                            self.style.value("fontSize") + increment)

    def zoomOut(self, increment=1):
        """
        Zoom out the editor.

        The effect is achieved by decreasing the editor font size by the
        increment value.

        .. note: Panels that needs to be resized depending on the font size
        should implement onStyleChanged and trigger an update.
        """
        value = self.style.value("fontSize") - increment
        if value <= 0:
            value = increment
        self.style.setValue("fontSize", value)

    def getLineIndent(self):
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

    def indent(self):
        """
        Indent current line or selection (based on settings.value("tabLength"))
        """
        if self.settings.value("useSpacesInsteadOfTab"):
            size = self.settings.value("tabLength")
            cursor = self.textCursor()
            cursor.beginEditBlock()
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            has_selection = True
            if not cursor.hasSelection():
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
                has_selection = False
            nb_lines = len(cursor.selection().toPlainText().splitlines())
            if nb_lines == 0:
                nb_lines = 1
            cursor.setPosition(cursor.selectionStart())
            nbSpacesAdded = 0
            startOffset = 0
            for i in range(nb_lines):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                indentation = self.getLineIndent()
                nbSpaces = size - (indentation % size)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.insertText(" " * nbSpaces)
                cursor.movePosition(QtGui.QTextCursor.EndOfLine)
                cursor.setPosition(cursor.position() + 1)
                nbSpacesAdded += nbSpaces
                if not i:
                    startOffset = nbSpaces
            cursor.setPosition(sel_start + startOffset)
            if has_selection:
                cursor.setPosition(sel_end + nbSpacesAdded,
                                   QtGui.QTextCursor.KeepAnchor)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
        else:
            self.keyPressEvent(
                QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Tab,
                                QtCore.Qt.NoModifier))

    def unIndent(self):
        """
        Unindent current line or selection by tabLength
        """
        if self.settings.value("useSpacesInsteadOfTab"):
            size = self.settings.value("tabLength")
            cursor = self.textCursor()
            cursor.beginEditBlock()
            pos = cursor.position()
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            has_selection = True
            if not cursor.hasSelection():
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
                has_selection = False
            nb_lines = len(cursor.selection().toPlainText().splitlines())
            cursor.setPosition(cursor.selectionStart())
            cpt = 0
            nbSpacesRemoved = 0
            for i in range(nb_lines):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                indentation = self.getLineIndent()
                nbSpaces = indentation - (indentation - (indentation % size))
                if not nbSpaces:
                    nbSpaces = size
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
                if cursor.selectedText().startswith(" " * nbSpaces):
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    [cursor.deleteChar() for _ in range(nbSpaces)]
                    pos -= nbSpaces
                    nbSpacesRemoved += nbSpaces
                    if not i:
                        startOffset = nbSpaces
                    cpt += 1
                else:
                    cursor.clearSelection()
                # next line
                cursor.movePosition(QtGui.QTextCursor.EndOfLine)
                cursor.setPosition(cursor.position() + 1)
            if cpt:
                cursor.setPosition(sel_start - startOffset)
            else:
                cursor.setPosition(sel_start)
            if has_selection:
                cursor.setPosition(sel_end - nbSpacesRemoved,
                                   QtGui.QTextCursor.KeepAnchor)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
        else:
            self.keyPressEvent(
                QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Backtab,
                          QtCore.Qt.NoModifier))

    def refreshPanels(self):
        self.__resizePanels()
        self.__updateViewportMargins()
        self.update()

    def resizeEvent(self, e):
        """
        Resize event, lets the QPlainTextEdit handle the resize event than
        resizes the panels

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
        self.__updateVisibleBlocks(e)
        QtGui.QPlainTextEdit.paintEvent(self, e)
        self.painted.emit(e)

    def keyPressEvent(self, event):
        """
        Release the keyReleasedEvent. Use the accept method of the event
        instance to prevent the event to propagate.

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
        self.keyPressed.emit(event)
        if not event.isAccepted():
            event.setAccepted(initialState)
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
        self.postKeyPressed.emit(event)

    def keyReleaseEvent(self, event):
        """
        Release the keyReleasedEvent. Use the stop properties of the event
        instance to prevent the event to propagate.

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
        Emits the focusedIn signal
        :param event:
        :return:
        """
        self.focusedIn.emit(event)
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def mousePressEvent(self, event):
        """
        Emits mousePressed signal

        :param event: QMouseEvent
        """
        initialState = event.isAccepted()
        event.ignore()
        self.mousePressed.emit(event)
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
        Display any decoration tooltip and emits the mouseMoved event.
        """
        c = self.cursorForPosition(event.pos())
        for sel in self.__selections:
            if sel.containsCursor(c) and sel.tooltip:
                QtGui.QToolTip.showText(
                    self.mapToGlobal(event.pos()), sel.tooltip, self)
                break
        self.mouseMoved.emit(event)
        QtGui.QPlainTextEdit.mouseMoveEvent(self, event)

    def showEvent(self, QShowEvent):
        QtGui.QPlainTextEdit.showEvent(self, QShowEvent)
        self.__updateViewportMargins()

    def setPlainText(self, txt):
        """
        Overrides the setPlainText method to keep track of the original text.
        Emits the newTextSet event.

        :param txt: The new text to set.
        :return:
        """
        QtGui.QPlainTextEdit.setPlainText(self, txt)
        self.__originalText = txt
        self.__onSettingsChanged("", "", "")
        self.newTextSet.emit()

    def __initSettings(self):
        """
        Init the settings PropertyRegistry
        """
        self.settings = PropertyRegistry()
        self.settings.valueChanged.connect(self.__onSettingsChanged)
        self.settings.addProperty("showWhiteSpaces", True)
        self.settings.addProperty("tabLength", constants.TAB_SIZE)
        self.settings.addProperty("useSpacesInsteadOfTab", True)

    def __initStyle(self):
        """
        Init the style PropertyRegistry
        """
        self.style = PropertyRegistry()
        self.style.valueChanged.connect(self.__resetStyleSheet)
        self.style.addProperty("font", constants.FONT)
        self.style.addProperty("fontSize", constants.FONT_SIZE)
        self.style.addProperty("background", constants.EDITOR_BACKGROUND)
        self.style.addProperty("foreground", constants.EDITOR_FOREGROUND)
        self.style.addProperty("whiteSpaceForeground",
                               constants.EDITOR_WS_FOREGROUND)
        self.style.addProperty("selectionBackground",
                               constants.SELECTION_BACKGROUND)
        self.style.addProperty("selectionForeground",
                               constants.SELECTION_FOREGROUND)
        self.style.addProperty(
            "panelBackground", constants.LINE_NBR_BACKGROUND)
        self.style.addProperty(
            "panelForeground", constants.LINE_NBR_FOREGROUND)
        self.__resetStyleSheet("", "", "")

    def __encodePlainText(self, encoding):
        if sys.version_info[0] == 3:
            content = bytes(self.toPlainText().encode(encoding))
        else:
            content = unicode(self.toPlainText()).encode(encoding)
        return content

    def __updateVisibleBlocks(self, event):
        """
        Update the list of visible blocks/lines position.

        :param event: paint event
        """
        self.__blocks[:] = []
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid():
            if block.isVisible():
                self.__blocks.append((top, blockNumber+1))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()

    def __computePanelsSizes(self):
        # takes scrolll bar into account
        vscroll_width = 0
        if self.verticalScrollBar().isVisible():
            vscroll_width = self.verticalScrollBar().width()
        hscroll_height = 0
        if self.horizontalScrollBar().isVisible():
            hscroll_height = self.horizontalScrollBar().height()
        # Left panels
        left = 0
        for panel in self.__panels[PanelPosition.LEFT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            left += sh.width()
        # Right panels
        right = vscroll_width
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
        bottom = hscroll_height
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            bottom += sh.height()

        return bottom, left, right, top

    def __resizePanels(self):
        """
        Resizes panels geometries
        """
        cr = self.contentsRect()
        s_bottom, s_left, s_right, s_top = self.__computePanelsSizes()
        # takes scrolll bar into account
        vscroll_width = 0
        # if self.verticalScrollBar().isVisible():
        #     vscroll_width = self.verticalScrollBar().width()
        hscroll_height = 0
        # if self.horizontalScrollBar().isVisible():
        #     hscroll_height = self.horizontalScrollBar().height()
        left = 0
        for panel in self.__panels[PanelPosition.LEFT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left() + left, cr.top() + s_top,
                              sh.width(),
                              cr.height() - s_bottom - s_top)
            left += sh.width()
        right = vscroll_width
        for panel in self.__panels[PanelPosition.RIGHT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.right() - right - sh.width(),
                              cr.top(), sh.width(), cr.height())
            right += sh.width()
        top = 0
        for panel in self.__panels[PanelPosition.TOP].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(), cr.top() + top,
                              cr.width() - vscroll_width,
                              sh.height())
            top += sh.height()
        bottom = hscroll_height
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(),
                              cr.bottom() - bottom - sh.height(),
                              cr.width() - vscroll_width, sh.height())
            bottom += sh.height()

    def __updatePanels(self, rect, dy):
        """
        Updates the panel on update request. (Scroll, update clipping rect,...)
        """
        for zones_id, zone in self.__panels.items():
            if zones_id == PanelPosition.TOP or zones_id == PanelPosition.BOTTOM:
                continue
            for panel_id, panel in zone.items():
                if dy:
                    panel.scroll(0, dy)
                else:
                    panel.update(0, rect.y(), panel.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.__updateViewportMargins()

    def __ontextChanged(self):
        """
        Updates dirty flag on text changed.
        """
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
        self.setViewportMargins(left, top, right, bottom)

    def __resetStyleSheet(self, section, key, value):
        """ Resets stylesheet. """
        stylesheet = CODE_EDIT_STYLESHEET % {
            "background": self.style.value("background").name(),
            "foreground": self.style.value("foreground").name(),
            "selectionBackground": self.style.value(
                "selectionBackground").name(),
            "selectionForeground": self.style.value(
                "selectionForeground").name()}
        self.setStyleSheet(stylesheet)
        self.setFont(QtGui.QFont(self.style.value("font"),
                                      self.style.value("fontSize")))

    def __onSettingsChanged(self, section, key, value):
        self.setTabStopWidth(int(self.settings.value("tabLength")) *
                             self.fontMetrics().widthChar(" "))
        self.setShowWhitespaces(self.settings.value("showWhiteSpaces"))

    def __doHomeKey(self, event, select=False):
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
            event.accept()
