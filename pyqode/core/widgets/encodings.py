import locale
from pyqode.core.api import ENCODINGS_MAP, convert_to_codec_key
from pyqode.core.qt import QtCore, QtWidgets
from pyqode.core.settings import Settings


class EncodingsComboBox(QtWidgets.QComboBox):
    """
    This combo box display the list of user preferred encoding.
    The last item let you choose an additional encoding from the list
    of encodings define in :mod:`pyqode.core.api.encodings` using
    the EncodingsEditorDialog.

    You can also set the current encoding, it will be automatically appended
    if not in the user list or set as the current index.
    """
    @property
    def current_encoding(self):
        return self._current_encoding

    @current_encoding.setter
    def current_encoding(self, value):
        self._current_encoding = convert_to_codec_key(value)
        self._refresh_items()

    def __init__(self, parent, default_encoding=locale.getpreferredencoding()):
        super().__init__(parent)
        self._current_encoding = default_encoding
        self._lock = False
        self._refresh_items()
        self.currentIndexChanged.connect(self._on_current_changed)

    def _on_current_changed(self, index):
        if self._lock:
            return
        if index == self.count() - 1:
            from pyqode.core.dialogs import DlgPreferredEncodingsEditor
            if DlgPreferredEncodingsEditor.edit_encodins(self):
                self._refresh_items()
        else:
            self._current_encoding = self.itemData(index, QtCore.Qt.UserRole)

    def _refresh_items(self):
        self._lock = True
        self.clear()
        for i, encoding in enumerate(sorted(Settings().preferred_encodings)
        ):
            encoding = convert_to_codec_key(encoding)
            try:
                alias, lang = ENCODINGS_MAP[encoding]
            except KeyError:
                print('KeyError with encoding:', encoding)
            else:
                self.addItem('%s (%s)' % (alias, lang))
                self.setItemData(i, encoding, QtCore.Qt.UserRole)
                if encoding == self._current_encoding:
                    self.setCurrentIndex(i)
        self.insertSeparator(self.count())
        self.addItem('Add or remove')
        self._lock = False
