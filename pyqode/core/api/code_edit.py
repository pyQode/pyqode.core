import logging
from pyqode.core.api.utils import DelayJobRunner, TextHelper
from pyqode.core.dialogs.goto import DlgGotoLine
from pyqode.core.managers import BackendManager
from pyqode.core.managers import FileManager
from pyqode.core.managers import ModesManager
from pyqode.core.managers import TextDecorationsManager
from pyqode.core.managers import PanelsManager
# ensure pyqode resource have been imported and are ready to be used.
from pyqode.core._forms import pyqode_core_rc
from pyqode.qt import QtWidgets, QtCore, QtGui


def _logger():
    """ Returns module's logger """
    return logging.getLogger(__name__)


class CodeEdit(QtWidgets.QPlainTextEdit):
    """
    Base class for any pyQode source code editor widget.

    Extends :class:`QPlainTextEdit` by adding an extension system (
    modes and panels) and by adding a series of additional signal and methods.

    To interact with the editor content, you may use the Qt Text API (
    QTextCursor, ...) or use high level API functions defined in
    :mod:`pyqode.core.api.TextHelper`

    .. note:: setPlainText has been overridden to force you to define
        a mime type and an encoding.

    """
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

    #: Store the list of mimetypes associated with the editor, for
    #: specialised editors.
    mimetypes = []

    @property
    def use_spaces_instead_of_tabs(self):
        """ Use spaces instead of tabulations. Default is True. """
        return self._use_spaces_instead_of_tabs

    @use_spaces_instead_of_tabs.setter
    def use_spaces_instead_of_tabs(self, value):
        self._use_spaces_instead_of_tabs = value

    @property
    def tab_length(self):
        """ Tab length, number of spaces. """
        return self._tab_length

    @tab_length.setter
    def tab_length(self, value):
        self._tab_length = value

    @property
    def min_indent_column(self):
        """
        Minimum indent column.

        Some languages such as cobol starts coding at column 7.
        """
        return self._min_indent_column

    @min_indent_column.setter
    def min_indent_column(self, value):
        self._min_indent_column = value

    @property
    def save_on_focus_out(self):
        """
        Automatically saves editor content on focus out.

        Default is False.
        """
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
    def show_whitespaces(self, value):
        self._show_whitespaces = value
        self._set_whitespaces_flags(value)

    @property
    def font_name(self):
        """
        The editor font family name.
        """
        return self._font_family

    @font_name.setter
    def font_name(self, value):
        if value == "":
            value = 'Source Code Pro'
        self._font_family = value
        self._reset_stylesheet()

    @property
    def font_size(self):
        """
        The editor font size.
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self._reset_stylesheet()

    @property
    def background(self):
        """
        The editor background color.
        """
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._reset_stylesheet()

    @property
    def foreground(self):
        """
        The editor foreground color.
        """
        return self._foreground

    @foreground.setter
    def foreground(self, value):
        self._foreground = value
        self._reset_stylesheet()

    @property
    def whitespaces_foreground(self):
        """
        The editor white spaces' foreground color. White spaces are highlighted
        by the syntax highlighter. You should call rehighlight to update their
        color. This is not done automatically to prevent multiple, useless
        call to rehighlight which can take some time on big files.
        """
        return self._whitespaces_foreground

    @whitespaces_foreground.setter
    def whitespaces_foreground(self, value):
        self._whitespaces_foreground = value

    @property
    def selection_background(self):
        """
        The editor selection's background color.
        """
        return self._sel_background

    @selection_background.setter
    def selection_background(self, value):
        self._sel_background = value
        self._reset_stylesheet()

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
    def word_separators(self):
        """
        The list of word separators used by the code completion mode
        and the word clicked mode.
        """
        return self._word_separators

    @word_separators.setter
    def word_separators(self, separators):
        self._word_separators = separators

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
    def file(self):
        """ FileManager used to open/save file on the editor """
        return self._file

    @file.setter
    def file(self, file_manager):
        self._file = file_manager

    @property
    def backend(self):
        """ BackendManager used to control the backend process """
        return self._backend

    @property
    def modes(self):
        """ ModesManager used to append modes to the editor """
        return self._modes

    @property
    def panels(self):
        """ PanelsManager used to append panels to the editor """
        return self._panels

    @property
    def decorations(self):
        """ TextDecorationManager: manage the list of text decorations """
        return self._decorations

    @property
    def syntax_highlighter(self):
        for mode in self.modes:
            if hasattr(mode, 'highlightBlock'):
                return mode
        return None

    def __init__(self, parent=None, create_default_actions=True):
        """
        :param parent: Parent widget

        :param create_default_actions: Specify if the default actions (copy,
            paste, ...) must be created or not. Default is True.
        """
        super().__init__(parent)
        self._backend = BackendManager(self)
        self._file = FileManager(self)
        self._modes = ModesManager(self)
        self._panels = PanelsManager(self)
        self._decorations = TextDecorationsManager(self)

        self._word_separators = [
            '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{',
            '}', '|', ':', '"', "'", "<", ">", "?", ",", ".", "/", ";", '[',
            ']', '\\', '\n', '\t', '=', '-', ' '
        ]
        self._min_indent_column = 0
        self._save_on_focus_out = False
        self._use_spaces_instead_of_tabs = True
        self._whitespaces_foreground = None
        self._sel_background = None
        self._show_whitespaces = False
        self._foreground = None
        self._sel_foreground = None
        self._tab_length = 4
        self._font_size = 10
        self._background = None
        QtGui.QFontDatabase.addApplicationFont(
            ':/fonts/rc/SourceCodePro-Regular.ttf')
        QtGui.QFontDatabase.addApplicationFont(
            ':/fonts/rc/SourceCodePro-Bold.ttf')
        self._font_family = "Source Code Pro"
        self._mimetypes = []

        # Flags/Working variables
        self._last_mouse_pos = QtCore.QPoint(0, 0)
        self._modified_lines = set()
        self._cleaning = False
        self._visible_blocks = []
        self._tooltips_runner = DelayJobRunner(delay=700)
        self._prev_tooltip_block_nbr = -1
        self._original_text = ""

        self._dirty = False

        # setup context menu
        self._actions = []
        self._menus = []
        if create_default_actions:
            self._init_actions()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._mnu = None  # bug with PySide (github #63)

        # init settings and styles from global settings/style modules
        self._init_settings()
        self._init_style()

        # connect slots
        self.textChanged.connect(self._on_text_changed)
        self.blockCountChanged.connect(self.update)
        self.cursorPositionChanged.connect(self.update)
        self.selectionChanged.connect(self.update)

        self.setMouseTracking(True)
        self.setCenterOnScroll(True)
        self.setLineWrapMode(self.NoWrap)

    def __del__(self):
        self.backend.stop()

    def set_mouse_cursor(self, cursor):
        """
        Changes the viewport's cursor

        :param cursor: the mouse cursor to set.
        :type cursor: QtWidgets.QCursor
        """
        self.viewport().setCursor(cursor)

    def show_tooltip(self, pos, tooltip):
        """
        Show a tool tip at the specified position

        :param pos: Tooltip position
        :param tooltip: Tooltip text
        """
        QtWidgets.QToolTip.showText(pos, tooltip[0: 1024], self)

    def clear(self):
        super().clear()

    def setPlainText(self, txt, mime_type, encoding):
        """
        Extends setPlainText to force the user to set an encoding and a
        mime type.

        Emits the new_text_set signal.

        :param txt: The new text to set.
        :param mime_type: Associated mimetype. Setting the mime will update the
                          pygments lexer.
        :param encoding: text encoding
        """
        self.file.mimetype = mime_type
        self.file._encoding = encoding
        for mode in self.modes:
            if hasattr(mode, 'set_mime_type'):
                try:
                    _logger().debug('setting up lexer from mimetype: %s',
                                    self.file.mimetype)
                    mode.set_mime_type(self.file.mimetype)
                except ValueError:
                    _logger().exception(
                        'Failed to set lexer from mimetype: %s',
                        self.file.mimetype)
                    _logger().debug('setting up lexer from file path: %s',
                                    self.file.path)
                    mode.set_lexer_from_filename(self.file.path)
                break
        self._original_text = txt
        self._modified_lines.clear()
        import time
        t = time.time()
        super().setPlainText(txt)
        _logger().info('setPlainText duration: %fs' % (time.time() - t))
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
        self.addAction(action)
        return action

    def remove_action(self, action):
        """
        Removes an action/separator from the editor's context menu.

        :param action: Action/seprator to remove.
        """
        self._actions.remove(action)
        self.removeAction(action)

    def add_menu(self, menu):
        self._menus.append(menu)
        self.addActions(menu.actions())

    def remove_menu(self, menu):
        self._menus.remove(menu)
        for action in menu.actions():
            self.removeAction(action)

    @QtCore.Slot()
    def delete(self):
        """ Deletes the selected text """
        self.textCursor().removeSelectedText()

    @QtCore.Slot()
    def goto_line(self):
        """
        Shows goto line dialog and go to the selected line.
        """
        helper = TextHelper(self)
        line, result = DlgGotoLine.get_line(
            self, helper.current_line_nbr(), helper.line_count())
        if not result:
            return
        if not line:
            line = 1
        return helper.goto_line(line, move=True)

    @QtCore.Slot()
    def rehighlight(self):
        """
        Calls rehighlight on the installed syntax highlighter mode.
        """
        for mode in self.modes:
            if hasattr(mode, 'rehighlight'):
                mode.rehighlight()

    @QtCore.Slot()
    def reset_zoom(self):
        """
        Resets the zoom value.
        """
        self._font_size = 10
        self._reset_stylesheet()

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
        TextHelper(self).mark_whole_doc_dirty()
        self._reset_stylesheet()

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
        TextHelper(self).mark_whole_doc_dirty()
        self._reset_stylesheet()

    @QtCore.Slot()
    def duplicate_line(self):
        """
        Duplicates the line under the cursor. If multiple lines are selected,
        only the last one is duplicated.
        """
        cursor = self.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        cursor.beginEditBlock()
        col = cursor.positionInBlock()
        cursor.select(cursor.LineUnderCursor)
        line = cursor.selectedText()
        cursor.movePosition(cursor.EndOfBlock)
        cursor.insertText('\n' + line)
        cursor.movePosition(cursor.StartOfBlock)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, col)
        self.setTextCursor(cursor)
        cursor.endEditBlock()

    @QtCore.Slot()
    def indent(self):
        """
        Indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.api.CodeEdit.indent_requested`
        signal, the :class:`pyqode.core.modes.IndenterMode` will
        perform the actual indentation.
        """
        self.indent_requested.emit()

    @QtCore.Slot()
    def un_indent(self):
        """
        Un-indents the text cursor or the selection.

        Emits the :attr:`pyqode.core.api.CodeEdit.unindent_requested`
        signal, the :class:`pyqode.core.modes.IndenterMode` will
        perform the actual un-indentation.
        """
        self.unindent_requested.emit()

    def resizeEvent(self, e):
        """
        Overrides resize event to resize the editor's panels.

        :param e: resize event
        """
        super().resizeEvent(e)
        self.panels.resize()

    def paintEvent(self, e):
        """
        Overrides paint event to update the list of visible blocks and emit
        the painted event.

        :param e: paint event
        """
        self._update_visible_blocks(e)
        super().paintEvent(e)
        self.painted.emit(e)

    def keyPressEvent(self, event):
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
            super().keyReleaseEvent(event)

    def focusInEvent(self, event):
        """
        Overrides focusInEvent to emits the focused_in signal

        :param event: QFocusEvent
        """
        self.focused_in.emit(event)
        super().focusInEvent(event)
        self.repaint()

    def focusOutEvent(self, event):
        """
        Saves content if save_on_focus_out is True.

        """
        if self.save_on_focus_out and self.dirty and self.file.path:
            self.file.save()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        """
        Overrides mousePressEvent to emits mouse_pressed signal

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_pressed.emit(event)
        cursor = self.cursorForPosition(event.pos())
        for sel in self.decorations:
            if sel.cursor.blockNumber() == cursor.blockNumber():
                if sel.contains_cursor(cursor):
                    sel.signals.clicked.emit(sel)
        if not event.isAccepted():
            event.setAccepted(initial_state)
            super().mousePressEvent(event)

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
            super().mouseReleaseEvent(event)

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
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouseMovedEvent to display any decoration tooltip and emits
        the mouse_moved event.
        """
        cursor = self.cursorForPosition(event.pos())
        self._last_mouse_pos = event.pos()
        block_found = False
        for sel in self.decorations:
            if sel.contains_cursor(cursor) and sel.tooltip:
                if (self._prev_tooltip_block_nbr != cursor.blockNumber() or
                        not QtWidgets.QToolTip.isVisible()):
                    pos = event.pos()
                    # add left margin
                    pos.setX(pos.x() + self.panels.margin_size())
                    # add top margin
                    pos.setY(pos.y() + self.panels.margin_size(0))
                    self._tooltips_runner.request_job(
                        self.show_tooltip,
                        self.mapToGlobal(pos), sel.tooltip[0: 1024])
                    self._prev_tooltip_block_nbr = cursor.blockNumber()
                block_found = True
                break
        if not block_found and self._prev_tooltip_block_nbr != -1:
            QtWidgets.QToolTip.hideText()
            self._prev_tooltip_block_nbr = -1
            self._tooltips_runner.cancel_requests()
        self.mouse_moved.emit(event)
        super().mouseMoveEvent(event)

    def showEvent(self, event):
        """ Overrides showEvent to update the viewport margins """
        super().showEvent(event)
        _logger().debug('show event')

    def _show_context_menu(self, point):
        """ Shows the context menu """
        self._mnu = QtWidgets.QMenu()
        for menu in self._menus:
            self._mnu.addMenu(menu)
        self._mnu.addSeparator()
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
        self.add_separator()

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
        self._background = QtGui.QColor('white')
        self._foreground = QtGui.QColor('black')
        self._whitespaces_foreground = QtGui.QColor('light gray')
        app = QtWidgets.QApplication.instance()
        self._sel_background = app.palette().highlight().color()
        self._sel_foreground = app.palette().highlightedText().color()
        self._font_size = 10
        self.font_name = ""

    def _update_visible_blocks(self, *args):
        """ Updates the list of visible blocks """
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

    def _on_text_changed(self):
        """ Adjust dirty flag depending on editor's content """
        if not self._cleaning:
            ln = TextHelper(self).cursor_position()[0]
            self._modified_lines.add(ln)
            txt = self.toPlainText()
            self.dirty = (txt != self._original_text)

    def _reset_stylesheet(self):
        """ Resets stylesheet"""
        self.setFont(QtGui.QFont(self._font_family, self._font_size))
        p = self.palette()
        p.setColor(QtGui.QPalette.Base, self.background)
        p.setColor(QtGui.QPalette.Text, self.foreground)
        p.setColor(QtGui.QPalette.Highlight, self.selection_background)
        p.setColor(QtGui.QPalette.HighlightedText, self.selection_foreground)
        self.setPalette(p)
        self.repaint()

    def _do_home_key(self, event=None, select=False):
        """ Performs home key action """
        # get nb char to first significative char
        delta = (self.textCursor().positionInBlock() -
                 TextHelper(self).line_indent())
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
