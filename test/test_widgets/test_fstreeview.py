import os
from pyqode.core.widgets import FileSystemTreeView, FileSystemContextMenu


def test_fs_treeview():
    tv = FileSystemTreeView()
    tv.set_context_menu(FileSystemContextMenu())
    tv.set_root_path(__file__)
    tv.show()
