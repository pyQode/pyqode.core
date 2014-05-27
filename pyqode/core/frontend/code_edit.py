# -*- coding: utf-8 -*-
"""
This module contains the definition of the CodeEdit
"""
import logging
import sys
from pyqode.qt import QtWidgets, QtCore, QtGui
from pyqode.core.frontend import text, dialogs
from pyqode.core.frontend.client import JsonTcpClient
from pyqode.core.frontend.extension import Panel
from pyqode.core.frontend.utils import DelayJobRunner


def _logger():
    """ Gets module logger """
    return logging.getLogger(__name__)


class CodeEdit(QtWidgets.QPlainTextEdit):
    """
    Base class for any pyqode source code editor widget.

    Extends :class:`PyQt5.GtGui.QPlainTextEdit` by adding an extension system (
    modes and panels) and by adding a series of additional signal and methods.

    To interact with the editor content, you may use the Qt Text API (
    QTextCursor, ...) or use the more high level functions defined in
    :mod:`pyqode.core.frontend.text`

    .. note:: setPlainText has been overriden to force you to define
        a mime type and an encoding.

    """
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    #: Paint hook
    painted = QtCore.Signal(QtGui.QPaintEvent)
    #: Signal emitted when a new text is set on the widget
    new_text_set = QtCore.Signal()
    #: Signal emitted when the text is saved to file
    text_saved = QtCore.Signal(str)
    #: Signal emitted before the text is saved to file
    text_saving = QtCore.Signal(str)
    #: Signal emitted when the dirty state changed
    dirty_changed = QtCore.Signal(bool)
    #: Signal emitted when a key is pressed
    key_pressed = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when a key is released
    key_released = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when a mouse button is pressed
    mouse_pressed = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted when a mouse button is released
    mouse_released = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted on a wheel event
    mouse_wheel_activated = QtCore.Signal(QtGui.QWheelEvent)
    #: Signal emitted at the end of the key_pressed event
    post_key_pressed = QtCore.Signal(QtGui.QKeyEvent)
    #: Signal emitted when focusInEvent is is called
    focused_in = QtCore.Signal(QtGui.QFocusEvent)
    #: Signal emitted when the mouse_moved
    mouse_moved = QtCore.Signal(QtGui.QMouseEvent)
    #: Signal emitted when the user press the TAB key
    indent_requested = QtCore.Signal()
    #: Signal emitted when the user press the BACK-TAB (Shift+TAB) key
    unindent_requested = QtCore.Signal()

    @property
    def use_spaces_instead_of_tabs(self):
        return self._use_spaces_instead_of_tabs

    @use_spaces_instead_of_tabs.setter
    def use_spaces_instead_of_tabs(self, value):
        self._use_spaces_instead_of_tabs = value

    @property
    def tab_length(self):
        return self._tab_length

    @tab_length.setter
    def tab_length(self, value):
        self._tab_length = value

    @property
    def min_indent_column(self):
        return self._min_indent_column

    @min_indent_column.setter
    def min_indent_column(self, value):
        self._min_indent_column = value

    @property
    def save_on_focus_out(self):
        return self._save_on_focus_out

    @save_on_focus_out.setter
    def save_on_focus_out(self, value):
        self._save_on_focus_out = value

    @property
    def show_whitespaces(self):
        """
        Shows/Hides white spaces highlighting.
        """
        return self._show_whitespaces

    @show_whitespaces.setter
    def show_whitespaces(self, value):  # pylint: disable=missing-docstring
        self._show_whitespaces = value
        self._set_whitespaces_flags(value)

    @property
    def font_name(self):
        """
        The editor font family name.
        """
        return self._font_family

    @font_name.setter
    def font_name(self, value):  # pylint: disable=missing-docstring
        self._font_family = value
        if not self._font_family:
            self._font_family = "monospace"
            if sys.platform == "win32":
                self._font_family = "Consolas"
            elif sys.platform == "darwin":
                self._font_family = 'Monaco'
        self._reset_palette()

    @property
    def font_size(self):
        """
        The editor font size.
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):  # pylint: disable=missing-docstring
        self._font_size = value
        self._reset_palette()

    @property
    def background(self):
        """
        The editor background color.
        """
        return self._background

    @background.setter
    def background(self, value):  # pylint: disable=missing-docstring
        self._background = value
        self._reset_palette()

    @property
    def foreground(self):
        """
        The editor foreground color.
        """
        return self._foreground

    @foreground.setter
    def foreground(self, value):  # pylint: disable=missing-docstring
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
        # pylint: disable=missing-docstring
        self._whitespaces_foreground = value
        self.rehighlight()

    @property
    def selection_background(self):
        """
        The editor selection's background color.
        """
        return self._sel_background

    @selection_background.setter
    def selection_background(self, value):  # pylint: disable=missing-docstring
        self._sel_background = value
        self._reset_palette()

    @property
    def selection_foreground(self):
        """
        The editor selection's foreground color.
        """
        return self._sel_foreground

    @selection_foreground.setter
    def selection_foreground(self, value):  # pylint: disable=missing-docstring
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
    def dirty(self, value):  # pylint: disable=missing-docstring
        if self._dirty != value:
            self._dirty = value
            self.dirty_changed.emit(value)

    @property
    def file_name(self):
        """
        Returns the open file name (see :meth:`QtCore.QFileInfo.fileName`)

        :rtype: str
        """
        return QtCore.QFileInfo(self.file_path).fileName()

    @property
    def file_path(self):
        """
        Gets/Sets the current file path.

        This property is used by many modes to work properly. It is
        automatically set by the :meth:`pyqode.core.frontend.open_file` and
        :meth:`pyqode.core.frontend.save_to_file` methods.

        :type: str
        """
        return self._fpath

    @file_path.setter
    def file_path(self, value):  # pylint: disable=missing-docstring
        self._fpath = value

    @property
    def file_encoding(self):
        """
        Returns the last encoding used to open/save the file.

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
        :rtype: List of tuple(int, int, QtWidgets.QTextBlock)
        """
        return self._visible_blocks

    @property
    def mime_type(self):
        """
        Gets the associated mime type.
        """
        return self._mime_type

    def __init__(self, parent=None, create_default_actions=True):
        """
        :param parent: Parent widget
        :param create_default_actions: Specify if the default actions (copy,
            paste, ...) must be created or not. Default is True.
        """
        super().__init__(parent)
        #: List of word separators
        self.word_separators = [
            '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{',
            '}', '|', ':', '"', "'", "<", ">", "?", ",", ".", "/", ";", '[',
            ']', '\\', '\n', '\t', '=', '-', ' '
        ]
        self._min_indent_column = 0
        self._save_on_focus_out = True
        self._use_spaces_instead_of_tabs = True
        self._whitespaces_foreground = None
        self._sel_background = None
        self._show_whitespaces = False
        self._foreground = None
        self._sel_foreground = None
        self._tab_length = 4
        self._font_size = 10
        self._background = None
        self._font_family = 'monospace'
        self._client = JsonTcpClient(self)
        self._last_mouse_pos = QtCore.QPoint(0, 0)
        self._cached_cursor_pos = (-1, -1)
        self._modified_lines = set()
        self._cleaning = False
        self._margin_sizes = (0, 0, 0, 0)
        self._top = self._left = self._right = self._bottom = -1
        self._visible_blocks = []
        self._extra_selections = []
        self._parenthesis_selections = []
        self._tooltips_runner = DelayJobRunner(delay=700)
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
            self._init_actions()
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
        self.setLineWrapMode(self.NoWrap)

    def __del__(self):
        try:
            self.blockCountChanged.disconnect(self._update_viewport_margins)
            self.textChanged.disconnect(self._on_text_changed)
            self.updateRequest.disconnect(self._update_panels)
            self.blockCountChanged.disconnect(self.update)
            self.cursorPositionChanged.disconnect(self.update)
            self.selectionChanged.disconnect(self.update)
        except TypeError:
            pass

    # Utility methods
    # ---------------
    def set_mouse_cursor(self, cursor):
        """
        Changes the viewport's cursor

        :param cursor: the mouse cursor to set.
        :type cursor: QtWidgets.QCursor
        """
        self.viewport().setCursor(cursor)
        QtWidgets.QApplication.processEvents()

    def show_tooltip(self, pos, tooltip):
        """
        Show a tool tip at the specified position

        :param pos: Tooltip position
        :param tooltip: Tooltip text
        """
        QtWidgets.QToolTip.showText(pos, tooltip[0: 1024], self)
        self._prev_tooltip_block_nbr = -1

    def margin_size(self, position=Panel.Position.LEFT):
        """
        Gets the size of a specific margin.

        :param position: Margin position. See
            :class:`pyqode.core.frontend.Panel.Position`
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
        # pylint: disable=invalid-name
        self._fencoding = encoding
        self._mime_type = mime_type
        self.clear()
        highlighter = None
        for mode in self._modes.values():
            if hasattr(mode, 'set_mime_type'):
                highlighter = mode
                try:
                    _logger().debug('setting up lexer from mimetype: %s',
                                    self.mime_type)
                    mode.set_mime_type(self.mime_type)
                except ValueError:
                    _logger().exception(
                        'Failed to set lexer from mimetype: %s',
                        self.mime_type)
                    _logger().debug('setting up lexer from file path: %s',
                                    self.file_path)
                    mode.set_lexer_from_filename(self.file_path)
                break
        self._original_text = txt
        self._modified_lines.clear()
        if highlighter:
            highlighter.process_events_on_highlight = True
        super().setPlainText(txt)
        if highlighter:
            highlighter.process_events_on_highlight = False
        self.new_text_set.emit()
        self.redoAvailable.emit(False)
        self.undoAvailable.emit(False)
        self.dirty = False

    def add_action(self, action):
        """
        Adds an action to the editor's context menu.

        :param action: QtWidgets.QAction
        """
        self._actions.append(action)
        super().addAction(action)

    def actions(self):
        """
        Returns the list of actions/sepqrators of the context menu.

        """
        return self._actions

    def add_separator(self):
        """
        Adds a sepqrator to the editor's context menu.

        :return: The sepator that has been added.
        :rtype: QtWidgets.QAction
        """
        action = QtWidgets.QAction(self)
        action.setSeparator(True)
        self._actions.append(action)
        return action

    def remove_action(self, action):
        """
        Removes an action/separator from the editor's context menu.

        :param action: Action/seprator to remove.
        """
        self._actions.remove(action)

    @QtCore.Slot()
    def delete(self):
        """ Deletes the selected text """
        self.textCursor().removeSelectedText()

    @QtCore.Slot()
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

    @QtCore.Slot()
    def rehighlight(self):
        """
        Convenience method that calls rehighlight on the instqlled
        syntax highlighter mode.
        """
        for mode in self._modes.values():
            if hasattr(mode, 'rehighlight'):
                mode.rehighlight()

    @QtCore.Slot()
    def reset_zoom(self):
        """
        Resets the zoom value.
        """
        self._font_size = 10
        self._reset_palette()

    @QtCore.Slot()
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

    @QtCore.Slot()
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

    @QtCore.Slot()
    def duplicate_line(self):
        """
        Duplicates the line under the cursor. If multiple lines are selected,
        only the last one is duplicated.
        """
        cursor = self.textCursor()
        cursor.select(cursor.LineUnderCursor)
        line = cursor.selectedText()
        cursor.movePosition(cursor.Down, cursor.MoveAnchor)
        cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
        cursor.insertText(line + "\n")
        cursor.movePosition(cursor.Left, cursor.MoveAnchor)
        self.setTextCursor(cursor)
        self._do_home_key()

    @QtCore.Slot()
    def indent(self):
        """
        Indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.frontend.CodeEdit.indent_requested`
        signal, the :class:`pyqode.core.frontend.modes.IndenterMode` will
        perform the actual indentation.
        """
        self.indent_requested.emit()

    @QtCore.Slot()
    def un_indent(self):
        """
        Un-indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.frontend.CodeEdit.unindent_requested`
        signal, the :class:`pyqode.core.frontend.modes.IndenterMode` will
        perform the actual un-indentation.
        """
        self.unindent_requested.emit()

    @QtCore.Slot()
    def refresh_panels(self):
        """ Refreshes the editor panels. """
        _logger().debug('refresh_panels')
        self._resize_panels()
        self._update_panels(self.contentsRect(), 0, force_update_margins=True)

    def resizeEvent(self, e):  # pylint: disable=invalid-name
        """
        Overrides resize event to resize the editor's panels.

        :param e: resize event
        """
        super().resizeEvent(e)
        self._resize_panels()

    def paintEvent(self, e):  # pylint: disable=invalid-name
        """
        Overrides paint event to update the list of visible blocks and emit
        the painted event.

        :param e: paint event
        """
        self._update_visible_blocks(e)
        super().paintEvent(e)
        self.painted.emit(e)

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides the keyPressEvent to emit the key_pressed signal.

        Also takes care of indenting and handling smarter home key.

        :param event: QKeyEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.key_pressed.emit(event)
        state = event.isAccepted()
        if not event.isAccepted():
            if event.key() == QtCore.Qt.Key_Tab:
                self.indent()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Backtab:
                self.un_indent()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Home:
                self._do_home_key(
                    event, int(event.modifiers()) & QtCore.Qt.ShiftModifier)
            if not event.isAccepted():
                event.setAccepted(initial_state)
                super().keyPressEvent(event)
        new_state = event.isAccepted()
        event.setAccepted(state)
        self.post_key_pressed.emit(event)
        event.setAccepted(new_state)

    def keyReleaseEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides keyReleaseEvent to emit the key_released signal.

        :param event: QKeyEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.key_released.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            super().keyReleaseEvent(event)

    def focusInEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides focusInEvent to emits the focused_in signal

        :param event: QFocusEvent
        """
        self.focused_in.emit(event)
        super().focusInEvent(event)
        self.repaint()
        QtWidgets.QApplication.processEvents()

    def focusOutEvent(self, event):  # pylint: disable=invalid-name
        """
        Saves content if save_on_focus_out is True.

        """
        if self.save_on_focus_out and self.dirty and self.file_path:
            self._save()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides mousePressEvent to emits mouse_pressed signal

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_pressed.emit(event)
        cursor = self.cursorForPosition(event.pos())
        for sel in self._extra_selections:
            if sel.cursor.blockNumber() == cursor.blockNumber():
                sel.signals.clicked.emit(sel)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        """
        Emits mouse_released signal.

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_released.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):  # pylint: disable=invalid-name
        """
        Emits the mouse_wheel_activated signal.

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_wheel_activated.emit(event)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides mouseMovedEvent to display any decoration tooltip and emits
        the mouse_moved event.
        """
        cursor = self.cursorForPosition(event.pos())
        self._last_mouse_pos = event.pos()
        block_found = False
        for sel in self._extra_selections:
            if (sel.cursor.blockNumber() == cursor.blockNumber() and
                    sel.tooltip):
                if self._prev_tooltip_block_nbr != cursor.blockNumber():
                    self._tooltips_runner.request_job(
                        self.show_tooltip,
                        self.mapToGlobal(event.pos()), sel.tooltip[0: 1024])
                self._prev_tooltip_block_nbr = cursor.blockNumber()
                block_found = True
                break
        if not block_found:
            if self._prev_tooltip_block_nbr != -1:
                QtWidgets.QToolTip.hideText()
            self._prev_tooltip_block_nbr = -1
            self._tooltips_runner.cancel_requests()
        self.mouse_moved.emit(event)
        super().mouseMoveEvent(event)

    def showEvent(self, event):  # pylint: disable=invalid-name
        """ Overrides showEvent to update the viewport margins """
        super().showEvent(event)
        _logger().debug('show event')
        self._update_viewport_margins()

    def _show_context_menu(self, point):
        """ Shows the context menu """
        self._mnu = QtWidgets.QMenu()
        self._mnu.addActions(self._actions)
        self._mnu.popup(self.mapToGlobal(point))

    def _set_whitespaces_flags(self, show):
        """ Sets show white spaces flag """
        doc = self.document()
        options = doc.defaultTextOption()
        if show:
            options.setFlags(options.flags() |
                             QtGui.QTextOption.ShowTabsAndSpaces)
        else:
            options.setFlags(options.flags() &
                             ~QtGui.QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(options)

    def _init_actions(self):
        """ Init default QAction """
        def _icon(val):
            if isinstance(val, tuple):
                theme, icon = val
                return QtGui.QIcon.fromTheme(theme, QtGui.QIcon(icon))
            else:
                QtGui.QIcon(val)
        # Undo
        action = QtWidgets.QAction('Undo', self)
        action.setShortcut(QtGui.QKeySequence.Undo)
        action.setIcon(_icon(('edit-undo', ':/pyqode-icons/rc/edit-undo.png')))
        action.triggered.connect(self.undo)
        self.undoAvailable.connect(action.setEnabled)
        self.add_action(action)
        self.action_undo = action
        # Redo
        action = QtWidgets.QAction('Redo', self)
        action.setShortcut(QtGui.QKeySequence.Redo)
        action.setIcon(_icon(('edit-redo', ':/pyqode-icons/rc/edit-redo.png')))
        action.triggered.connect(self.redo)
        self.redoAvailable.connect(action.setEnabled)
        self.add_action(action)
        self.action_redo = action
        # separator
        self.add_separator()
        # Copy
        action = QtWidgets.QAction('Copy', self)
        action.setShortcut(QtGui.QKeySequence.Copy)
        action.setIcon(_icon(('edit-copy', ':/pyqode-icons/rc/edit-copy.png')))
        action.triggered.connect(self.copy)
        self.copyAvailable.connect(action.setEnabled)
        self.add_action(action)
        self.action_copy = action
        # cut
        action = QtWidgets.QAction('Cut', self)
        action.setShortcut(QtGui.QKeySequence.Cut)
        action.setIcon(_icon(('edit-cut', ':/pyqode-icons/rc/edit-cut.png')))
        action.triggered.connect(self.cut)
        self.copyAvailable.connect(action.setEnabled)
        self.add_action(action)
        self.action_cut = action
        # paste
        action = QtWidgets.QAction('Paste', self)
        action.setShortcut(QtGui.QKeySequence.Paste)
        action.setIcon(_icon(('edit-paste',
                              ':/pyqode-icons/rc/edit-paste.png')))
        action.triggered.connect(self.paste)
        self.add_action(action)
        self.action_paste = action
        # delete
        action = QtWidgets.QAction('Delete', self)
        action.setShortcut(QtGui.QKeySequence.Delete)
        action.setIcon(_icon(('edit-delete',
                              ':/pyqode-icons/rc/edit-delete.png')))
        action.triggered.connect(self.delete)
        self.add_action(action)
        self.action_delete = action
        # duplicate line
        action = QtWidgets.QAction('Duplicate line', self)
        action.setShortcut('Ctrl+D')
        action.triggered.connect(self.duplicate_line)
        self.add_action(action)
        self.action_duplicate_line = action
        # select all
        action = QtWidgets.QAction('Select all', self)
        action.setShortcut(QtGui.QKeySequence.SelectAll)
        action.setIcon(_icon(('edit-select-all',
                              ':/pyqode-icons/rc/edit-select-all.png')))
        action.triggered.connect(self.selectAll)
        self.add_action(action)
        self.action_select_all = action
        # separator
        self.add_separator()
        # indent
        action = QtWidgets.QAction('Indent', self)
        action.setShortcut('Tab')
        action.setIcon(_icon(('format-indent-more',
                              ':/pyqode-icons/rc/format-indent-more.png')))
        action.triggered.connect(self.indent)
        self.add_action(action)
        self.action_indent = action
        # unindent
        action = QtWidgets.QAction('Un-indent', self)
        action.setShortcut('Shift+Tab')
        action.setIcon(_icon(('format-indent-less',
                              ':/pyqode-icons/rc/format-indent-less.png')))
        action.triggered.connect(self.un_indent)
        self.add_action(action)
        self.action_un_indent = action
        # separator
        self.add_separator()
        # goto
        action = QtWidgets.QAction('Go to line', self)
        action.setShortcut('Ctrl+G')
        action.setIcon(_icon(('start-here',
                              ':/pyqode-icons/rc/goto-line.png')))
        action.triggered.connect(self.goto_line)
        self.add_action(action)
        self.action_goto_line = action

    def _init_settings(self):
        """ Init setting """
        self._show_whitespaces = False
        self._tab_length = 4
        self._use_spaces_instead_of_tabs = True
        self.setTabStopWidth(self._tab_length *
                             self.fontMetrics().widthChar(" "))
        self._set_whitespaces_flags(self._show_whitespaces)

    def _init_style(self):
        """ Inits style options """
        self._font_name = ""  # platform specific value in property setter
        self._font_size = 10
        self._background = QtGui.QColor('white')
        self._foreground = QtGui.QColor('black')
        self._whitespaces_foreground = QtGui.QColor('light gray')
        app = QtWidgets.QApplication.instance()
        self._sel_background = app.palette().highlight().color()
        self._sel_foreground = app.palette().highlightedText().color()
        self._reset_palette()

    def _update_visible_blocks(self, *args):
        """ Updates the list of visible blocks """
        #: pylint: disable=unused-argument
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
        """ Compute panel zone sizes """
        # Left panels
        left = 0
        for panel in self._panels[Panel.Position.LEFT].values():
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            left += size_hint.width()
        # Right panels
        right = 0
        for panel in self._panels[Panel.Position.RIGHT].values():
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            right += size_hint.width()
        # Top panels
        top = 0
        for panel in self._panels[Panel.Position.TOP].values():
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            top += size_hint.height()
        # Bottom panels
        bottom = 0
        for panel in self._panels[Panel.Position.BOTTOM].values():
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            bottom += size_hint.height()
        self._top, self._left, self._right, self._bottom = (
            top, left, right, bottom)
        return bottom, left, right, top

    def _resize_panels(self):
        """ Resizes panels """
        # pylint: disable=too-many-locals
        content_rect = self.contentsRect()
        viewport_content_rect = self.viewport().contentsRect()
        s_bottom, s_left, s_right, s_top = self._compute_zones_sizes()
        w_offset = content_rect.width() - (viewport_content_rect.width() +
                                           s_left + s_right)
        h_offset = content_rect.height() - (viewport_content_rect.height() +
                                            s_bottom + s_top)
        left = 0
        panels = list(self._panels[Panel.Position.LEFT].values())
        panels.sort(key=lambda panel: panel.order_in_zone, reverse=True)
        for panel in panels:
            if not panel.isVisible():
                continue
            panel.adjustSize()
            size_hint = panel.sizeHint()
            panel.setGeometry(content_rect.left() + left,
                              content_rect.top() + s_top,
                              size_hint.width(),
                              content_rect.height() - s_bottom - s_top -
                              h_offset)
            left += size_hint.width()
        right = 0
        panels = list(self._panels[Panel.Position.RIGHT].values())
        panels.sort(key=lambda panel: panel.order_in_zone, reverse=True)
        for panel in panels:
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            panel.setGeometry(content_rect.right() - right -
                              size_hint.width() - w_offset,
                              content_rect.top(), size_hint.width(),
                              content_rect.height() - h_offset)
            right += size_hint.width()
        top = 0
        panels = list(self._panels[Panel.Position.TOP].values())
        panels.sort(key=lambda panel: panel.order_in_zone)
        for panel in panels:
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            panel.setGeometry(content_rect.left(), content_rect.top() + top,
                              content_rect.width() - w_offset,
                              size_hint.height())
            top += size_hint.height()
        bottom = 0
        panels = list(self._panels[Panel.Position.BOTTOM].values())
        panels.sort(key=lambda panel: panel.order_in_zone)
        for panel in panels:
            if not panel.isVisible():
                continue
            size_hint = panel.sizeHint()
            panel.setGeometry(content_rect.left(),
                              content_rect.bottom() - bottom -
                              size_hint.height() - h_offset,
                              content_rect.width() - w_offset,
                              size_hint.height())
            bottom += size_hint.height()

    def _update_panels(self, rect, delta_y, force_update_margins=False):
        """ Updates panels """
        _logger().debug('_update_panels')
        for zones_id, zone in self._panels.items():
            if zones_id == Panel.Position.TOP or \
               zones_id == Panel.Position.BOTTOM:
                continue
            panels = list(zone.values())
            for panel in panels:
                if not panel.scrollable:
                    continue
                if delta_y:
                    panel.scroll(0, delta_y)
                else:
                    line, col = text.cursor_position(self)
                    oline, ocol = self._cached_cursor_pos
                    if line != oline or col != ocol:
                        panel.update(0, rect.y(), panel.width(), rect.height())
                    self._cached_cursor_pos = text.cursor_position(self)
        if rect.contains(self.viewport().rect()) or force_update_margins:
            _logger().debug('_update_panels -> _update_viewport_margins')
            self._update_viewport_margins()

    def _on_text_changed(self):
        """ Adjust dirty flag depending on editor's content """
        if not self._cleaning:
            self._modified_lines.add(text.cursor_position(self)[0])
            txt = self.toPlainText()
            self.dirty = (txt != self._original_text)

    def _update_viewport_margins(self):
        """ Update viewport margins """
        top = 0
        left = 0
        right = 0
        bottom = 0
        _logger().debug('updating viewport margins')
        _logger().debug('processing left panels')
        for panel in self._panels[Panel.Position.LEFT].values():
            if panel.isVisible():
                width = panel.sizeHint().width()
                _logger().debug('right panel width: %r', width)
                left += width
            else:
                _logger().debug('skipping invisible panel %r', panel.name)
        _logger().debug('processing right panels')
        for panel in self._panels[Panel.Position.RIGHT].values():
            if panel.isVisible():
                width = panel.sizeHint().width()
                _logger().debug('right panel width: %r', width)
                right += width
            else:
                _logger().debug('skipping invisible panel %s', panel.name)
        _logger().debug('processing top panels')
        for panel in self._panels[Panel.Position.TOP].values():
            if panel.isVisible():
                height = panel.sizeHint().height()
                _logger().debug('_bottom panel height: %r', height)
                top += height
            else:
                _logger().debug('skipping invisible panel %s', panel.name)
        _logger().debug('processing _bottom panels')
        for panel in self._panels[Panel.Position.BOTTOM].values():
            if panel.isVisible():
                height = panel.sizeHint().height()
                _logger().debug('_bottom panel height: %r', height)
                bottom += height
            else:
                _logger().debug('skipping invisible panel %s', panel.name)
        self._margin_sizes = (top, left, right, bottom)
        self.setViewportMargins(left, top, right, bottom)
        _logger().debug('viewport margins updated: %r', repr(
            self._margin_sizes))

    def _reset_palette(self):
        """ Resets QPalette """
        self.setFont(QtGui.QFont(self._font_family, self._font_size))
        pal = self.palette()
        pal.setColor(pal.Base, self._background)
        pal.setColor(pal.Text, self._foreground)
        pal.setColor(QtGui.QPalette.Highlight, self._sel_background)
        pal.setColor(QtGui.QPalette.HighlightedText, self._sel_foreground)
        self.setPalette(pal)
        self.repaint()

    def _do_home_key(self, event=None, select=False):
        """ Performs home key action """
        # get nb char to first significative char
        delta = self.textCursor().positionInBlock() - text.line_indent(self)
        if delta:
            cursor = self.textCursor()
            move = QtGui.QTextCursor.MoveAnchor
            if select:
                move = QtGui.QTextCursor.KeepAnchor
            cursor.movePosition(
                QtGui.QTextCursor.Left, move, delta)
            self.setTextCursor(cursor)
            if event:
                event.accept()

    def _save(self):
        """ Save to file """
        text.save_to_file(self)
