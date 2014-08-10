"""
Use the encoding choice dialog to reload file in case of error.
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core import dialogs
from common import setup_editor, get_file_path

app = QtWidgets.QApplication(sys.argv)
success = False
editor = setup_editor()
pth = get_file_path()
success = False
encoding = 'utf-8'
while not success:
    try:
        editor.file.open(pth, encoding=encoding, use_cached_encoding=False)
    except UnicodeDecodeError:
        encoding = dialogs.DlgEncodingsChoice.choose_encoding(
            editor, pth, encoding)
    else:
        success = True
app.exec_()
