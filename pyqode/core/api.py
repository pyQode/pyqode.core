"""
This module contains the public API for interacting with QCodeEdit, client
side.

The API is a mostly procedural API that works on QCodeEdit instance.

Originally most of those functions were methods of QCodeEdit, we moved them
in separates modules for the sake of readability.

The API can be subdivised into several parts:

    1) Extension API:

        Base classes for extending QCodeEdit: Mode and panel and functions to
        add/remove/query modes and panels on QCodeEdit

    2) QTextCursor/QTextDocument API

        A series of function to interact with the text document

    3) Client/Server API

        A series of function to interacts with the pyqode server (start, stop,
        requests)

    4) Text decorations API

        Classes and function to easily add decoration to the qcodeedit.


    5) Syntax highlighter API

        The syntax highlighter base class and all the related classes (folding,
        symbol matcher,...)

"""
import sys
import weakref
from PyQt4 import QtGui, QtCore
from pyqode.core import logger
from pyqode.core import settings


# ----------------
# Modes and panels
# ----------------
class Mode(object):
    """
    Base class for qcodeedit extensions. An extension is a "thing" that can be
    installed on a QCodeEdit to add new behaviours or to modify the
    appearance.

    A mode is added to a QCodeEdit by using the
    :meth:`pyqode.core.QCodeEdit.installMode` or
    :meth:`pyqode.core.QCodeEdit.installPanel` methods.

    Subclasses must/should override the following methods:
        - :meth:`pyqode.core.Mode._on_state_changed`
        - :meth:`pyqode.core.Mode.refresh_style`
        - :meth:`pyqode.core.Mode.refresh_settings`

    The mode will be identified by its class name, this means that there cannot
    be two modes of the same type on a QCodeEdit (you have to subclass it)
    """
    @property
    def qcodeedit(self):
        """
        Provides easy access to the parent qcodeedit widget (weakref)

        **READ ONLY**

        :type: pyqode.core.qcodeedit.QCodeEdit
        """
        if self._qcodeedit is not None:
            return self._qcodeedit()
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
        self.name = self.__class__.__name__
        #: Mode description
        self.description = self.__doc__
        self._enabled = False
        self._qcodeedit = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def _on_install(self, qcodeedit):
        """
        Installs the extension on the editor. Subclasses might want to override
        this method to add new style/settings properties to the editor.

        .. note:: This method is called by QCodeEdit when you install a Mode.
                  You should never call it yourself, even in a subclass.

        .. warning:: Don't forget to call **super** when subclassing

        :param qcodeedit: qcodeedit widget instance
        :type qcodeedit: pyqode.core.QCodeEdit
        """
        self._qcodeedit = weakref.ref(qcodeedit)
        self.enabled = True

    def _on_uninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self._qcodeedit = None

    def _on_state_changed(self, state):
        """
        Called when the enable state changed.

        This method does not do anything, you may override it if you need
        to connect/disconnect to the qcodeedit's signals (connect when state is
        true and disconnect when it is false).

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        pass

    def refresh_style(self):
        """
        Called by QCodeEdit when the user wants to refresh style options.
        """
        pass

    def refresh_settings(self):
        """
        Called by QCodeEdit when the user wants to refresh settings.
        """
        pass


def install_mode(qcodeedit, mode):
    """
    Installs a mode on the qcodeedit.

    :param qcodeedit: QCodeEdit instance on which the mode will be installed.
    :param mode: The mode instance to install.
    :type mode: pyqode.core.api.Mode
    """
    logger.debug('installing mode %s' % mode)
    qcodeedit._modes[mode.name] = mode
    mode._on_install(qcodeedit)


def uninstall_mode(qcodeedit, name):
    """
    Uninstalls a previously installed mode.

    :param name: The name of the mode to uninstall.
    """
    logger.debug('Uninstalling mode %s' % name)
    m = qcodeedit.get_mode(name)
    if m:
        m._on_uninstall()
        return qcodeedit._modes.pop(name, None)


def get_mode(qcodeedit, name_or_klass):
    """
    Gets a mode by name.

    :param name_or_klass: The name or the class of the mode to get
    :type name_or_klass: str or type
    :rtype: pyqode.core.api.Mode
    """
    if not isinstance(name_or_klass, str):
        name_or_klass = name_or_klass.__name__
    return qcodeedit._modes[name_or_klass]


def get_modes(qcodeedit):
    """
    Returns the dictionary of modes.
    """
    return qcodeedit._modes


class Panel(QtGui.QWidget, Mode):
    """
    Base class for qcodeedit panels.

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

    def _on_install(self, qcodeedit):
        """
        Extends :meth:`pyqode.core.Mode._onInstall` method to set the qcodeedit
        instance as the parent widget.

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param qcodeedit: qcodeedit instance
        :type qcodeedit: pyqode.core.code_edit.QCodeEdit
        """
        Mode._on_install(self, qcodeedit)
        self.setParent(qcodeedit)
        self.qcodeedit.refresh_panels()
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
        if not self.qcodeedit.isVisible():
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
        self.qcodeedit.refresh_panels()

    def setVisible(self, visible):
        QtGui.QWidget.setVisible(self, visible)
        self.qcodeedit.refresh_panels()


