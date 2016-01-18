from pyqode.core.widgets import FileSystemTreeView, FileSystemContextMenu
from pyqode.qt.QtTest import QTest


def test_fs_treeview():
    tv = FileSystemTreeView()
    tv.set_context_menu(FileSystemContextMenu())
    tv.set_root_path(__file__)
    tv.show()
    QTest.qWait(2000)
