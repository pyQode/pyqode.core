"""
Show how decoding errors can be automatically handled using the EncodingPanel.
"""
import sys
from pyqode.core.qt import QtWidgets
from pyqode.core import api, panels
from common import setup_editor

app = QtWidgets.QApplication(sys.argv)
editor = setup_editor(
    panels=[(panels.EncodingPanel(), api.Panel.Position.TOP)])
app.exec_()