def install_panel(qcodeedit, panel, position=Panel.Position.LEFT):
    """
    Installs a panel on on the qcodeedit. You must specify the position of the
    panel (panels are rendered in one of the four document margins, see
    :class:`pyqode.core.qcodeedit.Panel.Position`.

    The panel is set as an object attribute using the panel's name as the
    key.

    :param panel: The panel instance to install
    :param position: The panel position

    :type panel: pyqode.core.api.Panel
    :type position: int
    """
    panel.order_in_zone = len(qcodeedit._panels[position])
    qcodeedit._panels[position][panel.name] = panel
    panel._on_install(qcodeedit)
    qcodeedit._update_viewport_margins()


def uninstall_panel(qcodeedit, name):
    """
    Uninstalls a previously installed panel.

    :param name: The name of the panel to uninstall

    :return: The uninstalled mode instance
    """
    logger.debug('Uninstalling panel %s' % name)
    p, zone = get_panel(qcodeedit, name, get_zone=True)
    if p:
        p._on_uninstall()
        return qcodeedit._panels[zone].pop(name, None)


def get_panel(qcodeedit, name_or_klass, get_zone=False):
    """
    Gets a panel by name

    :param name_or_klass: Name or class of the panel to get
    :param get_zone: True to also return the zone in which the panel has
        been installed.
    """
    if not isinstance(name_or_klass, str):
        name_or_klass = name_or_klass.__name__
    for i in range(4):
        try:
            panel = qcodeedit._panels[i][name_or_klass]
        except KeyError:
            pass
        else:
            if get_zone:
                return panel, i
            else:
                return panel
    return None, -1


def get_panels(qcodeedit):
    """
    Returns the panels dictionary.

    :return: A dictionary of :class:`pyqode.core.Panel`
    :rtype: dict
    """
    return qcodeedit._panels


# ----------------
# Text cursor manipulations
# ----------------
def goto_line(qcodeedit, line, column=0, move=True):
    """
    Moves the text cursor to the specified line (and column).

    :param qcodeedit: QCodeEdit instance.
    :param line: Number of the line to go to (1 based)
    :param column: Optional column number. Default start of line.
    :param move: True to move the cursor. False will return the cursor
                 without setting it on the qcodeedit.
    :return: The new text cursor
    :rtype: QtGui.QTextCursor
    """
    tc = qcodeedit.textCursor()
    tc.movePosition(tc.Start, tc.MoveAnchor)
    tc.movePosition(tc.Down, tc.MoveAnchor, line - 1)
    if column:
        tc.movePosition(tc.Right, tc.MoveAnchor, column)
    if move:
        qcodeedit.setTextCursor(tc)
    return tc


def selected_text(qcodeedit):
    """
    Returns the selected text.

    :param qcodeedit: QCodeEdit instance.
    """
    return qcodeedit.textCursor().selectedText()


def word_under_cursor(qcodeedit, select_whole_word=False, tc=None):
    """
    Gets the word under cursor using the separators defined by
    :attr:`pyqode.core.settings.word_separators`.

    .. note: Instead of returning the word string, this function returns
        a QTextCursor, that way you may get more information than just the
        string. To get the word, just call ``selectedText`` on the return
        value.

    :param qcodeedit: QCodeEdit instance.
    :param select_whole_word: If set to true the whole word is selected,
     else the selection stops at the cursor position.
    :param tc: Optional custom text cursor (e.g. from a QTextDocument clone)
    :return The QTextCursor that contains the selected word.
    """
    if not tc:
        tc = qcodeedit.textCursor()
    word_separators = settings.word_separators
    end_pos = start_pos = tc.position()
    # select char by char until we are at the original cursor position.
    while not tc.atStart():
        tc.movePosition(tc.Left, tc.KeepAnchor, 1)
        try:
            ch = tc.selectedText()[0]
            word_separators = settings.word_separators
            st = tc.selectedText()
            if (st in word_separators and (st != "n" and st != "t")
                    or ch.isspace()):
                break  # start boundary found
        except IndexError:
            break  # nothing selectable
        start_pos = tc.position()
        tc.setPosition(start_pos)
    if select_whole_word:
        # select the resot of the word
        tc.setPosition(end_pos)
        while not tc.atEnd():
            tc.movePosition(tc.Right, tc.KeepAnchor, 1)
            ch = tc.selectedText()[0]
            st = tc.selectedText()
            if (st in word_separators and (st != "n" and st != "t")
                    or ch.isspace()):
                break  # end boundary found
            end_pos = tc.position()
            tc.setPosition(end_pos)
    # now that we habe the boundaries, we can select the text
    tc.setPosition(start_pos)
    tc.setPosition(end_pos, tc.KeepAnchor)
    return tc


