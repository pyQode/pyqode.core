#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
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

from PyQt4 import QtGui, QtCore

from pyqode.core import logger, dialogs
from pyqode.core.api import constants
from pyqode.core.api.properties import PropertyRegistry
from pyqode.core.api.client import JsonTcpClient
from pyqode.core.api.system import DelayJobRunner


class Mode(object):
    """
    Base class for editor extensions. An extension is a "thing" that can be
    installed on the QCodeEdit to add new behaviours or to modify the
    appearance.

    An extension is added to a QCodeEdit by using the
    :meth:`pyqode.core.QCodeEdit.installMode` or
    :meth:`pyqode.core.QCodeEdit.installPanel` methods.

    Subclasses must/should override the following methods:
        - :meth:`pyqode.core.Mode._onStateChanged`
        - :meth:`pyqode.core.Mode._onStyleChanged`
        - :meth:`pyqode.core.Mode._onSettingsChanged`

    Uses :attr:`pyqode.core.Mode.IDENTIFIER` and
    :attr:`pyqode.core.Mode.DESCRIPTION` to setup the mode name and
    description:

    .. code-block:: python

        class MyMode(Mode):
            IDENTIFIER = "myMode"
            DESCRIPTION = "Describes your mode here"

        m = MyMode()
        print(m.name, m.description)

        >>> ("myMode", "Describes your mode here" )
    """
    #: The mode identifier, must redefined for every subclasses
    IDENTIFIER = ""
    #: The mode description, must redefined for every subclasses
    DESCRIPTION = ""

    @property
    def editor(self):
        """
        Provides easy access to the CodeEditorWidget weakref. **READ ONLY**

        :type: pyqode.core.QCodeEdit
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Tell if the mode is enabled, :meth:`pyqode.core.Mode._onStateChanged`
        is called when the value changed.

        :type: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled != self._enabled:
            self._enabled = enabled
            self._on_state_changed(enabled)

    def __init__(self):
        #: Mode name/identifier. :class:`pyqode.core.QCodeEdit` use it as the
        #: attribute key when you install a mode.
        self.name = self.IDENTIFIER
        #: Mode description
        self.description = self.DESCRIPTION
        self._enabled = False
        self._editor = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def _on_install(self, editor):
        """
        Installs the extension on the editor. Subclasses might want to override
        this method to add new style/settings properties to the editor.

        .. note:: This method is called by QCodeEdit when you install a Mode.
                  You should never call it yourself, even in a subclass.

        .. warning:: Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pyqode.core.QCodeEdit
        """
        self._editor = weakref.ref(editor)
        self.enabled = True
        editor.style.valueChanged.connect(self._on_style_changed)
        editor.settings.valueChanged.connect(self._on_settings_changed)

    def _on_uninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self._editor = None

    def _on_state_changed(self, state):
        """
        Called when the enable state changed.

        This method does not do anything, you may override it if you need
        to connect/disconnect to the editor's signals (connect when state is
        true and disconnect when it is false).

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        pass

    def _on_style_changed(self, section, key):
        """
        Automatically called when a style property changed.

        .. note: If the editor style changed globally, key will be set to an
                 empty string.

        :param section: The section which contains the property that has
            changed.
        :type section: str

        :param key: The property key
        :type key: str
        """
        pass

    def _on_settings_changed(self, section, key):
        """
        Automatically called when a settings property changed

        .. note: If the editor style changed globally, key will be set to an
                 empty string.

        :param section: The section which contains the property that has
            changed.
        :type section: str

        :param key: The property key
        :type key: str
        """
        pass


