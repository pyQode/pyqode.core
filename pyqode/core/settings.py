"""
This module contains a class to access the pyQode settings (QSettings).

QSettings are used to cache some specific settings.

At the moment, we use it to store the lists of encoding that appears in
the encoding menu (to not have a too big encoding menu, user can choose which
encoding should be display, offering a small compact menu with all
its favorite encodings). We also cache encoding used to save or load a
file so that we can reuse it automatically next time the user want to
open the same file.

In the future, we could use this cache some editor states (such as
the last cursor position for a specific file path, code completion history to
show the favorite completions first,...)

We do not store editor styles and settings here. Those kind of settings are
better handled at the application level.

"""
import json
import locale
from pyqode.qt import QtCore
from pyqode.core.api import encodings


class Settings:
    def __init__(self, suffix=''):
        self._settings = QtCore.QSettings('pyQode', 'pyqode.core%s' % suffix)

    def clear(self):
        self._settings.clear()

    @property
    def preferred_encodings(self):
        """
        The list of user defined encodings, for display in the encodings
        menu/combobox.

        """
        return json.loads(self._settings.value(
            'userDefinedEncodings', '["%s"]' % encodings.convert_to_codec_key(
                locale.getpreferredencoding())))

    @preferred_encodings.setter
    def preferred_encodings(self, value):
        lst = [encodings.convert_to_codec_key(v) for v in value]
        self._settings.setValue('userDefinedEncodings',
                                json.dumps(list(set(lst))))

    def get_file_encoding(self, file_path):
        """
        Gets an eventual cached encoding for file_path.

        Raises a KeyError if no encoding were cached for the specified file
        path.

        :param file_path: path of the file to look up
        :returns: The cached encoding.
        """
        try:
            map = json.loads(self._settings.value('cachedFileEncodings'))
        except TypeError:
            map = {}
        return map[file_path]

    def set_file_encoding(self, path, encoding):
        """
        Cache encoding for the specified file path.

        :param path: path of the file to cache
        :param encoding: encoding to cache
        """
        try:
            map = json.loads(self._settings.value('cachedFileEncodings'))
        except TypeError:
            map = {}
        map[path] = encoding
        self._settings.setValue('cachedFileEncodings', json.dumps(map))
