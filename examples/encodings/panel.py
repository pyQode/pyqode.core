"""
Show how decoding errors can be automatically handled using the EncodingPanel.
"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core import api, panels
from common import setup_editor, get_file_path

app = QtWidgets.QApplication(sys.argv)
editor = setup_editor(
    panels=[(panels.EncodingPanel(), api.Panel.Position.TOP)])
editor.file.open(get_file_path(), use_cached_encoding=False)
app.exec_()