def select_word_under_mouse_cursor(qcodeedit):
    """
    Selects the word under the **mouse** cursor.

    :return: A QTextCursor with the word under mouse cursor selected.
    """
    tc = qcodeedit.cursorForPosition(qcodeedit._last_mouse_pos)
    tc = word_under_cursor(qcodeedit, True, tc)
    return tc


def cursor_position(qcodeedit):
    """
    Returns the QTextCursor position. The position is a tuple made up of the
    line number (1 based) and the column number (0 based).

    :param qcodeedit: QCodeEdit instance
    :return: tuple(line, column)
    """
    return (qcodeedit.textCursor().blockNumber() + 1,
            qcodeedit.textCursor().columnNumber())


def cursor_line_nbr(qcodeedit):
    """
    Returns the text cursor's line number.

    :param qcodeedit: QCodeEdit instance

    :return: Line number
    """
    return cursor_position(qcodeedit)[0]


def cursor_column_nbr(qcodeedit):
    """
    Returns the text cursor's column number.

    :param qcodeedit: QCodeEdit instance

    :return: Column number
    """
    return cursor_position(qcodeedit)[1]


def line_count(qcodeedit):
    """
    Returns the line count of the specified qcodeedit

    :param qcodeedit: QCodeEdit instance
    :return: number of lines in the document.
    """
    return qcodeedit.document().blockCount()


def line_text(qcodeedit, line_nbr):
    """
    Gets the text of the specified line

    :param qcodeedit: QCodeEdit instance
    :param line_nbr: The line number of the text to get

    :return: Entire line's text
    :rtype: str
    """
    tc = qcodeedit.textCursor()
    tc.movePosition(tc.Start)
    tc.movePosition(tc.Down, tc.MoveAnchor, line_nbr - 1)
    tc.select(tc.LineUnderCursor)
    return tc.selectedText()


def current_line_text(qcodeedit):
    """
    Returns the text of the current line.

    :param qcodeedit: QCodeEdit instance

    :return: Text of the current line
    """
    return line_text(qcodeedit, cursor_line_nbr(qcodeedit))


def set_line_text(qcodeedit, line_nbr, new_text):
    """
    Replace an entire line with ``new_text``.

    :param qcodeedit: QCodeEdit instance
    :param new_text: The replacement text.

    """
    tc = qcodeedit.textCursor()
    tc.movePosition(tc.Start)
    tc.movePosition(tc.Down, tc.MoveAnchor, line_nbr - 1)
    tc.select(tc.LineUnderCursor)
    tc.insertText(new_text)
    qcodeedit.setTextCursor(tc)


def remove_last_line(qcodeedit):
    """
    Removes the last line of the document.
    """
    tc = qcodeedit.textCursor()
    tc.movePosition(tc.End, tc.MoveAnchor)
    tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
    tc.movePosition(tc.End, tc.KeepAnchor)
    tc.removeSelectedText()
    tc.deletePreviousChar()
    qcodeedit.setTextCursor(tc)


def clean_document(qcodeedit):
    """
    Removes trailing whitespaces and ensure one single blank line at the
    end of the QTextDocument.
    """
    value = qcodeedit.verticalScrollBar().value()
    pos = cursor_position(qcodeedit)

    qcodeedit.textCursor().beginEditBlock()

    # cleanup whitespaces
    qcodeedit._cleaning = True
    eaten = 0
    removed = set()
    for line in qcodeedit._modified_lines:
        for j in range(-1, 2):
            # skip current line
            if line + j != pos[0]:
                txt = line_text(qcodeedit, line + j)
                stxt = txt.rstrip()
                set_line_text(qcodeedit, line + j, stxt)
                removed.add(line + j)
    qcodeedit._modified_lines -= removed
    if line_text(qcodeedit, line_count(qcodeedit)):
        qcodeedit.appendPlainText("\n")
    else:
        # remove last blank line (except one)
        i = 0
        while line_count(qcodeedit) - i > 0:
            l = line_text(qcodeedit, line_count(qcodeedit) - i)
            if l:
                break
            i += 1
        for j in range(i - 1):
            remove_last_line(qcodeedit)

    qcodeedit._cleaning = False
    qcodeedit._original_text = qcodeedit.toPlainText()

    # restore cursor and scrollbars
    tc = qcodeedit.textCursor()
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
    qcodeedit.setTextCursor(tc)
    qcodeedit.verticalScrollBar().setValue(value)

    qcodeedit.textCursor().endEditBlock()