class Panel(QtGui.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a QWidget.

    .. note:: A disabled panel will be hidden automatically.
    """

    # todo make it an enum when python 3.4 is available
    class Position(object):
        """
        Enumerates the possible panel positions
        """
        #: Top margin
        TOP = 0
        #: Left margin
        LEFT = 1
        #: Right margin
        RIGHT = 2
        #: Bottom margin
        BOTTOM = 3

    @property
    def scrollable(self):
        """
        A scrollable panel will follow the editor's scroll-bars. Left and right
        panels follow the vertical scrollbar. Top and bottom panels follow the
        horizontal scrollbar.

        :type: bool
        """
        return self._scrollable

    @scrollable.setter
    def scrollable(self, value):
        self._scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        #: Panel order into the zone it is installed to. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.order_in_zone = -1
        self._scrollable = False
        self._background_brush = None
        self._foreground_pen = None

    def _on_install(self, editor):
        """
        Extends :meth:`pyqode.core.Mode._onInstall` method to set the editor
        instance as the parent widget.

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param editor: Editor instance
        :type editor: pyqode.core.editor.QCodeEdit
        """
        Mode._on_install(self, editor)
        self.setParent(editor)
        self.editor.refresh_panels()
        self._background_brush = QtGui.QBrush(QtGui.QColor(
            self.palette().window().color()))
        self._foreground_pen = QtGui.QPen(QtGui.QColor(
            self.palette().windowText().color()))

    def _on_state_changed(self, state):
        """
        Shows/Hides the Panel

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if not self.editor.isVisible():
            return
        if state is True:
            self.show()
        else:
            self.hide()

    def paintEvent(self, event):
        if self.isVisible():
            # fill background
            self._background_brush = QtGui.QBrush(QtGui.QColor(
                self.palette().window().color()))
            self._foreground_pen = QtGui.QPen(QtGui.QColor(
                self.palette().windowText().color()))
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self._background_brush)

    def showEvent(self, *args, **kwargs):
        self.editor.refresh_panels()

    def setVisible(self, visible):
        QtGui.QWidget.setVisible(self, visible)
        self.editor.refresh_panels()


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

        Gets/sets self.settings.value("showWhiteSpaces")
        """
        return self.settings.value("showWhiteSpaces")

    @show_whitespaces.setter
    def show_whitespaces(self, value):
        assert isinstance(value, bool)
        self.settings.set_value("showWhiteSpaces", value)

    @property
    def save_on_focus_out(self):
        """
        Enables auto save on focus out.

        Gets/sets self.settings.value("saveOnFrameDeactivation")
        """
        return self.settings.value("saveOnFrameDeactivation")

    @save_on_focus_out.setter
    def save_on_focus_out(self, value):
        assert isinstance(value, bool)
        self.settings.set_value("saveOnFrameDeactivation", value)

    @property
    def font_name(self):
        """
        The editor font.

        Gets/sets self.style.value("font")
        """
        return self.style.value("font")

    @font_name.setter
    def font_name(self, value):
        self.style.set_value("font", value)

    @property
    def font_size(self):
        """
        The editor font size.

        Gets/sets self.style.value("fontSize")
        """
        return self.style.value("fontSize")

    @font_size.setter
    def font_size(self, value):
        self.style.set_value("fontSize", value)

    @property
    def background(self):
        """
        The editor background color.

        Gets/sets self.style.value("background")
        """
        return self.style.value("background")

    @background.setter
    def background(self, value):
        self.style.set_value("background", value)

    @property
    def foreground(self):
        """
        The editor foreground color.

        Gets/sets self.style.value("foreground")
        """
        return self.style.value("foreground")

    @foreground.setter
    def foreground(self, value):
        self.style.set_value("foreground", value)

    @property
    def whitespaces_foreground(self):
        """
        The editor white spaces' foreground color.

        Gets/sets self.style.value("whiteSpaceForeground")
        """
        return self.style.value("whiteSpaceForeground")

    @whitespaces_foreground.setter
    def whitespaces_foreground(self, value):
        self.style.set_value("whiteSpaceForeground", value)

    @property
    def selection_background(self):
        """
        The editor selection's background color.

        Gets/sets self.style.value("selectionBackground")
        """
        return self.style.value("selectionBackground")

    @selection_background.setter
    def selection_background(self, value):
        self.style.set_value("selectionBackground", value)

    @property
    def selection_foreground(self):
        """
        The editor selection's foreground color.

        Gets/sets self.style.value("selectionForeground")
        """
        return self.style.value("selectionForeground")

    @selection_foreground.setter
    def selection_foreground(self, value):
        self.style.set_value("selectionForeground", value)

    @property
    def current_line_text(self):
        return self.line_text(self.cursor_position[0])

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
    def cursor_position(self):
        """
        Returns the text cursor position (line, column).

        .. note:: The line number is 1 based while the column number is 0
            based.

        :return: The cursor position (line, column)
        :rtype: tuple(int, int)
        """
        return (self.textCursor().blockNumber() + 1,
                self.textCursor().columnNumber())

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

        :return: A list of tuple(top position, line number, block)
        :rtype: List of tuple(int, int, QtGui.QTextBlock)
        """
        return self._blocks

    @property
    def style(self):
        """
        Gets/Sets the editor style properties.

        :type: pyqode.core.QPropertyRegistry
        """
        return self._style

    @style.setter
    def style(self, value):
        self._style.update(value)

    @property
    def settings(self):
        """
        Gets/Sets the editor settings properties.

        :type: pyqode.core.QPropertyRegistry
        """
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings.update(value)

    @property
    def line_count(self):
        """ Returns the document line count """
        return self.document().blockCount()

    def __init__(self, parent=None, create_default_actions=True):
        """
        :param parent: Parent widget

        :param create_default_actions: Specify if the default actions (copy,
                                     paste, ...) must be created.
                                     Default is True.
        """
        QtGui.QPlainTextEdit.__init__(self, parent)
        self.client = None
        self._last_mouse_pos = None
        self._cached_cursor_pos = (-1, -1)
        self._modified_lines = set()
        self._cleaning = False
        self._margin_sizes = (0, 0, 0, 0)
        self.top = self.left = self.right = self.bottom = -1
        self.setCenterOnScroll(True)

        #: The list of visible blocks, update every paintEvent
        self._blocks = []

        self._parenthesis_selections = []

        self._tooltips_runner = DelayJobRunner(
            self, nb_threads_max=1, delay=700)
        self._prev_tooltip_block_nbr = -1

        #: The list of actions, (none is a separator)
        self._actions = []
        if create_default_actions:
            self._create_default_actions()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # panels and modes
        self._modes = {}
        self._panels = {Panel.Position.TOP: {},
                        Panel.Position.LEFT: {},
                        Panel.Position.RIGHT: {},
                        Panel.Position.BOTTOM: {}}

        #: Path of the current file
        self._fpath = None
        #: Encoding of the current file
        self._fencoding = None
        #: Original text, used to compute the control flag
        self._original_text = ""

        #: Dirty flag; tells if the widget text content is different from the
        #: file content
        self._dirty = False

        self._init_settings()
        self._init_style()

        #: The list of active extra-selections (TextDecoration)
        self._selections = []

        # connect slots
        self.blockCountChanged.connect(self._update_viewport_margins)
        self.textChanged.connect(self._on_text_changed)
        self.updateRequest.connect(self._update_panels)
        self.blockCountChanged.connect(self.update)
        self.cursorPositionChanged.connect(self.update)
        self.selectionChanged.connect(self.update)

        self.setMouseTracking(True)

        self.mnu = None

    def __del__(self):
        try:
            self.stop_server()
        except RuntimeError:
            pass  # wrapped C/C++ object  already deleted

    def start_server(self, script, interpreter=sys.executable, args=None):
        """
        Starts the server process.

        The server is a python script that starts a
        :class:`pyqode.core.api.server.JsonServer`. You (the user) must write
        the server script so that you can apply your own configuration
        server side.

        The script can be run with a custom interpreter. The default is to use
        sys.executable.

        :param str script: Path to the server main script.
        :param str interpreter: The python interpreter to use to run the server
            script. If None, sys.executable is used unless we are in a frozen
            application (cx_Freeze). The executable is not used if the
            executable scripts ends with '.exe' on Windows
        :param list args: list of additional command line args to use to start
            the server process.
        """
        self.client = JsonTcpClient(self)
        self.client.start(script, interpreter=interpreter, args=args)

    def stop_server(self):
        """
        Stops the server process and closes the associated client socket.

        It is automatically called when the widgets is destroyed but you should
        rather close it explicitly.
        """
        try:
            if self.client:
                self.client.close()
        except RuntimeError:
            pass

    def request_work(self, worker_class_or_function, args, on_receive=None):
        """
        Requests some work on the server process.

        :param worker_class_or_function: Worker class or function
        """
        fully_qualified_name = '%s.%s' % (worker_class_or_function.__module__,
                                          worker_class_or_function.__name__)
        self.client.request_work(worker_class_or_function, args,
                                 on_receive=on_receive)

    def uninstall_all(self):
        """
        Uninstalls all modes and panels.
        """
        while len(self._modes):
            k = list(self._modes.keys())[0]
            self.uninstall_mode(k)
        while len(self._panels):
            zone = list(self._panels.keys())[0]
            while len(self._panels[zone]):
                k = list(self._panels[zone].keys())[0]
                self.uninstall_panel(k, zone)
            self._panels.pop(zone, None)

    def show_context_menu(self, pt):
        self.mnu = QtGui.QMenu()
        self.mnu.addActions(self._actions)
        self.mnu.popup(self.mapToGlobal(pt))

    @QtCore.pyqtSlot()
    def delete(self):
        """ Deletes the selected text """
        self.textCursor().removeSelectedText()

    def goto_line(self, line=None, move=True, column=None):
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
            line, result = dialogs.GoToLineDialog.get_line(
                self, self.cursor_position[0], self.line_count)
            if not result:
                return
            if not line:
                line = 1
        tc = self.textCursor()
        tc.movePosition(tc.Start, tc.MoveAnchor)
        tc.movePosition(tc.Down, tc.MoveAnchor, line - 1)
        if column:
            tc.movePosition(tc.Right, tc.MoveAnchor, column)
        if move:
            self.setTextCursor(tc)
        return tc

    def selected_text(self):
        """ Returns the selected text. """
        return self.textCursor().selectedText()

    def select_word_under_cursor(self, select_whole_word=False, tc=None):
        """
        Selects the word under cursor using the separators defined in the
        the constants module.

        :param select_whole_word: If set to true the whole word is selected,
         else the selection stops at the cursor position.

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
        if select_whole_word:
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

    def select_word_under_mouse_cursor(self):
        """
        Selects the word under the **mouse** cursor.

        :return: A QTextCursor with the word under mouse cursor selected.
        """
        tc = self.cursorForPosition(self._last_mouse_pos)
        tc = self.select_word_under_cursor(True, tc)
        #print(tc.selectedText())
        return tc

    def detect_encoding(self, data):
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
            encoding = chardet.detect(bytes(data))['encoding']
        except ImportError:
            logger.warning("chardet not available, using utf8 by default")
            encoding = self.default_encoding()
        return encoding

    @staticmethod
    def default_encoding():
        """ Returns the result of :py:func:`sys.getfilesystemencoding` """
        return sys.getfilesystemencoding()

    def _read_file(self, path, replace_tabs_by_spaces=True, encoding=None,
                   auto_detect_encoding=False):
        # encoding = "utf-8"
        with open(path, 'rb') as f:
            data = f.read()
            if not encoding and auto_detect_encoding:
                try:
                    encoding = self.detect_encoding(data)
                except UnicodeEncodeError:
                    QtGui.QMessageBox.warning(self, "Failed to open file",
                                              "Failed to detect encoding")
            if not encoding:
                encoding = self.default_encoding()
            content = data.decode(encoding)
        if replace_tabs_by_spaces:
            content = content.replace(
                "\t", " " * self.settings.value("tabLength"))
        return content, encoding

    def open_file(self, path, replace_tabs_by_spaces=True, encoding=None,
                  detect_encoding=False):
        """
        Helper method to open a file in the editor.

        :param path: The file path to open
        :type path: str

        :param replace_tabs_by_spaces: True to replace tabs by spaces
               (settings.value("tabSpace") * " ")
        :type replace_tabs_by_spaces: bool

        :param encoding: The encoding to use. If no encoding is provided and
                         detectEncoding is false, pyqode will try to decode the
                         content using the system default encoding.
        :type encoding: str

        :param detect_encoding: If true and no encoding is specified, pyqode
            will try to detect encoding using chardet2.
        :type detect_encoding: bool
        """
        content, encoding = self._read_file(path, replace_tabs_by_spaces,
                                            encoding, detect_encoding)
        self._fpath = path
        self._fencoding = encoding
        self.setPlainText(content)
        self.dirty = False

    def line_text(self, line_nbr):
        """
        Gets the current line text.

        :param line_nbr: The line number of the text to get

        :return: Entire line's text
        :rtype: str
        """
        tc = self.textCursor()
        tc.movePosition(tc.Start)
        tc.movePosition(tc.Down, tc.MoveAnchor, line_nbr - 1)
        tc.select(tc.LineUnderCursor)
        return tc.selectedText()

    def set_line_text(self, line_nbr, text):
        """
        Replace the text of a single line by the supplied text.

        :param line_nbr: The line number of the text to remove
        :type: lineNbr: int

        :param text: Replacement text
        :type: text: str
        """
        tc = self.textCursor()
        tc.movePosition(tc.Start)
        tc.movePosition(tc.Down, tc.MoveAnchor, line_nbr - 1)
        tc.select(tc.LineUnderCursor)
        tc.insertText(text)

    def remove_last_line(self):
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

    def clean_document(self):
        """
        Removes trailing whitespaces and ensure one single blank line at the
        end of the QTextDocument. (call setPlainText to update the text).
        """
        value = self.verticalScrollBar().value()
        pos = self.cursor_position

        self.textCursor().beginEditBlock()

        # cleanup whitespaces
        self._cleaning = True
        eaten = 0
        for line in self._modified_lines:
            for j in range(-1, 2):
                if line + j != pos[0]:
                    txt = self.line_text(line + j)
                    stxt = txt.rstrip()
                    self.set_line_text(line + j, stxt)

        if self.line_text(self.line_count):
            self.appendPlainText("\n")
        else:
            # remove last blank line (except one)
            i = 0
            while True:
                l = self.line_text(self.line_count - i)
                if l:
                    break
                i += 1
            for j in range(i - 1):
                self.remove_last_line()

        self._cleaning = False
        self._original_text = self.toPlainText()

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

    @QtCore.pyqtSlot()
    def save_to_file(self, path=None, encoding=None, force=False):
        """
        Saves the plain text to a file.

        :param path: Optional file path. If None, we use the current file
                         path (set by openFile).
        :type path: str or None

        :param encoding: Optional encoding. If None, the method will use the
                         last encoding used to open/save the file.

        :param force: Bypass the dirty flag and force the save.

        :return: The operation status as a bool (True for success)
        """
        if not self.dirty and not force:
            return True
        self.text_saving.emit(path)
        if len(self.toPlainText()):
            self.clean_document()
        if not path:
            if self.file_path:
                path = self.file_path
            else:
                return False
        if encoding:
            self._fencoding = encoding
        try:
            content = self._encode_plain_text(self.file_encoding)
        except UnicodeEncodeError:
            content = self._encode_plain_text(self.default_encoding())
        with open(path, "wb") as f:
            f.write(content)
        self.dirty = False
        self._fpath = path
        self.text_saved.emit(path)
        return True

    def install_mode(self, mode):
        """
        Installs a mode on the editor.

        The mode is set as an object attribute using the mode's name as the
        key.

        :param mode: The mode instance to install.
        :type mode: pyqode.core.editor.Mode
        """
        self._modes[mode.name] = mode
        mode._on_install(self)
        setattr(self, mode.name, mode)

    def uninstall_mode(self, name):
        """
        Uninstalls a previously installed mode.

        :param name: The name of the mode to uninstall

        :return:
        """
        logger.debug('Uninstalling mode %s' % name)
        m = self.mode(name)
        if m:
            m._on_uninstall()
            self._modes.pop(name, None)
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
        return self._modes[name]

    def modes(self):
        """
        Returns the dictionary of modes.
        """
        return self._modes

    def install_panel(self, panel, position=Panel.Position.LEFT):
        """
        Installs a panel on on the editor. You must specify the position of the
        panel (panels are rendered in one of the four document margins, see
        :class:`pyqode.core.editor.Panel.Position`.

        The panel is set as an object attribute using the panel's name as the
        key.

        :param panel: The panel instance to install
        :param position: The panel position

        :type panel: pyqode.core.editor.Panel
        :type position: int
        """
        panel.order_in_zone = len(self._panels[position])
        self._panels[position][panel.name] = panel
        panel._on_install(self)
        self._update_viewport_margins()
        setattr(self, panel.name, panel)

    def uninstall_panel(self, name, zone):
        """
        Uninstalls a previously installed panel.

        :param name: The name of the panel to uninstall

        :return:
        """
        logger.debug('Uninstalling panel %s' % name)
        m = self._panels[zone][name]
        if m:
            try:
                m._on_uninstall()
            except (RuntimeError, AttributeError):
                pass
            self._panels[zone].pop(name, None)
        self.__dict__.pop(name, None)

    def panels(self):
        """
        Returns the panels dictionary.

        :return: A dictionary of :class:`pyqode.core.Panel`
        :rtype: dict
        """
        return self._panels

    def add_decoration(self, decoration):
        """
        Adds a text decoration.

        :param decoration: Text decoration
        :type decoration: pyqode.core.TextDecoration
        """
        if decoration not in self._selections:
            self._selections.append(decoration)
            self._selections = sorted(self._selections,
                                      key=lambda sel: sel.draw_order)
            self.setExtraSelections(self._selections)

    def remove_decoration(self, decoration):
        """
        Remove text decoration.

        :param decoration: The decoration to remove
        :type decoration: pyqode.core.TextDecoration
        """
        try:
            self._selections.remove(decoration)
            self.setExtraSelections(self._selections)
        except ValueError:
            pass

    def clear_decorations(self):
        """
        Clears all text decorations
        """
        self._selections[:] = []
        self.setExtraSelections(self._selections)

    def margin_size(self, position=Panel.Position.LEFT):
        """
        Gets the size of a specific margin.

        :param position: Margin position. See
            :class:`pyqode.core.Panel.Position`

        :return: The size of the specified margin
        :rtype: float
        """
        return self._margin_sizes[position]

    def select_full_lines(self, start, end, apply_selection=True):
        """
        Select entire lines between start and end.

        :param start: Start line number (1 based)
        :type start: int
        :param end: End line number (1 based)
        :type end: int

        :param apply_selection: True to apply the selection before returning
         the QTextCursor.
        :type apply_selection: bool

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
            if apply_selection:
                self.setTextCursor(tc)

    def selection_range(self):
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

    def line_pos_from_number(self, line_number):
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

    def line_nbr_from_position(self, y_pos):
        """
        Returns the line number from the y_pos

        :param y_pos: Y pos in the QCodeEdit

        :return: Line number (1 based)
        :rtype: int
        """
        height = self.fontMetrics().height()
        for top, l, block in self._blocks:
            if top <= y_pos <= top + height:
                return l
        return None

    def reset_zoom(self):
        """
        Resets the zoom value.
        """
        self.style.set_value("fontSize", constants.FONT_SIZE)

    def mark_whole_doc_dirty(self):
        """
        Marks the whole document as dirty to force a full refresh. **SLOW**
        """
        tc = self.textCursor()
        tc.select(tc.Document)
        self.document().markContentsDirty(tc.selectionStart(),
                                          tc.selectionEnd())

    def zoom_in(self, increment=1):
        """
        Zooms in the editor.

        The effect is achieved by increasing the editor font size by the
        increment value.

        Panels that needs to be resized depending on the font size need to
        implement onStyleChanged.
        """
        self.style.set_value("fontSize",
                             self.style.value("fontSize") + increment)
        self.mark_whole_doc_dirty()

    def zoom_out(self, increment=1):
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
        self.style.set_value("fontSize", value)
        self.mark_whole_doc_dirty()

    def line_indent(self):
        """
        Returns the current line indentation

        :return: Number of spaces that makes the indentation level of the
                 current line
        """
        # todo rewrite this using line_text
        original_cursor = self.textCursor()
        cursor = QtGui.QTextCursor(original_cursor)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                            QtGui.QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        indentation = len(line) - len(line.lstrip())
        self.setTextCursor(original_cursor)
        return indentation

    def _show_whitespaces(self, show):
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

    def set_cursor(self, cursor):
        """
        Changes the viewport cursor

        :param cursor: the nex mouse cursor to set.
        :type cursor: QtGui.QCursor
        """
        self.viewport().setCursor(cursor)
        QtGui.QApplication.processEvents()

    def refresh_panels(self):
        """ Refreshes the editor panels. """
        self._resize_panels()
        self._update_viewport_margins()
        self._update_panels(self.contentsRect(), 0)
        self.update()

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
        self.update_visible_blocks(e)
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
        replace = self.settings.value("useSpacesInsteadOfTab")
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
        if self.settings.value("saveOnFrameDeactivation"):
            self.save_to_file()

    def mousePressEvent(self, event):
        """
        Overrides mousePressEvent to emits mouse_pressed signal

        :param event: QMouseEvent
        """
        initial_state = event.isAccepted()
        event.ignore()
        self.mouse_pressed.emit(event)
        c = self.cursorForPosition(event.pos())
        for sel in self._selections:
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
        for sel in self._selections:
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

    def show_tooltip(self, pos, tooltip):
        """
        Show a tool tip at the specified position

        :param pos: Tooltip position

        :param tooltip: Tooltip text
        """
        QtGui.QToolTip.showText(pos, tooltip[0: 1024], self)
        self._prev_tooltip_block_nbr = -1

    def showEvent(self, event):
        """ Overrides showEvent to update the viewport margins """
        QtGui.QPlainTextEdit.showEvent(self, event)
        self._update_viewport_margins()

    def setPlainText(self, txt):
        """
        Overrides the setPlainText method to keep track of the original text.

        Emits the new_text_set signal.

        :param txt: The new text to set.
        """
        QtGui.QPlainTextEdit.setPlainText(self, txt)
        self._original_text = txt
        self._modified_lines.clear()
        self._on_settings_changed("", "")
        self.new_text_set.emit()
        self.redoAvailable.emit(False)
        self.undoAvailable.emit(False)
        title = QtCore.QFileInfo(self.file_path).fileName()
        self.setDocumentTitle(title)
        self.setWindowTitle(title)

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
            if action.text() in constants.ICONS:
                icon, shortcut, theme = constants.ACTIONS[action.text()]
                if use_theme:
                    action.setIcon(QtGui.QIcon.fromTheme(
                        theme, QtGui.QIcon(icon)))
                else:
                    action.setIcon(QtGui.QIcon(icon))
        try:
            self.searchAndReplacePanel.refresh_icons(use_theme=use_theme)
        except AttributeError:
            pass  # panel not installed

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
                icon, shortcut, theme = constants.ACTIONS[name]
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
        """
        Init the settings PropertyRegistry
        """
        self._settings = PropertyRegistry()
        self.settings.valueChanged.connect(self._on_settings_changed)
        self.settings.add_property("showWhiteSpaces", False)
        self.settings.add_property("tabLength", constants.TAB_SIZE)
        self.settings.add_property("useSpacesInsteadOfTab", True)
        self.settings.add_property("minIndentColumn", 0)
        self.settings.add_property("saveOnFrameDeactivation", True)

    def _init_style(self):
        """
        Init the style PropertyRegistry
        """
        self._style = PropertyRegistry()
        self.style.valueChanged.connect(self._reset_palette)
        self.style.add_property("font", constants.FONT)
        self.style.add_property("fontSize", constants.FONT_SIZE)
        self.style.add_property("background", constants.EDITOR_BACKGROUND)
        self.style.add_property("foreground", constants.EDITOR_FOREGROUND)
        self.style.add_property("whiteSpaceForeground",
                                constants.EDITOR_WS_FOREGROUND)
        self.style.add_property("selectionBackground",
                                self.palette().highlight().color())
        self.style.add_property("selectionForeground",
                                self.palette().highlightedText().color())
        self._reset_palette("", "")

    def _encode_plain_text(self, encoding):
        content = bytes(self.toPlainText().encode(encoding))
        return content

    def update_visible_blocks(self, event):
        """
        Update the list of visible blocks/lines position.

        :param event: QtGui.QPaintEvent
        """
        self._blocks[:] = []
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
                self._blocks.append((top, block_nbr + 1, block))
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
        """
        Resizes panels geometries
        """
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
        """
        Updates the panel on update request. (Scroll, update clipping rect,...)
        """
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
                    l, c = self.cursor_position
                    ol, oc = self._cached_cursor_pos
                    if l != ol or c != oc:
                        panel.update(0, rect.y(), panel.width(), rect.height())
                    self._cached_cursor_pos = self.cursor_position
        if rect.contains(self.viewport().rect()):
            self._update_viewport_margins()

    def _on_text_changed(self):
        """
        Updates dirty flag on text changed.
        """
        if not self._cleaning:
            self._modified_lines.add(self.cursor_position[0])
            txt = self.toPlainText()
            self.dirty = (txt != self._original_text)

    def _update_viewport_margins(self):
        """
        Updates the viewport margins depending on the installed panels
        """
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

    def _reset_palette(self, section, key):
        """ Resets stylesheet. """
        if key == "font" or key == "fontSize" or not key:
            font = self.style.value("font")
            self.setFont(QtGui.QFont(font, self.style.value("fontSize")))
        if (key == "background" or key == "foreground" or
                key == "selectionBackground" or key == "selectionForeground"
                or not key):
            p = self.palette()
            c = QtGui.QColor(self.style.value("background"))
            p.setColor(p.Base, c)
            c = QtGui.QColor(self.style.value("foreground"))
            p.setColor(p.Text, c)
            c = QtGui.QColor(self.style.value("selectionBackground"))
            p.setColor(QtGui.QPalette.Highlight, c)
            c = QtGui.QColor(self.style.value("selectionForeground"))
            p.setColor(QtGui.QPalette.HighlightedText, c)
            self.setPalette(p)

    def _on_settings_changed(self, section, key):
        self.setTabStopWidth(int(self.settings.value("tabLength")) *
                             self.fontMetrics().widthChar(" "))
        self._show_whitespaces(self.settings.value("showWhiteSpaces"))

    def _do_home_key(self, event=None, select=False):
        # get nb char to first significative char
        delta = self.textCursor().positionInBlock() - self.line_indent()
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
