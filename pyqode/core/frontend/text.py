import functools
import logging
import mimetypes
import os
import sys

from PyQt4 import QtCore, QtGui

from pyqode.core import settings
from pyqode.core.frontend.utils import show_wait_cursor


def _logger():
    return logging.getLogger(__name__)


def goto_line(editor, line, column=0, move=True):
    """
    Moves the text cursor to the specified line (and column).

    :param editor: editor instance.
    :param line: Number of the line to go to (1 based)
    :param column: Optional column number. Default start of line.
    :param move: True to move the cursor. False will return the cursor
                 without setting it on the editor.
    :return: The new text cursor
    :rtype: QtGui.QTextCursor
    """
    tc = editor.textCursor()
    tc.movePosition(tc.Start, tc.MoveAnchor)
    tc.movePosition(tc.Down, tc.MoveAnchor, line - 1)
    if column:
        tc.movePosition(tc.Right, tc.MoveAnchor, column)
    if move:
        editor.setTextCursor(tc)
    return tc


def selected_text(editor):
    """
    Returns the selected text.

    :param editor: editor instance.
    """
    return editor.textCursor().selectedText()


def word_under_cursor(editor, select_whole_word=False, tc=None):
    """
    Gets the word under cursor using the separators defined by
    :attr:`pyqode.core.settings.word_separators`.

    .. note: Instead of returning the word string, this function returns
        a QTextCursor, that way you may get more information than just the
        string. To get the word, just call ``selectedText`` on the return
        value.

    :param editor: editor instance.
    :param select_whole_word: If set to true the whole word is selected,
     else the selection stops at the cursor position.
    :param tc: Optional custom text cursor (e.g. from a QTextDocument clone)
    :return The QTextCursor that contains the selected word.
    """
    if not tc:
        tc = editor.textCursor()
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


def word_under_mouse_cursor(editor):
    """
    Selects the word under the **mouse** cursor.

    :return: A QTextCursor with the word under mouse cursor selected.
    """
    tc = editor.cursorForPosition(editor._last_mouse_pos)
    tc = word_under_cursor(editor, True, tc)
    return tc


def cursor_position(editor):
    """
    Returns the QTextCursor position. The position is a tuple made up of the
    line number (1 based) and the column number (0 based).

    :param editor: editor instance
    :return: tuple(line, column)
    """
    return (editor.textCursor().blockNumber() + 1,
            editor.textCursor().columnNumber())


def current_line_nbr(editor):
    """
    Returns the text cursor's line number.

    :param editor: editor instance

    :return: Line number
    """
    return cursor_position(editor)[0]


def current_column_nbr(editor):
    """
    Returns the text cursor's column number.

    :param editor: editor instance

    :return: Column number
    """
    return cursor_position(editor)[1]


def line_count(editor):
    """
    Returns the line count of the specified editor

    :param editor: editor instance
    :return: number of lines in the document.
    """
    return editor.document().blockCount()


def line_text(editor, line_nbr):
    """
    Gets the text of the specified line

    :param editor: editor instance
    :param line_nbr: The line number of the text to get

    :return: Entire line's text
    :rtype: str
    """
    doc = editor.document()
    block = doc.findBlockByNumber(line_nbr - 1)
    return block.text()


def current_line_text(editor):
    """
    Returns the text of the current line.

    :param editor: editor instance

    :return: Text of the current line
    """
    return line_text(editor, current_line_nbr(editor))


def set_line_text(editor, line_nbr, new_text):
    """
    Replace an entire line with ``new_text``.

    :param editor: editor instance
    :param new_text: The replacement text.

    """
    tc = editor.textCursor()
    tc.movePosition(tc.Start)
    tc.movePosition(tc.Down, tc.MoveAnchor, line_nbr - 1)
    tc.select(tc.LineUnderCursor)
    tc.insertText(new_text)
    editor.setTextCursor(tc)


def remove_last_line(editor):
    """
    Removes the last line of the document.
    """
    tc = editor.textCursor()
    tc.movePosition(tc.End, tc.MoveAnchor)
    tc.select(tc.LineUnderCursor)
    tc.removeSelectedText()
    tc.deletePreviousChar()
    editor.setTextCursor(tc)


