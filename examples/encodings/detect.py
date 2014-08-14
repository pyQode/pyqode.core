"""
This example tries to detect the file encoding using chardet. You can install
chardet by running the following commmand::

    pip install chardet

.. note:: If you run this example without supplying a file argument, it will
    open a fallback file encoded with a chinese encoding. Chardet will not
    detect the right encoding but the file will load without any errors.

    I made this example to show you that you should not rely on a charset
    detector but instead provided a way for the user to reload the file with
    another encoding. This can be done using the EncodingMenu (in
    pyqode.core.widgets).

"""
import sys
from pyqode.qt import QtWidgets
from pyqode.core import api, panels, widgets
from common import setup_editor, get_file_path
import chardet

pth = get_file_path()
with open(pth, 'rb') as buf:
    encoding = chardet.detect(buf.read())['encoding']

app = QtWidgets.QApplication(sys.argv)
editor = setup_editor(
    panels=[(panels.EncodingPanel(), api.Panel.Position.TOP)])
editor.file.open(pth, encoding=encoding, use_cached_encoding=False)
app.exec_()
