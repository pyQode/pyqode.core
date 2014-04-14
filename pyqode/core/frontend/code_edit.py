# -*- coding: utf-8 -*-
"""
This module contains the definition of the QCodeEdit
"""
import sys

from PyQt4 import QtGui, QtCore

from pyqode.core import logger, settings, style
from pyqode.core._internal import dialogs
from pyqode.core._internal.client import JsonTcpClient
from pyqode.core.frontend import text
from pyqode.core.frontend.extension import Panel
from pyqode.core.frontend.utils import DelayJobRunner


class QCodeEdit(QtGui.QPlainTextEdit):
    """
    Base class for any pyqode editor widget.

    Extends :py:class:`QPlainTextEdit` by adding an extension system (
    modes and panels), a rich property system for styles and settings
    (see :class:`pyqode.core.PropertyRegistry`) and by adding a series of
    additional signal and methods.

    **Signals:**
        - :attr:`pyqode.core.QCodeEdit.painted`
        - :attr:`pyqode.core.QCodeEdit.new_text_set`
        - :attr:`pyqode.core.QCodeEdit.painted`
        - :attr:`pyqode.core.QCodeEdit.text_saved`
        - :attr:`pyqode.core.QCodeEdit.text_saving`
        - :attr:`pyqode.core.QCodeEdit.dirty_changed`
        - :attr:`pyqode.core.QCodeEdit.key_pressed`
        - :attr:`pyqode.core.QCodeEdit.key_released`
        - :attr:`pyqode.core.QCodeEdit.mouse_pressed`
        - :attr:`pyqode.core.QCodeEdit.mouse_released`
        - :attr:`pyqode.core.QCodeEdit.mouse_wheel_activated`
        - :attr:`pyqode.core.QCodeEdit.post_key_pressed`
        - :attr:`pyqode.core.QCodeEdit.focused_in`
        - :attr:`pyqode.core.QCodeEdit.mouse_moved`
        - :attr:`pyqode.core.QCodeEdit.indent_requested`
        - :attr:`pyqode.core.QCodeEdit.unindent_requested`

    .. note:: QCodeEdit has been designed to work with files (
              :meth:`pyqode.core.QCodeEdit.openFile`,
              :meth:`pyqode.core.QCodeEdit.saveToFile`), not plain text.
              Well, you can still use some plain text but many modes and panels
              that rely heavily on the current file name/path won't work
              properly (e.g. the syntax highlighter mode uses the file name
              extension to automatically adapt the lexer so you will need to do
              it manually depending on the nature of the text/code to edit).
    """
    #: Paint hook
    painted = QtCore.pyqtSignal(QtGui.QPaintEvent)
    #: Signal emitted when a new text is set on the widget
    new_text_set = QtCore.pyqtSignal()
    #: Signal emitted when the text is saved to file
    text_saved = QtCore.pyqtSignal(str)
    #: Signal emitted before the text is saved to file
    text_saving = QtCore.pyqtSignal(str)
    #: Signal emitted when the dirty state changed
    dirty_changed = QtCore.pyqtSignal(bool)
    #: Signal emitted when a key is pressed
    key_pressed = QtCore.pyqtSignal(QtGui.QKeyEvent)
    #: Signal emitted when a key is released
    key_released = QtCore.pyqtSignal(QtGui.QKeyEvent)
    #: Signal emitted when a mouse button is pressed
    mouse_pressed = QtCore.pyqtSignal(QtGui.QMouseEvent)
    #: Signal emitted when a mouse button is released
    mouse_released = QtCore.pyqtSignal(QtGui.QMouseEvent)
    #: Signal emitted on a wheel event
    mouse_wheel_activated = QtCore.pyqtSignal(QtGui.QWheelEvent)
    #: Signal emitted at the end of the key_pressed event
    post_key_pressed = QtCore.pyqtSignal(QtGui.QKeyEvent)
    #: Signal emitted when focusInEvent is is called
    focused_in = QtCore.pyqtSignal(QtGui.QFocusEvent)
    #: Signal emitted when the mouse_moved
    mouse_moved = QtCore.pyqtSignal(QtGui.QMouseEvent)
    #: Signal emitted when the user press the TAB key
    indent_requested = QtCore.pyqtSignal()
    #: Signal emitted when the user press the BACK-TAB (Shift+TAB) key
    unindent_requested = QtCore.pyqtSignal()

    @property
    def show_whitespaces(self):
        """
        Shows/Hides white spaces highlighting.
        """
        return self._show_whitespaces

    @show_whitespaces.setter
    def show_whitespaces(self, value):
        self._show_whitespaces = value
        self._set_whitespaces_flags(value)

    @property
    def save_on_focus_out(self):
        """
        Enables auto save on focus out.
        """
        return self._save_on_focus_out

    @save_on_focus_out.setter
    def save_on_focus_out(self, value):
        self._save_on_focus_out = value

    @property
    def font_name(self):
        """
        The editor font.
        """
        return self._font_family

    @font_name.setter
    def font_name(self, value):
        self._font_family = value
        self._reset_palette()

    @property
    def font_size(self):
        """
        The editor font size.
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self._reset_palette()

    @property
    def background(self):
        """
        The editor background color.
        """
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._reset_palette()

    @property
    def foreground(self):
        """
        The editor foreground color.
        """
        return self._foreground

    @foreground.setter
    def foreground(self, value):
        self._foreground = value
        self._reset_palette()

    @property
    def whitespaces_foreground(self):
        """
        The editor white spaces' foreground color.
        """
        return self._whitespaces_foreground

    @whitespaces_foreground.setter
    def whitespaces_foreground(self, value):
        self._whitespaces_foreground = value
        # highlighted by syntax highlighter
        self.rehighlight()

    @property
    def selection_background(self):
        """
        The editor selection's background color.
        """
        return self._sel_background

    @selection_background.setter
    def selection_background(self, value):
        self._sel_background = value
        self._reset_palette()

    @property
    def selection_foreground(self):
        """
        The editor selection's foreground color.
        """
        return self._sel_foreground

    @selection_foreground.setter
    def selection_foreground(self, value):
        self._sel_foreground = value
        self.rehighlight()

    @property
    def dirty(self):
        """
        Gets/sets the dirty flag.

        :type: bool
        """
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        if self._dirty != value:
            self._dirty = value
            self.dirty_changed.emit(value)

    @property
    def file_name(self):
        """
        Returns the file name (see :meth:`QtCore.QFileInfo.fileName`)

        :rtype: str
        """
        return QtCore.QFileInfo(self.file_path).fileName()

    @property
    def file_path(self):
        """
        Gets/Sets the current file path. This property is used by many modes to
        work properly. It is automatically set by the
        :meth:`pyqode.core.QCodeEdit.openFile` and
        :meth:`pyqode.core.QCodeEdit.saveToFile` methods.

        If you need to work with plain text, be sure to adapt file path
        accordingly (the extension is enough)

        :type: str
        """
        return self._fpath

    @file_path.setter
    def file_path(self, value):
        self._fpath = value

    @property
    def file_encoding(self):
        """
        Returns last encoding used to open the file

        :rtype: str
        """
        return self._fencoding

    @property
    def visible_blocks(self):
        """
        Returns the list of visible blocks.

        Each element in the list is a tuple made up of the line top position,
        the line number (already 1 based), and the QTextBlock itself.

        :return: A list of tuple(top_position, line_number, block)
        :rtype: List of tuple(int, int, QtGui.QTextBlock)
        """
        return self._visible_blocks

    @property
    def mime_type(self):
        return self._mime_type

    def __init__(self, parent=None, create_default_actions=True):
        """
        :param parent: Parent widget

        :param create_default_actions: Specify if the default actions (copy,
                                     paste, ...) must be created.
                                     Default is True.
        """
        QtGui.QPlainTextEdit.__init__(self, parent)
        self._client = JsonTcpClient(self)
        self._last_mouse_pos = None
        self._cached_cursor_pos = (-1, -1)
        self._modified_lines = set()
        self._cleaning = False
        self._margin_sizes = (0, 0, 0, 0)
        self.top = self.left = self.right = self.bottom = -1
        self._visible_blocks = []
        self._extra_selections = []
        self._parenthesis_selections = []
        self._tooltips_runner = DelayJobRunner(
            self, nb_threads_max=1, delay=700)
        self._prev_tooltip_block_nbr = -1
        self._fpath = None
        self._fencoding = None
        self._mime_type = None
        self._original_text = ""
        self._modes = {}
        self._panels = {Panel.Position.TOP: {},
                        Panel.Position.LEFT: {},
                        Panel.Position.RIGHT: {},
                        Panel.Position.BOTTOM: {}}
        self._dirty = False

        # setup context menu
        self._actions = []
        if create_default_actions:
            self._create_default_actions()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._mnu = None  # bug with PySide (github #63)

        # init settings and styles from global settings/style modules
        self._init_settings()
        self._init_style()

        # connect slots
        self.blockCountChanged.connect(self._update_viewport_margins)
        self.textChanged.connect(self._on_text_changed)
        self.updateRequest.connect(self._update_panels)
        self.blockCountChanged.connect(self.update)
        self.cursorPositionChanged.connect(self.update)
        self.selectionChanged.connect(self.update)

        self.setMouseTracking(True)
        self.setCenterOnScroll(True)

    # Utility methods
    # ---------------
    def set_mouse_cursor(self, cursor):
        """
        Changes the viewport cursor

        :param cursor: the nex mouse cursor to set.
        :type cursor: QtGui.QCursor
        """
        self.viewport().setCursor(cursor)
        QtGui.QApplication.processEvents()

    def show_tooltip(self, pos, tooltip):
        """
        Show a tool tip at the specified position

        :param pos: Tooltip position

        :param tooltip: Tooltip text
        """
        QtGui.QToolTip.showText(pos, tooltip[0: 1024], self)
        self._prev_tooltip_block_nbr = -1

    def margin_size(self, position=Panel.Position.LEFT):
        """
        Gets the size of a specific margin.

        :param position: Margin position. See
            :class:`pyqode.core.Panel.Position`

        :return: The size of the specified margin
        :rtype: float
        """
        return self._margin_sizes[position]

    def setPlainText(self, txt, mime_type, encoding):
        """
        Extends setPlainText to force the user to set an encoding and a
        mime type.

        Emits the new_text_set signal.

        :param txt: The new text to set.
        """
        self._fencoding = encoding
        self._mime_type = mime_type
        QtGui.QPlainTextEdit.setPlainText(self, txt)
        self._original_text = txt
        self._modified_lines.clear()
        self.new_text_set.emit()
        self.redoAvailable.emit(False)
        self.undoAvailable.emit(False)
        self.dirty = False
        for mode in self._modes.values():
            if hasattr(mode, 'set_mime_type'):
                mode.set_mime_type(self.mime_type)

    def add_action(self, action):
        """
        Adds an action to the editor's context menu.

        :param action: QtGui.QAction
        """
        self._actions.append(action)
        QtGui.QPlainTextEdit.addAction(self, action)

    def actions(self):
        """
        Returns the list of actions/seprators of the context menu.
        :return:
        """
        return self._actions

    def add_separator(self):
        """
        Adds a seprator to the editor's context menu.

        :return: The sepator that has been added.
        :rtype: QtGui.QAction
        """
        action = QtGui.QAction(self)
        action.setSeparator(True)
        self._actions.append(action)
        return action

    def remove_action(self, action):
        """
        Removes an action/separator from the editor's context menu.

        :param action: Action/seprator to remove.
        """
        self._actions.remove(action)

    def refresh_icons(self, use_theme=True):
        for action in self._actions:
            if action.text() in settings.actions:
                icon, theme = style.icons[action.text()]
                if use_theme:
                    action.setIcon(QtGui.QIcon.fromTheme(
                        theme, QtGui.QIcon(icon)))
                else:
                    action.setIcon(QtGui.QIcon(icon))
        try:
            self.searchAndReplacePanel.refresh_icons(use_theme=use_theme)
        except AttributeError:
            pass  # panel not installed

    def refresh_settings(self,):
        """
        Refresh all settings, every installed mode/panel will be refreshed too.

        """
        self._init_settings()
        for m in self._modes.values():
            m.refresh_settings()
        for zone in self._panels.values():
            for panel in zone.values():
                panel.refresh_settings()

    def refresh_style(self):
        """
        Refreshes the editor style, every installed mode/panel will be
        refreshed too.

        """
        self._init_style()
        for m in self._modes.values():
            m.refresh_style()
        for zone in self._panels.values():
            for panel in zone.values():
                panel.refresh_style()

    # Public slots
    # ------------
    @QtCore.pyqtSlot()
    def delete(self):
        """ Deletes the selected text """
        self.textCursor().removeSelectedText()

    @QtCore.pyqtSlot()
    def goto_line(self):
        """
        Shows goto line dialog and go to the selected line.
        """
        line, result = dialogs.GoToLineDialog.get_line(
            self, text.current_line_nbr(self), text.line_count(self))
        if not result:
            return
        if not line:
            line = 1
        return text.goto_line(self, line, move=True)

    @QtCore.pyqtSlot()
    def rehighlight(self):
        """
        Convenience method that calls rehighlight on the syntax highlighter
        mode.

        """
        for mode in self._modes.values():
            if hasattr(mode, 'rehighlight'):
                mode.rehighlight()

    @QtCore.pyqtSlot()
    def reset_zoom(self):
        """
        Resets the zoom value.
        """
        self._font_size = style.font_size
        self._reset_palette()

    @QtCore.pyqtSlot()
    def zoom_in(self, increment=1):
        """
        Zooms in the editor.

        The effect is achieved by increasing the editor font size by the
        increment value.

        Panels that needs to be resized depending on the font size need to
        implement onStyleChanged.
        """
        self._font_size += increment
        text.mark_whole_doc_dirty(self)
        self._reset_palette()

    @QtCore.pyqtSlot()
    def zoom_out(self, increment=1):
        """
        Zooms out the editor.

        The effect is achieved by decreasing the editor font size by the
        increment value.

        Panels that needs to be resized depending on the font size need to
        implement onStyleChanged and trigger an update.
        """
        self._font_size -= increment
        if self._font_size <= 0:
            self._font_size = increment
        text.mark_whole_doc_dirty(self)
        self._reset_palette()

    @QtCore.pyqtSlot()
    def duplicate_line(self):
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
        self._do_home_key()

    @QtCore.pyqtSlot()
    def indent(self):
        """
        Indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.QCodeEdit.indent_requested` signal, the
        :class:`pyqode.core.IndenterMode` will perform the actual indentation.
        """
        self.indent_requested.emit()

    @QtCore.pyqtSlot()
    def un_indent(self):
        """
        Un-indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.QCodeEdit.unindent_requested` signal, the
        :class:`pyqode.core.IndenterMode` will perform the actual
        un-indentation.
        """
        self.unindent_requested.emit()

    @QtCore.pyqtSlot()
    def refresh_panels(self):
        """ Refreshes the editor panels. """
        self._resize_panels()
        self._update_viewport_margins()
        self._update_panels(self.contentsRect(), 0)
        self.update()

    # Events
    # ------
    def resizeEvent(self, e):
        """
        Overrides resize event to resize the editor's panels.

        :param e: resize event
        """
        QtGui.QPlainTextEdit.resizeEvent(self, e)
        self._resize_panels()

    def paintEvent(self, e):
        """
        Overrides paint event to update the list of visible blocks and emit
        the painted event.

        :param e: paint event
        """
        self._update_visible_blocks(e)
        QtGui.QPlainTextEdit.paintEvent(self, e)
        self.painted.emit(e)

    def keyPressEvent(self, event):
        """
        Overrides the keyPressEvent to emit the key_pressed signal.

        Also takes care of indenting and handling smarter home key.

        :param event: QKeyEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        replace = self._use_spaces_instead_of_tabs
        if replace and event.key() == QtCore.Qt.Key_Tab:
            self.indent()
            event.accept()
        elif replace and event.key() == QtCore.Qt.Key_Backtab:
            self.un_indent()
            event.accept()
        elif event.key() == QtCore.Qt.Key_Home:
            self._do_home_key(
                event, int(event.modifiers()) & QtCore.Qt.ShiftModifier)
        elif (event.key() == QtCore.Qt.Key_D and
              event.modifiers() & QtCore.Qt.ControlModifier):
            self.duplicate_line()
            event.accept()
        self.key_pressed.emit(event)
        state = event.isAccepted()
        if not event.isAccepted():
            event.setAccepted(initial_state)
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
        event.setAccepted(state)
        self.post_key_pressed.emit(event)

    def keyReleaseEvent(self, event):
        """
        Overrides keyReleaseEvent to emit the key_released signal.

        :param event: QKeyEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.key_released.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            QtGui.QPlainTextEdit.keyReleaseEvent(self, event)

    def focusInEvent(self, event):
        """
        Overrides focusInEvent to emits the focused_in signal

        :param event: QFocusEvent
        """
        self.focused_in.emit(event)
        QtGui.QPlainTextEdit.focusInEvent(self, event)
        self.repaint()
        QtGui.QApplication.processEvents()

    def focusOutEvent(self, event):
        if self._save_on_focus_out:
            QtCore.QTimer.singleShot(500, self._save)

    def mousePressEvent(self, event):
        """
        Overrides mousePressEvent to emits mouse_pressed signal

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_pressed.emit(event)
        c = self.cursorForPosition(event.pos())
        for sel in self._extra_selections:
            if sel.cursor.blockNumber() == c.blockNumber():
                sel.signals.clicked.emit(sel)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            QtGui.QPlainTextEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Emits mouse_released signal.

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_released.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            QtGui.QPlainTextEdit.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        """
        Emits the mouse_wheel_activated signal.

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_wheel_activated.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            QtGui.QPlainTextEdit.wheelEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouseMovedEvent to display any decoration tooltip and emits
        the mouse_moved event.
        """
        c = self.cursorForPosition(event.pos())
        self._last_mouse_pos = event.pos()
        block_found = False
        for sel in self._extra_selections:
            if sel.cursor.blockNumber() == c.blockNumber() and sel.tooltip:
                if self._prev_tooltip_block_nbr != c.blockNumber():
                    self._tooltips_runner.request_job(
                        self.show_tooltip, False,
                        self.mapToGlobal(event.pos()), sel.tooltip[0: 1024])
                self._prev_tooltip_block_nbr = c.blockNumber()
                block_found = True
                break
        if not block_found:
            if self._prev_tooltip_block_nbr != -1:
                QtGui.QToolTip.hideText()
            self._prev_tooltip_block_nbr = -1
            self._tooltips_runner.cancel_requests()
        self.mouse_moved.emit(event)
        QtGui.QPlainTextEdit.mouseMoveEvent(self, event)

    def showEvent(self, event):
        """ Overrides showEvent to update the viewport margins """
        QtGui.QPlainTextEdit.showEvent(self, event)
        self._update_viewport_margins()

    # Private methods
    # ---------------
    def _show_context_menu(self, pt):
        self._mnu = QtGui.QMenu()
        self._mnu.addActions(self._actions)
        self._mnu.popup(self.mapToGlobal(pt))

    def _set_whitespaces_flags(self, show):
        doc = self.document()
        options = doc.defaultTextOption()
        if show:
            options.setFlags(options.flags() |
                             QtGui.QTextOption.ShowTabsAndSpaces)
        else:
            options.setFlags(options.flags() &
                             ~QtGui.QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(options)

    def _create_default_actions(self):
        values = [
            ("Undo", self.undo, self.undoAvailable),
            ("Redo", self.redo, self.redoAvailable),
            None,
            ("Copy", self.copy, self.copyAvailable),
            ("Cut", self.cut, self.copyAvailable),
            ("Paste", self.paste, None),
            ("Delete", self.delete, None),
            ("Select all", self.selectAll, None),
            ("Indent", self.indent, None),
            ("Un-indent", self.un_indent, None),
            ("Go to line", self.goto_line, None)
        ]

        for val in values:
            if val:
                name, trig_slot, enable_signal = val
                shortcut = settings.actions[name]
                icon, theme = style.icons[name]
                a = QtGui.QAction(QtGui.QIcon.fromTheme(
                    theme, QtGui.QIcon(icon)), name, self)
                a.setShortcut(shortcut)
                a.setIconVisibleInMenu(True)
                a.triggered.connect(trig_slot)
                if enable_signal:
                    enable_signal.connect(a.setEnabled)
                self.add_action(a)
            else:
                self.add_separator()

    def _init_settings(self):
        self._show_whitespaces = settings.show_white_spaces
        self._tab_length = settings.tab_length
        self._use_spaces_instead_of_tabs = settings.use_spaces_instead_of_tabs
        self._save_on_focus_out = settings.save_on_focus_out
        self.setTabStopWidth(self._tab_length *
                             self.fontMetrics().widthChar(" "))
        self._set_whitespaces_flags(self._show_whitespaces)

    def _init_style(self):
        if style.font is None:
            self._font_family = "monospace"
            if sys.platform == "win32":
                self._font_family = "Consolas"
            elif sys.platform == "darwin":
                self._font_family = 'Monaco'
        else:
            self._font_family = style.font
        self._font_size = style.font_size
        self._background = style.background
        self._foreground = style.foreground
        self._whitespaces_foreground = style.whitespaces_foreground
        if style.selection_background is None:
            self._sel_background = self.palette().highlight().color()
        else:
            self._sel_background = style.selection_background
        if style.selection_foreground is None:
            self._sel_foreground = self.palette().highlightedText().color()
        else:
            self._sel_foreground = style.selection_foreground
        self._reset_palette()

    def _update_visible_blocks(self, event):
        self._visible_blocks[:] = []
        block = self.firstVisibleBlock()
        block_nbr = block.blockNumber()
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
                self._visible_blocks.append((top, block_nbr + 1, block))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_nbr = block.blockNumber()

    def _compute_zones_sizes(self):
        # Left panels
        left = 0
        for panel in self._panels[Panel.Position.LEFT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            left += sh.width()
        # Right panels
        right = 0
        for panel in self._panels[Panel.Position.RIGHT].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            right += sh.width()
        # Top panels
        top = 0
        for panel in self._panels[Panel.Position.TOP].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            top += sh.height()
        # Bottom panels
        bottom = 0
        for panel in self._panels[Panel.Position.BOTTOM].values():
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            bottom += sh.height()
        self.top, self.left, self.right, self.bottom = top, left, right, bottom
        return bottom, left, right, top

    def _resize_panels(self):
        cr = self.contentsRect()
        vcr = self.viewport().contentsRect()
        s_bottom, s_left, s_right, s_top = self._compute_zones_sizes()
        w_offset = cr.width() - (vcr.width() + s_left + s_right)
        h_offset = cr.height() - (vcr.height() + s_bottom + s_top)
        left = 0
        panels = list(self._panels[Panel.Position.LEFT].values())
        panels.sort(key=lambda panel: panel.order_in_zone, reverse=True)
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
        panels = list(self._panels[Panel.Position.RIGHT].values())
        panels.sort(key=lambda panel: panel.order_in_zone, reverse=True)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.right() - right - sh.width() - w_offset,
                              cr.top(), sh.width(), cr.height() - h_offset)
            right += sh.width()
        top = 0
        panels = list(self._panels[Panel.Position.TOP].values())
        panels.sort(key=lambda panel: panel.order_in_zone)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(), cr.top() + top,
                              cr.width() - w_offset,
                              sh.height())
            top += sh.height()
        bottom = 0
        panels = list(self._panels[Panel.Position.BOTTOM].values())
        panels.sort(key=lambda panel: panel.order_in_zone)
        for panel in panels:
            if not panel.isVisible():
                continue
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(),
                              cr.bottom() - bottom - sh.height() - h_offset,
                              cr.width() - w_offset, sh.height())
            bottom += sh.height()

    def _update_panels(self, rect, dy):
        for zones_id, zone in self._panels.items():
            if zones_id == Panel.Position.TOP or \
               zones_id == Panel.Position.BOTTOM:
                continue
            panels = list(zone.values())
            for panel in panels:
                if not panel.scrollable:
                    continue
                if dy:
                    panel.scroll(0, dy)
                else:
                    l, c = text.cursor_position(self)
                    ol, oc = self._cached_cursor_pos
                    if l != ol or c != oc:
                        panel.update(0, rect.y(), panel.width(), rect.height())
                    self._cached_cursor_pos = text.cursor_position(self)
        if rect.contains(self.viewport().rect()):
            self._update_viewport_margins()

    def _on_text_changed(self):
        if not self._cleaning:
            self._modified_lines.add(text.cursor_position(self)[0])
            txt = self.toPlainText()
            self.dirty = (txt != self._original_text)

    def _update_viewport_margins(self):
        top = 0
        left = 0
        right = 0
        bottom = 0
        for panel in self._panels[Panel.Position.LEFT].values():
            if panel.isVisible():
                left += panel.sizeHint().width()
        for panel in self._panels[Panel.Position.RIGHT].values():
            if panel.isVisible():
                right += panel.sizeHint().width()
        for panel in self._panels[Panel.Position.TOP].values():
            if panel.isVisible():
                top += panel.sizeHint().height()
        for panel in self._panels[Panel.Position.BOTTOM].values():
            if panel.isVisible():
                bottom += panel.sizeHint().height()
        self._margin_sizes = (top, left, right, bottom)
        self.setViewportMargins(left, top, right, bottom)

    def _reset_palette(self):
        self.setFont(QtGui.QFont(self._font_family, self._font_size))
        p = self.palette()
        p.setColor(p.Base, self._background)
        p.setColor(p.Text, self._foreground)
        p.setColor(QtGui.QPalette.Highlight, self._sel_background)
        p.setColor(QtGui.QPalette.HighlightedText, self._sel_foreground)
        self.setPalette(p)

    def _do_home_key(self, event=None, select=False):
        # get nb char to first significative char
        delta = self.textCursor().positionInBlock() - text.line_indent(self)
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

    def _save(self):
        text.save_to_file(self)
