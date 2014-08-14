# -*- coding: utf-8 -*-
"""
Contains utility functions
"""
import functools
import logging
from pyqode.qt import QtCore, QtGui


def _logger():
    """ Returns module logger """
    return logging.getLogger(__name__)


class memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            if args in self.cache:
                return self.cache[args]
            else:
                value = self.func(*args)
                self.cache[args] = value
                return value
        except TypeError:
            return self.func(*args)

    def __repr__(self):
        """ Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)


def drift_color(base_color, factor=110):
    """
    Return color that is lighter or darker than the base color.

    If base_color.lightness is higher than 128, the returned color is darker
    otherwise is is lighter.

    :param base_color: The base color to drift from
    :return A lighter or darker color.
    """
    base_color = QtGui.QColor(base_color)
    if base_color.lightness() > 128:
        return base_color.darker(factor)
    else:
        if base_color == QtGui.QColor('#000000'):
            return drift_color(QtGui.QColor('#101010'), factor + 20)
        else:
            return base_color.lighter(factor + 10)


class TextStyle(object):
    """
    Helper class to define a text format. This class has methods to set the
    text style from a string and to easily be created from a string, making
    serialisation extremely easy.

    A text style is made up of a text color and a series of text attributes:

        - bold/nbold
        - italic/nitalic
        - underlined/nunderlined.

    Example of usage::

        style = TextStyle('#808000 nbold nitalic nunderlined')
        print(style)  #should print '#808000 nbold nitalic nunderlined'

    """

    def __init__(self, style=None):
        """
        :param style: The style string ("#rrggbb [bold] [italic] [underlined])
        """
        self.color = QtGui.QColor()
        self.bold = False
        self.italic = False
        self.underlined = False
        if style:
            self.from_string(style)

    def __repr__(self):
        color = self.color.name()
        bold = "nbold"
        if self.bold:
            bold = "bold"
        italic = "nitalic"
        if self.italic:
            italic = "italic"
        underlined = "nunderlined"
        if self.underlined:
            underlined = "underlined"
        return " ".join([color, bold, italic, underlined])

    @memoized
    def from_string(self, string):
        """ Makes TextStyles from a string """
        tokens = string.split(" ")
        assert len(tokens) == 4
        self.color = QtGui.QColor(tokens[0])
        self.bold = False
        if tokens[1] == "bold":
            self.bold = True
        self.italic = False
        if tokens[2] == "italic":
            self.italic = True
        self.underlined = False
        if tokens[3] == "underlined":
            self.underlined = True


class DelayJobRunner(object):
    """
    Utility class for running job after a certain delay. If a new request is
    made during this delay, the previous request is dropped and the timer is
    restarted for the new request.

    We use this to implement a cooldown effect that prevents jobs from being
    executed while the IDE is not idle.

    A job is a simple callable.
    """
    def __init__(self, delay=500):
        """
        :param delay: Delay to wait before running the job. This delay applies
        to all requests and cannot be changed afterwards.
        """
        self._timer = QtCore.QTimer()
        self._interval = delay
        self._timer.timeout.connect(self._exec_requested_job)
        self._args = []
        self._kwargs = {}
        self._job = lambda x: None

    def request_job(self, job, *args, **kwargs):
        """
        Request a job execution. The job will be executed after the delay
        specified in the DelayJobRunner contructor elapsed if no other job is
        requested until then.

        :param job: job.
        :type job: callable

        :param force: Specify if we must force the job execution by stopping
                      the job that is currently running (if any).
        :type force: bool

        :param args: args
        :param kwargs: kwargs
        """
        self.cancel_requests()
        self._job = job
        self._args = args
        self._kwargs = kwargs
        self._timer.start(self._interval)

    def cancel_requests(self):
        """
        Cancels pending requests.
        """
        self._timer.stop()

    def _exec_requested_job(self):
        """
        Execute the requested job after the timer has timeout.
        """
        self._timer.stop()
        self._job(*self._args, **self._kwargs)


class TextHelper:
    """
    Text helper helps you manipulate the content of CodeEdit and extends the
    Qt text api for an easier usage.

    """
    def __init__(self, editor):
        """
        :param editor: The editor to work on.
        """
        self._editor = editor

    def goto_line(self, line, column=0, move=True):
        """
        Moves the text cursor to the specified line (and column).

        :param line: Number of the line to go to (1 based)
        :param column: Optional column number. Default start of line.
        :param move: True to move the cursor. False will return the cursor
                     without setting it on the editor.
        :return: The new text cursor
        :rtype: QtGui.QTextCursor
        """
        text_cursor = self._editor.textCursor()
        text_cursor.movePosition(text_cursor.Start, text_cursor.MoveAnchor)
        text_cursor.movePosition(text_cursor.Down, text_cursor.MoveAnchor,
                                 line - 1)
        if column:
            text_cursor.movePosition(text_cursor.Right, text_cursor.MoveAnchor,
                                     column)
        if move:
            self._editor.setTextCursor(text_cursor)
        return text_cursor

    def selected_text(self):
        """
        Returns the selected text.
        """
        return self._editor.textCursor().selectedText()

    def word_under_cursor(self, select_whole_word=False, text_cursor=None):
        """
        Gets the word under cursor using the separators defined by
        :attr:`pyqode.core.api.CodeEdit.word_separators`.

        .. note: Instead of returning the word string, this function returns
            a QTextCursor, that way you may get more information than just the
            string. To get the word, just call ``selectedText`` on the returned
            value.

        :param select_whole_word: If set to true the whole word is selected,
         else the selection stops at the cursor position.
        :param text_cursor: Optional custom text cursor (e.g. from a
            QTextDocument clone)
        :returns: The QTextCursor that contains the selected word.
        """
        editor = self._editor
        if not text_cursor:
            text_cursor = editor.textCursor()
        word_separators = editor.word_separators
        end_pos = start_pos = text_cursor.position()
        # select char by char until we are at the original cursor position.
        while not text_cursor.atStart():
            text_cursor.movePosition(
                text_cursor.Left, text_cursor.KeepAnchor, 1)
            try:
                char = text_cursor.selectedText()[0]
                word_separators = editor.word_separators
                selected_txt = text_cursor.selectedText()
                if (selected_txt in word_separators and
                        (selected_txt != "n" and selected_txt != "t")
                        or char.isspace()):
                    break  # start boundary found
            except IndexError:
                break  # nothing selectable
            start_pos = text_cursor.position()
            text_cursor.setPosition(start_pos)
        if select_whole_word:
            # select the resot of the word
            text_cursor.setPosition(end_pos)
            while not text_cursor.atEnd():
                text_cursor.movePosition(text_cursor.Right,
                                         text_cursor.KeepAnchor, 1)
                char = text_cursor.selectedText()[0]
                selected_txt = text_cursor.selectedText()
                if (selected_txt in word_separators and
                        (selected_txt != "n" and selected_txt != "t")
                        or char.isspace()):
                    break  # end boundary found
                end_pos = text_cursor.position()
                text_cursor.setPosition(end_pos)
        # now that we habe the boundaries, we can select the text
        text_cursor.setPosition(start_pos)
        text_cursor.setPosition(end_pos, text_cursor.KeepAnchor)
        return text_cursor

    def word_under_mouse_cursor(self):
        """
        Selects the word under the **mouse** cursor.

        :return: A QTextCursor with the word under mouse cursor selected.
        """
        editor = self._editor
        text_cursor = editor.cursorForPosition(editor._last_mouse_pos)
        text_cursor = self.word_under_cursor(True, text_cursor)
        return text_cursor

    def cursor_position(self):
        """
        Returns the QTextCursor position. The position is a tuple made up of
        the line number (1 based) and the column number (0 based).

        :return: tuple(line, column)
        """
        return (self._editor.textCursor().blockNumber() + 1,
                self._editor.textCursor().columnNumber())

    def current_line_nbr(self):
        """
        Returns the text cursor's line number.

        :return: Line number
        """
        return self.cursor_position()[0]

    def current_column_nbr(self):
        """
        Returns the text cursor's column number.

        :return: Column number
        """
        return self.cursor_position()[1]

    def line_count(self):
        """
        Returns the line count of the specified editor

        :return: number of lines in the document.
        """
        return self._editor.document().blockCount()

    def line_text(self, line_nbr):
        """
        Gets the text of the specified line

        :param line_nbr: The line number of the text to get

        :return: Entire line's text
        :rtype: str
        """
        doc = self._editor.document()
        block = doc.findBlockByNumber(line_nbr - 1)
        return block.text()

    def previous_line_text(self):
        if self.current_line_nbr() - 1:
            return self.line_text(self.current_line_nbr() - 1)
        return ''

    def current_line_text(self):
        """
        Returns the text of the current line.

        :return: Text of the current line
        """
        return self.line_text(self.current_line_nbr())

    def set_line_text(self, line_nbr, new_text):
        """
        Replace an entire line with ``new_text``.

        :param editor: editor instance
        :param new_text: The replacement text.

        """
        editor = self._editor
        text_cursor = editor.textCursor()
        text_cursor.movePosition(text_cursor.Start)
        text_cursor.movePosition(text_cursor.Down, text_cursor.MoveAnchor,
                                 line_nbr - 1)
        text_cursor.select(text_cursor.LineUnderCursor)
        text_cursor.insertText(new_text)
        editor.setTextCursor(text_cursor)

    def remove_last_line(self):
        """
        Removes the last line of the document.
        """
        editor = self._editor
        text_cursor = editor.textCursor()
        text_cursor.movePosition(text_cursor.End, text_cursor.MoveAnchor)
        text_cursor.select(text_cursor.LineUnderCursor)
        text_cursor.removeSelectedText()
        text_cursor.deletePreviousChar()
        editor.setTextCursor(text_cursor)

    def clean_document(self):
        """
        Removes trailing whitespaces and ensure one single blank line at the
        end of the QTextDocument.
        """
        editor = self._editor
        value = editor.verticalScrollBar().value()
        pos = self.cursor_position()
        _logger().debug('BEGIN edit blocks for cleaning  ')
        editor.textCursor().beginEditBlock()

        # cleanup whitespaces
        editor._cleaning = True
        eaten = 0
        removed = set()
        for line in editor._modified_lines:
            for j in range(-1, 2):
                # skip current line
                if line + j != pos[0]:
                    if line + j >= 1:
                        txt = self.line_text(line + j)
                        stxt = txt.rstrip()
                        if txt != stxt:
                            self.set_line_text(line + j, stxt)
                        removed.add(line + j)
        editor._modified_lines -= removed

        # ensure there is only one blank line left at the end of the file
        i = self.line_count()
        while i:
            line = self.line_text(i)
            if line.strip():
                break
            self.remove_last_line()
            i -= 1
        if self.line_text(self.line_count()):
            editor.appendPlainText('')

        # restore cursor and scrollbars
        text_cursor = editor.textCursor()
        doc = editor.document()
        assert isinstance(doc, QtGui.QTextDocument)
        text_cursor.movePosition(text_cursor.Start)
        text_cursor.movePosition(
            text_cursor.Down, text_cursor.MoveAnchor,
            pos[0] - 1 if pos[0] <= doc.blockCount() else doc.blockCount() - 1)
        text_cursor.movePosition(text_cursor.StartOfLine,
                                 text_cursor.MoveAnchor)
        cpos = text_cursor.position()
        text_cursor.select(text_cursor.LineUnderCursor)
        if text_cursor.selectedText():
            text_cursor.setPosition(cpos)
            offset = pos[1] - eaten
            text_cursor.movePosition(text_cursor.Right, text_cursor.MoveAnchor,
                                     offset)
        else:
            text_cursor.setPosition(cpos)
        editor.setTextCursor(text_cursor)
        editor.verticalScrollBar().setValue(value)

        _logger().debug('FINISH editing blocks for cleaning')
        text_cursor.endEditBlock()
        editor._cleaning = False

    def select_lines(self, start=1, end=-1, apply_selection=True):
        """
        Selects entire lines between start and end line numbers.

        This functions apply the selection and returns the text cursor that
        contains the selection.

        Optionally it is possible to prevent the selection from being applied
        on the code editor widget by setting ``apply_selection`` to False.

        :param start: Start line number (1 based)
        :param end: End line number (1 based). Use -1 to select up to the
            end of the document
        :param apply_selection: True to apply the selection before returning
         the QTextCursor.
        :returns: A QTextCursor that holds the requested selection
        """
        editor = self._editor
        if end == -1:
            end = self.line_count()
        if start and end:
            text_cursor = editor.textCursor()
            text_cursor.movePosition(text_cursor.Start, text_cursor.MoveAnchor)
            text_cursor.movePosition(text_cursor.Down, text_cursor.MoveAnchor,
                                     start - 1)
            if end > start:  # Going down
                text_cursor.movePosition(text_cursor.Down,
                                         text_cursor.KeepAnchor, end - start)
                text_cursor.movePosition(text_cursor.EndOfLine,
                                         text_cursor.KeepAnchor)
            elif end < start:  # going up
                # don't miss end of line !
                text_cursor.movePosition(text_cursor.EndOfLine,
                                         text_cursor.MoveAnchor)
                text_cursor.movePosition(text_cursor.Up,
                                         text_cursor.KeepAnchor, start - end)
                text_cursor.movePosition(text_cursor.StartOfLine,
                                         text_cursor.KeepAnchor)
            else:
                text_cursor.movePosition(text_cursor.EndOfLine,
                                         text_cursor.KeepAnchor)
            if apply_selection:
                editor.setTextCursor(text_cursor)
            return text_cursor
        return None

    def selection_range(self):
        """
        Returns the selected lines boundaries (start line, end line)

        :return: tuple(int, int)
        """
        editor = self._editor
        doc = editor.document()
        start = doc.findBlock(
            editor.textCursor().selectionStart()).blockNumber() + 1
        end = doc.findBlock(
            editor.textCursor().selectionEnd()).blockNumber() + 1
        text_cursor = QtGui.QTextCursor(editor.textCursor())
        text_cursor.setPosition(editor.textCursor().selectionEnd())
        if text_cursor.columnNumber() == 0 and start != end:
            end -= 1
        return start, end

    def line_pos_from_number(self, line_number):
        """
        Computes line position on Y-Axis (at the center of the line) from line
        number.

        :param line_number: The line number for which we want to know the
                            position in pixels.
        :return: The center position of the line.
        """
        editor = self._editor
        block = editor.document().findBlockByNumber(line_number - 1)
        if block.isValid():
            return int(editor.blockBoundingGeometry(block).translated(
                editor.contentOffset()).top())
        if line_number <= 0:
            return 0
        else:
            return int(editor.blockBoundingGeometry(
                block.previous()).translated(editor.contentOffset()).bottom())

    def line_nbr_from_position(self, y_pos):
        """
        Returns the line number from the y_pos

        :param y_pos: Y pos in the editor
        :return: Line number (1 based)
        """
        editor = self._editor
        height = editor.fontMetrics().height()
        for top, line, block in editor.visible_blocks:
            if top <= y_pos <= top + height:
                return line
        return None

    def mark_whole_doc_dirty(self):
        """
        Marks the whole document as dirty to force a full refresh. **SLOW**
        """
        text_cursor = self._editor.textCursor()
        text_cursor.select(text_cursor.Document)
        self._editor.document().markContentsDirty(text_cursor.selectionStart(),
                                                  text_cursor.selectionEnd())

    def line_indent(self, line_nbr=None):
        """
        Returns the indent level of the specified line

        :param line_nbr: Number of the line to get indentation (1 base).
            Pass None to use the current line number. Note that you can also
            pass a QTextBlock instance instead of an int.
        :return: Number of spaces that makes the indentation level of the
                 current line
        """
        editor = self._editor
        if line_nbr is None:
            line_nbr = self.current_line_nbr()
        elif isinstance(line_nbr, QtGui.QTextBlock):
            line_nbr = line_nbr.blockNumber() + 1
        line = self.line_text(line_nbr)
        indentation = len(line) - len(line.lstrip())
        return indentation

    def get_right_word(self):
        """
        Gets the character on the right of the text cursor.

        :return: The word that is on the right of the text cursor.
        """
        text_cursor = self._editor.textCursor()
        text_cursor.movePosition(QtGui.QTextCursor.WordRight,
                                 QtGui.QTextCursor.KeepAnchor)
        return text_cursor.selectedText().strip()

    def get_right_character(self):
        """
        Gets the character that is on the right of the text cursor.

        """
        next_char = self.get_right_word()
        if len(next_char):
            next_char = next_char[0]
        else:
            next_char = None
        return next_char

    def insert_text(self, text, keep_position=True):
        """
        Inserts text at the cursor position.

        :param text: text to insert
        :param keep_position: Flag that specifies if the cursor position must
            be kept. Pass False for a regular insert (the cursor will be at
            the end of the inserted text).
        """
        text_cursor = self._editor.textCursor()
        if keep_position:
            pos = text_cursor.position()
        text_cursor.insertText(text)
        if keep_position:
            text_cursor.setPosition(pos)
        self._editor.setTextCursor(text_cursor)

    def clear_selection(self):
        """
        Clears text cursor selection

        """
        text_cursor = self._editor.textCursor()
        text_cursor.clearSelection()
        self._editor.setTextCursor(text_cursor)

    def move_right(self, keep_anchor=False, nb_chars=1):
        """
        Moves the cursor on the right.

        :param keep_anchor: True to keep anchor (to select text) or False to
            move the anchor (no selection)
        :param nb_chars: Number of characters to move.
        """
        text_cursor = self._editor.textCursor()
        text_cursor.movePosition(
            text_cursor.Right, text_cursor.KeepAnchor if keep_anchor else
            text_cursor.MoveAnchor, nb_chars)
        self._editor.setTextCursor(text_cursor)

    def selected_text_to_lower(self):
        """
        Replaces the selected text by its lower version

        :param editor: CodeEdit instance
        """
        text_cursor = self._editor.textCursor()
        text_cursor.insertText(text_cursor.selectedText().lower())
        self._editor.setTextCursor(text_cursor)

    def selected_text_to_upper(self):
        """
        Replaces the selected text by its upper version

        """
        txt = self.selected_text()
        self.insert_text(txt.upper())

    def search_text(self, text_cursor, search_txt, search_flags):
        """
        Searches a text in a text document.

        :param text_cursor: Current text cursor
        :param search_txt: Text to search
        :param search_flags: QTextDocument.FindFlags
        :returns: the list of occurrences, the current occurrence index
        :rtype: tuple([], int)

        """
        def compare_cursors(cursor_a, cursor_b):
            return (cursor_b.selectionStart() >= cursor_a.selectionStart() and
                    cursor_b.selectionEnd() <= cursor_a.selectionEnd())

        text_document = self._editor.document()
        occurrences = []
        index = -1
        cursor = text_document.find(search_txt, 0, search_flags)
        original_cursor = text_cursor
        while not cursor.isNull():
            if compare_cursors(cursor, original_cursor):
                index = len(occurrences)
            occurrences.append((cursor.selectionStart(),
                                cursor.selectionEnd()))
            cursor.setPosition(cursor.position() + 1)
            cursor = text_document.find(search_txt, cursor, search_flags)
        _logger().debug('search occurences: %r', occurrences)
        _logger().debug('occurence index: %d', index)
        return occurrences, index

    def is_comment_or_string(self, cursor_or_block, formats=None):
        if formats is None:
            formats = ["comment", "string", "docstring"]
        layout = None
        pos = 0
        if isinstance(cursor_or_block, QtGui.QTextBlock):
            pos = len(cursor_or_block.text()) - 1
            layout = cursor_or_block.layout()
        elif isinstance(cursor_or_block, QtGui.QTextCursor):
            b = cursor_or_block.block()
            pos = cursor_or_block.position() - b.position()
            layout = cursor_or_block.block().layout()
        if layout is not None:
            additional_formats = layout.additionalFormats()
            sh = self._editor.syntax_highlighter
            if sh:
                ref_formats = sh.color_scheme.formats
                for r in additional_formats:
                    if r.start <= pos < (r.start + r.length):
                        for fmt_type in formats:
                            is_user_obj = (r.format.objectType() ==
                                           r.format.UserObject)
                            if (ref_formats[fmt_type] == r.format and
                                    is_user_obj):
                                return True
        return False


class TextBlockHelper:
    """
    Helps retrieving the various part of the user state bitmask.

    This helper should be used to replace calls to
    ``QTextBlock.setUserState``/``QTextBlock.getUserState`` as well as
    ``QSyntaxHighlighter.setCurrentBlockState``/
    ``QSyntaxHighlighter.currentBlockState`` and
    ``QSyntaxHighlighter.previousBlockState``.

    The bitmask is made up of the following fields:

        - bit0 -> bit26: User state (for syntax highlighting)
        - bit26: fold trigger state
        - bit27-bit29: fold level (8 level max)
        - bit30: fold trigger flag

    """
    @staticmethod
    def get_state(block):
        """
        Gets the user state, generally used for syntax highlighting.
        :param block: block to access
        :return: The block state

        """
        if block is None:
            return -1
        state = block.userState()
        if state == -1:
            return state
        return state & 0x03FFFFFF

    @staticmethod
    def set_state(block, state):
        """
        Sets the user state, generally used for syntax highlighting.

        :param block: block to modify
        :param state: new state value.
        :return:
        """
        if block is None:
            return
        user_state = block.userState()
        if user_state == -1:
            user_state = 0
        higher_part = user_state & 0xFC000000
        state &= 0x03FFFFFF
        state |= higher_part
        block.setUserState(state)

    @staticmethod
    def get_fold_lvl(block):
        """
        Gets the block fold level

        :param block: block to access.
        :returns: The block fold level
        """
        if block is None:
            return 0
        state = block.userState()
        if state == -1:
            state = 0
        return (state & 0x38000000) >> 27

    @staticmethod
    def set_fold_lvl(block, val):
        """
        Sets the block fold level.

        :param block: block to modify
        :param val: The new fold level [0-7]
        """
        if block is None:
            return
        state = block.userState()
        if state == -1:
            state = 0
        if val >= 8:
            val = 7
        state &= 0xC7FFFFFF
        state |= val << 27
        block.setUserState(state)

    @staticmethod
    def is_fold_trigger(block):
        """
        Checks if the block is a fold trigger.

        :param block: block to check
        :return: True if the block is a fold trigger (represented as a node in
            the fold panel)
        """
        if block is None:
            return False
        state = block.userState()
        if state == -1:
            state = 0
        return bool(state & 0x40000000)

    @staticmethod
    def set_fold_trigger(block, val):
        if block is None:
            return
        state = block.userState()
        if state == -1:
            state = 0
        state &= 0xBFFFFFFF
        state |= int(val) << 30
        block.setUserState(state)

    @staticmethod
    def get_fold_trigger_state(block):
        """
        Gets the fold trigger state.
        :return: False for an open trigger, True for for closed trigger
        """
        if block is None:
            return False
        state = block.userState()
        if state == -1:
            state = 0
        return bool(state & 0x04000000)

    @staticmethod
    def set_fold_trigger_state(block, val):
        """
        Sets the fold trigger state.

        :param block: The block to modify
        :param val: The new trigger state (False = open, True = closed)
        """
        if block is None:
            return
        state = block.userState()
        if state == -1:
            state = 0
        state &= 0xFBFFFFFF
        state |= int(val) << 26
        block.setUserState(state)


class ParenthesisInfo(object):
    """
    Stores information about a parenthesis in a line of code.
    """
    def __init__(self, pos, char):
        #: Position of the parenthesis, expressed as a number of character
        self.position = pos
        #: The parenthesis character, one of "(", ")", "{", "}", "[", "]"
        self.character = char


def get_block_symbol_data(editor, block):
    """
    Gets the list of ParenthesisInfo for specific text block.
    """
    def list_symbols(editor, block, character):
        text = block.text()
        symbols = []
        cursor = QtGui.QTextCursor(block)
        cursor.movePosition(cursor.StartOfBlock)
        pos = text.find(character, 0)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, pos)
        if TextHelper(editor).is_comment_or_string(cursor):
            # skips symbols in string literal or comment
            pos = -1
        while pos != -1:
            info = ParenthesisInfo(pos, character)
            symbols.append(info)
            pos = text.find(character, pos + 1)
            cursor.movePosition(cursor.StartOfBlock)
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, pos)
            if TextHelper(editor).is_comment_or_string(cursor):
                pos = -1
        return symbols

    parentheses = sorted(
        list_symbols(editor, block, '(') + list_symbols(editor, block, ')'),
        key=lambda x: x.position)
    square_brackets = sorted(
        list_symbols(editor, block, '[') + list_symbols(editor, block, ']'),
        key=lambda x: x.position)
    braces = sorted(
        list_symbols(editor, block, '{') + list_symbols(editor, block, '}'),
        key=lambda x: x.position)
    return parentheses, square_brackets, braces


def keep_tc_pos(func):
    """
    Cache text cursor position and restore it when the wrapped
    function exits.

    This decorator can only be used on modes or panels.
    """
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        """ Decorator """
        sb = editor.verticalScrollBar()
        spos = sb.sliderPosition()
        pos = editor.textCursor().position()
        retval = func(editor, *args, **kwds)
        text_cursor = editor.textCursor()
        text_cursor.setPosition(pos)
        editor.setTextCursor(text_cursor)
        sb.setSliderPosition(spos)
        return retval
    return wrapper