def clean_document(editor):
    """
    Removes trailing whitespaces and ensure one single blank line at the
    end of the QTextDocument.
    """
    value = editor.verticalScrollBar().value()
    pos = cursor_position(editor)
    original_pos = editor.textCursor().position()

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
                    txt = line_text(editor, line + j)
                    stxt = txt.rstrip()
                    if txt != stxt:
                        set_line_text(editor, line + j, stxt)
                    removed.add(line + j)
    editor._modified_lines -= removed

    # ensure there is only one blank line left at the end of the file
    i = line_count(editor)
    while i:
        l = line_text(editor, i)
        if l.strip():
            break
        remove_last_line(editor)
        i -= 1
    if line_text(editor, line_count(editor)):
        editor.appendPlainText('')

    # restore cursor and scrollbars
    tc = editor.textCursor()
    doc = editor.document()
    assert isinstance(doc, QtGui.QTextDocument)
    tc.movePosition(tc.Start)
    tc.movePosition(tc.Down, tc.MoveAnchor,
                    pos[0] - 1 if pos[0] <= doc.blockCount() else
                    doc.blockCount() - 1)
    tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
    p = tc.position()
    tc.select(tc.LineUnderCursor)
    if tc.selectedText():
        tc.setPosition(p)
        offset = pos[1] - eaten
        tc.movePosition(tc.Right, tc.MoveAnchor, offset)
    else:
        tc.setPosition(p)
    editor.setTextCursor(tc)
    editor.verticalScrollBar().setValue(value)

    _logger().debug('FINISH editing blocks for cleaning')
    tc.endEditBlock()
    editor._cleaning = False


