"""
This module contains the file helper implementation

"""
import locale
import logging
import mimetypes
import os
from pyqode.core.api.manager import Manager
from pyqode.core.api.utils import TextHelper
from pyqode.core.qt import QtCore, QtWidgets


def _logger():
    return logging.getLogger(__name__)


class FileManager(Manager):
    """
    Helps manage file operations:
        - open
        - save
        - provide icon
        - detect encoding
        - detect mimetype

    Example of usage::

        editor = CodeEdit()
        assert editor.file.path == ''
        editor.open(__file__)
        assert editor.file.path == __file__
        print(editor.file.encoding)

    """
    @property
    def path(self):
        """ Gets the file path """
        return self._path

    @property
    def name(self):
        """ Gets the file base name """
        return os.path.split(self.path)[1]

    @property
    def extension(self):
        """ Gets the file path """
        return os.path.splitext(self.path)[1]

    @property
    def dirname(self):
        """ Gets the file directory name """
        return os.path.dirname(self._path)

    @property
    def encoding(self):
        """ Gets the file encoding """
        return self._encoding

    @property
    def icon(self):
        """ Gets the file icon, provided by _get_icon """
        return self._get_icon()

    def _get_icon(self):
        return QtWidgets.QFileIconProvider().icon(QtCore.QFileInfo(self.path))

    def __init__(self, editor, replace_tabs_by_spaces=True):
        """
        :param editor: Code edit instance to work on.
        :param replace_tabs_by_spaces: True to replace tabs by spaces on
                                       load/save.
        """
        super().__init__(editor)
        self._path = ''
        self.mimetype = ''
        self._encoding = locale.getpreferredencoding()
        self.replace_tabs_by_spaces = replace_tabs_by_spaces

    def detect_encoding(self, path):
        """
        Detects file encoding

        :param path: file path
        :return: detected encoding
        """
        _logger().debug('detecting file encoding for file: %s', path)
        with open(path, 'rb') as file:
            data = file.read()
        try:
            import chardet
        except ImportError:
            encoding = locale.getpreferredencoding()
            _logger().warning("chardet not available, using default encoding: "
                              "%s", encoding)
        else:
            encoding = chardet.detect(data)['encoding']
            _logger().debug('encoding detected using chardet: %s', encoding)
        return encoding

    @staticmethod
    def get_mimetype(path):
        """
        Guesses the mime type of a file. If mime type cannot be detected, plain
        text is assumed.

        :param path: path of the file
        :return: the corresponding mime type.
        """
        _logger().debug('detecting mimetype for %s', path)
        mimetype = mimetypes.guess_type(path)[0]
        if mimetype is None:
            mimetype = mimetypes.guess_type('file.txt')[0]
        _logger().debug('mimetype detected: %s', mimetype)
        return mimetype

    def open(self, path):
        """
        Open a file and set its content on the editor widget.

        :param path: Path of the file to open.
        """
        self._encoding = self.detect_encoding(path)
        _logger().info('file encoding: %s', self.encoding)
        # open file and get its content
        with open(path, 'r', encoding=self.encoding) as file:
            content = file.read()
        # replace tabs by spaces
        if self.replace_tabs_by_spaces:
            content = content.replace("\t", " " * self.editor.tab_length)
        # set plain text
        self._path = path
        self.editor.setPlainText(
            content, self.get_mimetype(path), self.encoding)
        self.editor.setDocumentTitle(self.editor.file.name)
        self.editor.setWindowTitle(self.editor.file.name)

    def _save_tmp(self, plain_text, path):
        """
        Save the editor content to a temporary file.

        :param plain_text: text to save
        :param path: path of the file to save
        """
        _logger().debug('saving editor content to temp file: %s', path)
        # fallback to locale preferred encoding (happen for ascii files)
        for encoding in [self.encoding, locale.getpreferredencoding()]:
            try:
                with open(path, 'w', encoding=encoding) as file:
                    file.write(plain_text)
            except UnicodeEncodeError as e:
                if encoding == self.encoding:
                    _logger().exception(
                        'failed to save text with encoding %s', encoding)
                else:
                    raise e  # even preferred encoding didn't work
            else:
                _logger().info('text saved with encoding %s: %s', encoding, path)
                return True

    def _rm_tmp(self, tmp_path):
        _logger().debug('remove original file: %s', tmp_path)
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    def _reset_selection(self, sel_end, sel_start):
        text_cursor = self.editor.textCursor()
        text_cursor.setPosition(sel_start)
        text_cursor.setPosition(sel_end, text_cursor.KeepAnchor)
        self.editor.setTextCursor(text_cursor)

    def _get_selection(self):
        sel_start = self.editor.textCursor().selectionStart()
        sel_end = self.editor.textCursor().selectionEnd()
        return sel_end, sel_start

    def save(self, path=None, encoding=None):
        """
        Save the editor content to a file.

        :param path: optional file path. Set it to None to save using the current
                     path (save), set a new path to save as.
        :param encoding: optional encoding, will use the current
                         file encoding if None.

        """
        _logger().debug("saving %r to %r with %r encoding", self.path, path, encoding)
        if path is None:
            if self.path:
                path = self.path
            else:
                _logger().debug(
                    'failed to save file, path argument cannot be None if '
                    'FileManager.path is also None')
                return False
        # override encoding on demand
        if encoding is not None:
            self._encoding = encoding
        self.editor.text_saving.emit(path)
        sel_end, sel_start = self._get_selection()
        TextHelper(self.editor).clean_document()
        plain_text = self.editor.toPlainText()
        # perform a safe save: we first save to a temporary file, if the save
        # succeeded we just rename it to the final file name, then we remove
        # the temporary file.
        tmp_path = path + '~'
        status = False
        try:
            self._save_tmp(plain_text, tmp_path)
        except (IOError, OSError, UnicodeEncodeError) as e:
            self._rm_tmp(tmp_path)
            _logger().exception('failed to save file: %s', path)
        else:
            _logger().debug('save to temp file succeeded')
            # remove path and rename temp file
            _logger().debug('rename %s to %s', tmp_path, path)
            try:
                # needed on windows as we cannot rename an existing file
                os.remove(path)
            except OSError:
                # first save  (aka save as)
                pass
            os.rename(tmp_path, path)
            self._rm_tmp(tmp_path)
            # reset dirty flags
            self.editor._original_text = plain_text
            self.editor.dirty = False
            # remember path for next save
            self._path = path
            # reset selection
            if sel_start != sel_end:
                self._reset_selection(sel_end, sel_start)
            status = True
        self.editor.text_saved.emit(path)
        return status

    def close(self):
        """
        Close the file open in the editor:
            - clear editor content
            - reset file attributes to their default values

        """
        self.editor.clear()
        self._path = ''
        self.mimetype = ''
        self._encoding = locale.getpreferredencoding()
