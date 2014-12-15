"""
This example show you how to use the FileSystemTreeView (we show the
content of test_dir).
"""
import logging
import os
import sys
from pyqode.core.widgets import FileSystemTreeView, FileSystemContextMenu
from pyqode.qt import QtWidgets


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    def _on_tv_activated(index):
        print(tv.filePath(index))
        print(tv.fileInfo(index))

    app = QtWidgets.QApplication(sys.argv)
    tv = FileSystemTreeView()
    tv.set_context_menu(FileSystemContextMenu())
    tv.activated.connect(_on_tv_activated)
    path = os.path.join(os.getcwd(), 'test_dir')
    print('watching: %s' % path)
    tv.set_root_path(path)
    tv.show()
    app.exec_()
