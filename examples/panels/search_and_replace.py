"""
Minimal example showing the use of the SearchAndReplacePanel.
"""
import logging
logging.basicConfig(level=logging.DEBUG)
import sys

from pyqode.qt import QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.backend import server
from pyqode.core.panels import SearchAndReplacePanel


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEdit()
    editor.backend.start(server.__file__)
    editor.resize(800, 600)
    editor.panels.append(SearchAndReplacePanel(),
                         SearchAndReplacePanel.Position.TOP)
    editor.setPlainText('Pres Ctrl+F to search text in the document', '', '')
    editor.show()
    app.exec_()
    editor.close()
    del editor
    del app