def select_lines(qcodeedit, start, end, apply_selection=True):
    """
    Select entire lines between start and end.

    This functions returned the text cursor that contains the selection.

    Optionally it is possible to prevent the selection from being applied on
    the code qcodeedit widget by setting ``apply_selection`` to False.

    :param qcodeedit: QCodeEdit instance.
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
        tc = qcodeedit.textCursor()
        tc.movePosition(tc.Start, tc.MoveAnchor)
        tc.movePosition(tc.Down, tc.MoveAnchor, start - 1)
        if end > start:  # Going down
            tc.movePosition(tc.Down, tc.KeepAnchor, end - start)
            tc.movePosition(tc.EndOfLine, tc.KeepAnchor)
        elif end < start:  # going up
            # don't miss end of line !
            tc.movePosition(tc.EndOfLine, tc.MoveAnchor)
            tc.movePosition(tc.Up, tc.KeepAnchor, start - end)
            tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
        else:
            tc.movePosition(tc.EndOfLine, tc.KeepAnchor)
        if apply_selection:
            qcodeedit.setTextCursor(tc)


def selection_range(qcodeedit):
    """
    Returns the selected lines boundaries (start line, end line)

    :return: tuple(int, int)
    """
    doc = qcodeedit.document()
    start = doc.findBlock(
        qcodeedit.textCursor().selectionStart()).blockNumber() + 1
    end = doc.findBlock(
        qcodeedit.textCursor().selectionEnd()).blockNumber() + 1
    tc = QtGui.QTextCursor(qcodeedit.textCursor())
    tc.setPosition(qcodeedit.textCursor().selectionEnd())
    if tc.columnNumber() == 0 and start != end:
        end -= 1
    return start, end


def line_pos_from_number(qcodeedit, line_number):
    """
    Gets the line pos on the Y-Axis (at the center of the line) from a
    line number (1 based).

    :param line_number: The line number for which we want to know the
                        position in pixels.

    :return: The center position of the line.
    :rtype: int or None
    """
    block = qcodeedit.document().findBlockByNumber(line_number)
    if block:
        return int(qcodeedit.blockBoundingGeometry(block).translated(
                   qcodeedit.contentOffset()).top())
    return None


def line_nbr_from_position(qcodeedit, y_pos):
    """
    Returns the line number from the y_pos

    :param y_pos: Y pos in the QCodeEdit

    :return: Line number (1 based)
    :rtype: int
    """
    height = qcodeedit.fontMetrics().height()
    for top, l, block in qcodeedit.visible_blocks:
        if top <= y_pos <= top + height:
            return l
    return None


# ----------------
# Client/Server api
# ----------------
class NotConnectedError(Exception):
    """
    Raised if the client is not connected to the server when an operation is
    requested.
    """
    def __init__(self):
        super(NotConnectedError, self).__init__(
            'Client socket not connected or server not started')


def start_server(qcodeedit, script, interpreter=sys.executable, args=None):
    """
    Starts a pyqode server, specific to a QCodeEdit instance.

    The server is a python script that starts a
    :class:`pyqode.core.server.JsonServer`. You (the user) must write
    the server script so that you can apply your own configuration
    server side.

    The script can be run with a custom interpreter. The default is to use
    sys.executable.

    :param: qcodeedit: QCodeEdit instance
    :param str script: Path to the server main script.
    :param str interpreter: The python interpreter to use to run the server
        script. If None, sys.executable is used unless we are in a frozen
        application (cx_Freeze). The executable is not used if the
        executable scripts ends with '.exe' on Windows
    :param list args: list of additional command line args to use to start
        the server process.
    """
    qcodeedit._client.start(script, interpreter=interpreter, args=args)


def stop_server(qcodeedit):
    """
    Stops the server process for a specific QCodeEdit and closes the
    associated client socket.

    You have to explicitly call this method when you're done with the qcodeedit
    widget, just before calling del on the widget.

    :param: qcodeedit: QCodeEdit instance
    """
    try:
        if qcodeedit._client:
            qcodeedit._client.close()
    except RuntimeError:
        pass


def request_work(qcodeedit, worker_class_or_function, args, on_receive=None):
    """
    Requests some work on the server process of a specific QCodeEdit instance.

    :param: qcodeedit: QCodeEdit instance
    :param worker_class_or_function: Worker class or function
    :param args: worker args, any Json serializable objects
    :param on_receive: an optional callback executed when we receive the
        worker's results. The callback will be called with two arguments:
        the status (bool) and the results (object)

    :raise: NotConnectedError if the server cannot be reached.

    """
    qcodeedit._client.request_work(worker_class_or_function, args,
                                   on_receive=on_receive)


def connected_to_server(qcodeedit):
    """
    Cheks if the client socket is connected to a server
    """
    return qcodeedit._client.is_connected


# ----------------
# Text decorations api
# ----------------
class TextDecorationSignals(QtCore.QObject):
    clicked = QtCore.pyqtSignal(object)


class TextDecoration(QtGui.QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration. The text decoration is an
    utility class that adds a few utility methods over the Qt ExtraSelection.

    In addition to the helper methods, a tooltip can be added to a decoration.
    Usefull for errors marks and so on...

    Text decoration expose 1 **clicked** signal stored in a separate QObject:
    :attr:`pyqode.core.TextDecoration.signals`

    .. code-block:: python

        deco = TextDecoration()
        deco.signals.clicked.connect(a_slot)

        def a_slot(decoration):
            print(decoration)
    """

    def __init__(self, cursor_or_bloc_or_doc, start_pos=None, end_pos=None,
                 start_line=None, end_line=None, draw_order=0, tooltip=None):
        """
        Creates a text decoration

        :param cursor_or_bloc_or_doc: Selection
        :type cursor_or_bloc_or_doc: QTextCursor or QTextBlock or QTextDocument

        :param start_pos: Selection start pos

        :param end_pos: Selection end pos

        .. note:: Use the cursor selection if startPos and endPos are none.
        """
        QtGui.QTextEdit.ExtraSelection.__init__(self)
        self.signals = TextDecorationSignals()
        self.draw_order = draw_order
        self.tooltip = tooltip
        cursor = QtGui.QTextCursor(cursor_or_bloc_or_doc)
        if start_pos is not None:
            cursor.setPosition(start_pos)
        if end_pos is not None:
            cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        if start_line is not None:
            cursor.movePosition(cursor.Start, cursor.MoveAnchor)
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, start_line - 1)
        if end_line is not None:
            cursor.movePosition(cursor.Down, cursor.KeepAnchor,
                                end_line - start_line)
        self.cursor = cursor

    def contains_cursor(self, cursor):
        """
        Checks if the textCursor is in the decoration

        :param cursor: The text cursor to test
        :type cursor: QtGui.QTextCursor
        """
        return self.cursor.selectionStart() <= cursor.position() < \
            self.cursor.selectionEnd()

    def set_as_bold(self):
        """ Uses bold text """
        self.format.setFontWeight(QtGui.QFont.Bold)

    def set_foreground(self, color):
        """ Sets the foreground color.
        :param color: Color
        :type color: QtGui.QColor
        """
        self.format.setForeground(color)

    def set_background(self, brush):
        """
        Sets the background brush.

        :param brush: Brush
        :type brush: QtGui.QBrush
        """
        self.format.setBackground(brush)

    def set_outline(self, color):
        """
        Uses an outline rectangle.

        :param color: Color of the outline rect
        :type color: QtGui.QColor
        """
        self.format.setProperty(QtGui.QTextFormat.OutlinePen,
                                QtGui.QPen(color))

    def set_full_width(self, flag=True, clear=True):
        """
        Sets full width selection.

        :param flag: True to use full width selection.
        :type flag: bool

        :param clear: True to clear any previous selection. Default is True.
        :type clear: bool
        """
        if clear:
            self.cursor.clearSelection()
        self.format.setProperty(QtGui.QTextFormat.FullWidthSelection, flag)

    def set_as_underlined(self, color=QtCore.Qt.blue):
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SingleUnderline)
        self.format.setUnderlineColor(color)

    def set_as_spell_check(self, color=QtCore.Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def set_as_error(self, color=QtCore.Qt.red):
        """ Highlights text as a syntax error.

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def set_as_warning(self, color=QtGui.QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: Underline color
        :type color: QtGui.QColor
        """
        self.format.setUnderlineStyle(
            QtGui.QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)