def select_lines(editor, start, end, apply_selection=True):
    """
    Selects entire lines between start and end line numbers.

    This functions apply the selection and returns the text cursor that
    contains the selection.

    Optionally it is possible to prevent the selection from being applied on
    the code editor widget by setting ``apply_selection`` to False.

    :param editor: editor instance.
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
        tc = editor.textCursor()
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
            editor.setTextCursor(tc)


def selection_range(editor):
    """
    Returns the selected lines boundaries (start line, end line)

    :return: tuple(int, int)
    """
    doc = editor.document()
    start = doc.findBlock(
        editor.textCursor().selectionStart()).blockNumber() + 1
    end = doc.findBlock(
        editor.textCursor().selectionEnd()).blockNumber() + 1
    tc = QtGui.QTextCursor(editor.textCursor())
    tc.setPosition(editor.textCursor().selectionEnd())
    if tc.columnNumber() == 0 and start != end:
        end -= 1
    return start, end


def line_pos_from_number(editor, line_number):
    """
    Gets the line pos on the Y-Axis (at the center of the line) from a
    line number (1 based).

    :param line_number: The line number for which we want to know the
                        position in pixels.

    :return: The center position of the line.
    :rtype: int or None
    """
    block = editor.document().findBlockByNumber(line_number)
    if block:
        return int(editor.blockBoundingGeometry(block).translated(
                   editor.contentOffset()).top())
    return None


def line_nbr_from_position(editor, y_pos):
    """
    Returns the line number from the y_pos

    :param y_pos: Y pos in the editor

    :return: Line number (1 based)
    :rtype: int
    """
    height = editor.fontMetrics().height()
    for top, l, block in editor.visible_blocks:
        if top <= y_pos <= top + height:
            return l
    return None


def keep_tc_pos(f):
    """
    Cache text cursor position and restore it when the wrapped
    function exits.

    This decorator can only be used on modes or panels.
    """
    @functools.wraps(f)
    def wrapper(editor, *args, **kwds):
        pos = editor.textCursor().position()
        retval = f(editor, *args, **kwds)
        tc = editor.textCursor()
        tc.setPosition(pos)
        editor.setTextCursor(tc)
        return retval
    return wrapper


def detect_encoding(path, default_encoding):
    """
    Detects the file encoding using chardet. If chardet is not available, the
    default system encoding is used instead.

    :param path: path of the file to detect encoding
    :param default_encoding: fallback encoding that is used in case we failed
        to detect the proper encoding.

    :returns: File encoding
    """
    _logger().debug('detecting file encoding for file: %s' % path)
    with open(path, 'rb') as f:
        data = f.read()
    try:
        import chardet
        encoding = chardet.detect(bytes(data))['encoding']
    except ImportError:
        _logger().warning("chardet not available, using default encoding by "
                          "default: %s" % default_encoding)
        encoding = default_encoding
    else:
        _logger().debug('encoding detected using chardet: %s' % encoding)
    return encoding


def get_mimetype(path):
    """
    Guesses the mime type of a file. If mime type cannot be detected, plain
    text is assumed.

    :param path: path of the file
    :return: the corresponding mime type.
    """
    _logger().debug('detecting mimetype for %s' % path)
    mimetype = mimetypes.guess_type(path)[0]
    if mimetype is None:
        mimetype = mimetypes.guess_type('file.txt')[0]
    _logger().debug('mimetype detected: %s' % mimetype)
    return mimetype


@show_wait_cursor
def open_file(editor, path, replace_tabs_by_spaces=True,
              detect_encoding_func=detect_encoding,
              default_encoding=sys.getfilesystemencoding()):
    """
    Opens a file on a CodeEdit instance.

    .. note:: This functions uses the :mod:`mimetypes` module to detect the
        file's mime type. You might need to add custom mime types using
        :meth:`mimetypes.add_type`.

        E.g., for cobol, you would need to the following::

            import mimetypes
            for ext in ['.cbl', '.CBL', '.cob', '.COB',
                        '.cpy', '.CPY', '.pco', '.PCO']:
                mimetypes.add_type('text/x-cobol', ext)

    :param editor: Editor instance
    :param path: path of the file to open
    :param replace_tabs_by_spaces: True to replace tabs by spaces, False to
        leave it as it is. Default is True.
    :param detect_encoding_func: Function to execute to detect encoding.
        Default is to detect encoding with chardet.
    :param default_encoding: Default encoding to use in case
        detect_encoding_func failed.
    """
    # detect encoding
    encoding = (detect_encoding_func(path, default_encoding)
                if detect_encoding_func else default_encoding)
    _logger().debug('file encoding: %s' % encoding)
    # open file and get its content
    with open(path, 'r', encoding=encoding) as f:
        content = f.read()
    # replace tabs by spaces
    if replace_tabs_by_spaces:
        content = content.replace(
            "\t", " " * settings.tab_length)
    # set plain text
    editor.file_path = path
    editor.setPlainText(content, get_mimetype(path), encoding)
    title = QtCore.QFileInfo(editor.file_path).fileName()
    editor.setDocumentTitle(title)
    editor.setWindowTitle(title)


@show_wait_cursor
def save_to_file(editor, path=None, encoding=None):
    """
    Saves the content of the editor to a file.

    :param editor: CodeEdit instance
    :param path: Path of the file to save
    :param encoding: Encoding of the file to save.

    """
    editor.text_saving.emit(path)
    sel_start = editor.textCursor().selectionStart()
    sel_end = editor.textCursor().selectionEnd()
    _logger().debug('cleaning document')
    clean_document(editor)
    _logger().debug('document cleaned')
    plain_text = editor.toPlainText()
    if path is None:
        if editor.file_path:
            path = editor.file_path
        else:
            _logger().debug('failed to save file. Path cannot be None if '
                            'editor.file_path is None')
            return False
    # change encoding ?
    if encoding:
        editor._fencoding = encoding
    # perform a safe save: we first save to a temporary file, if the save
    # succeeded we just rename it to the final file name.
    tmp_path = path + '~'
    try:
        _logger().debug('saving editor content to temp file: %s' % tmp_path)
        with open(tmp_path, 'w', encoding=editor.file_encoding) as f:
            f.write(plain_text)
    except (IOError, OSError):
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        _logger().exception('failed to save file: %s' % path)
        return False
    else:
        _logger().debug('save to temp file succeeded')
        # remove path and rename temp file
        _logger().debug('remove file: %s' % path)
        try:
            os.remove(path)
        except (OSError, IOError):
            pass
        _logger().debug('rename %s to %s' % (tmp_path, path))
        os.rename(tmp_path, path)
        editor._original_text = plain_text
        editor.dirty = False
        editor._fpath = path
        editor.text_saved.emit(path)
        if sel_start != sel_end:
            # reset selection
            tc = editor.textCursor()
            tc.setPosition(sel_start)
            tc.setPosition(sel_end, tc.KeepAnchor)
            editor.setTextCursor(tc)
        return True


def mark_whole_doc_dirty(editor):
    """
    Marks the whole document as dirty to force a full refresh. **SLOW**

    :param editor: CodeEdit instance
    """
    tc = editor.textCursor()
    tc.select(tc.Document)
    editor.document().markContentsDirty(tc.selectionStart(),
                                        tc.selectionEnd())


def line_indent(editor, line_nbr=None):
    """
    Returns the indent level of the specified line

    :param editor: CodeEdit instance
    :param line_nbr: Number of the line to get indentation (1 base). Pass None
        to use the current line number.
    :return: Number of spaces that makes the indentation level of the
             current line
    """
    if line_nbr is None:
        line_nbr = current_line_nbr(editor)
    line = line_text(editor, line_nbr)
    indentation = len(line) - len(line.lstrip())
    return indentation


def get_right_word(editor):
    """
    Gets the character on the right of the text cursor.

    :param editor: CodeEdit instance.
    :return: The word that is on the right of the text cursor.
    """
    tc = editor.textCursor()
    tc.movePosition(QtGui.QTextCursor.WordRight,
                    QtGui.QTextCursor.KeepAnchor)
    return tc.selectedText().strip()


def get_right_character(editor):
    """
    Gets the character that is on the right of the text cursor.

    :param editor: CodeEdit instance

    :return:
    """
    next_char = get_right_word(editor)
    if len(next_char):
        next_char = next_char[0]
    else:
        next_char = None
    return next_char


def insert_text(editor, text, keep_position=True):
    """
    Inserts text at the cursor position.

    :param editor: CodeEdit instance
    :param text: text to insert
    :param keep_position: Flag that specifies if the cursor position must be
        kept. Pass False for a regular insert (the cursor will be at the end
        of the inserted text).
    """
    tc = editor.textCursor()
    if keep_position:
        p = tc.position()
    tc.insertText(text)
    if keep_position:
        tc.setPosition(p)
    editor.setTextCursor(tc)


def clear_selection(editor):
    """
    Clears text cursor selection

    :param editor: CodeEdit instance
    """
    tc = editor.textCursor()
    tc.clearSelection()
    editor.setTextCursor(tc)


def move_right(editor, keep_anchor=False, nb_chars=1):
    """
    Moves the cursor on the right.

    :param editor: CodeEdit instance
    :param keep_anchor: True to keep anchor (to select text) or False to move
        the anchor (no selection)
    :param nb_chars: Number of characters to move.
    """
    tc = editor.textCursor()
    tc.movePosition(tc.Right, tc.KeepAnchor if keep_anchor else tc.MoveAnchor,
                    nb_chars)
    editor.setTextCursor(tc)


def selected_text_to_lower(editor):
    """
    Replaces the selected text by its lower version

    :param editor: CodeEdit instance
    """
    tc = editor.textCursor()
    tc.insertText(tc.selectedText().lower())
    editor.setTextCursor(tc)


def selected_text_to_upper(editor):
    """
    Replaces the selected text by its upper version

    :param editor: CodeEdit instance
    """
    txt = selected_text(editor)
    insert_text(editor, txt.upper())


def compare_cursors(cursor_a, cursor_b):
    """
    Compares two text cursor (take selection into account).

    :param cursor_a: First cursor to compare
    :param cursor_b: Second cursor to compare
    :return: True if the cursors are identical (same start and end pos)
    """
    return (cursor_b.selectionStart() >= cursor_a.selectionStart() and
            cursor_b.selectionEnd() <= cursor_a.selectionEnd())


def search_text(text_document, text_cursor, search_txt, search_flags):
    """
    Searches a text in a text document.

    :param text_document: QTextDocument
    :param text_cursor: Current text cursor
    :param search_txt: Text to search
    :param search_flags: QTextDocument.FindFlags
    :return: the list of occurences, the current occurence index
    :returns tuple([], int)
    """
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
    _logger().debug('search occurences: %r' % occurrences)
    _logger().debug('occurence index: %d' % index)
    return occurrences, index
