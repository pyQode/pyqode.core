"""
Use context menu to reload the file with another encoding
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core import widgets
from common import setup_editor, get_file_path

app = QtWidgets.QApplication(sys.argv)
success = False
editor = setup_editor()
widgets.EncodingsContextMenu(parent=editor)
pth = get_file_path()
try:
    editor.file.open(pth, encoding='utf-8', use_cached_encoding=False)
except UnicodeDecodeError:
    QtWidgets.QMessageBox.warning(
        editor, 'Decoding error',
        'Failed to open file with utf-8, please use the reload button to '
        'reload the file with another encoding')
app.exec_()
