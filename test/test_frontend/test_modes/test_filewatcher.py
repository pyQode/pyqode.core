import os
from PyQt4 import QtCore, QtGui
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
import datetime
from pyqode.core import frontend, settings
from pyqode.core.frontend import modes


editor = None
mode = modes.FileWatcherMode()


file_path = os.path.join(
    os.getcwd(), 'test', 'test_frontend', 'test_modes', 'file_to_watch.txt')


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    editor.setMinimumWidth(800)
    editor.setMinimumWidth(600)
    frontend.install_mode(editor, mode)
    with open(file_path, 'w') as f:
        f.write("test file initial")
    frontend.open_file(editor, file_path)
    editor.show()
    QTest.qWait(500)


def teardown_module():
    global editor
    del editor
    os.remove(file_path)


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_modif_accept_with_focus():
    with open(file_path, 'r') as f:
        with open(file_path, 'w') as f2:
            f2.write("test file %s" % datetime.datetime.now())
    editor.setFocus(True)
    QtCore.QTimer.singleShot(1500, accept_mbox)
    # wait for the message box to appear
    QTest.qWait(1000)


def test_modif_reject_with_focus():
    with open(file_path, 'r') as f:
        with open(file_path, 'w') as f2:
            f2.write("test file %s" % datetime.datetime.now())
    editor.setFocus(True)
    QtCore.QTimer.singleShot(1500, reject_mbox)
    # wait for the message box to appear
    QTest.qWait(1000)


def test_modif_without_focus():
    win = QtGui.QMainWindow()
    win.show()
    QTest.qWaitForWindowShown(win)
    with open(file_path, 'r') as f:
        with open(file_path, 'w') as f2:
            f2.write("test file %s" % datetime.datetime.now())
    QtCore.QTimer.singleShot(1500, accept_mbox)
    # wait for the filewatcher to detect the changed
    QTest.qWait(500)
    QtGui.QApplication.instance().setActiveWindow(editor)
    # wait for the message box to appear
    QTest.qWait(500)


def accept_mbox():
    widgets = QtGui.QApplication.instance().topLevelWidgets()
    for w in widgets:
        if isinstance(w, QtGui.QMessageBox):
            QTest.keyPress(w, QtCore.Qt.Key_Space)


def reject_mbox():
    widgets = QtGui.QApplication.instance().topLevelWidgets()
    for w in widgets:
        if isinstance(w, QtGui.QMessageBox):
            QTest.keyPress(w, QtCore.Qt.Key_Escape)


def test_modif_autoreload():
    mode.auto_reload = True
    with open(file_path, 'r') as f:
        with open(file_path, 'w') as f2:
            f2.write("test file %s" % datetime.datetime.now())
    QTest.qWait(1000)


def test_delete():
    os.remove(file_path)
    QTest.qWait(1000)
    with open(file_path, 'w') as f:
        f.write("test file initial")
    frontend.open_file(editor, file_path)


def test_none_filepath():
    p = editor.file_path
    editor.file_path = None
    mode._update_mtime()
    editor.file_path = p


def test_non_existing_file_path():
    p = editor.file_path
    editor.file_path = '/usr/blah/foo/bar.txt'
    mode._update_mtime()
    editor.file_path = p
