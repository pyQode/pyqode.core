"""
This module tests the text api module (pyqode.core.text)
"""
import os
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
import sys

from pyqode.core.editor import QCodeEdit
from pyqode.core import client
from pyqode.core import text

from .helpers import cwd_at


app = None
editor = None
window = None


def process_events():
    global app
    app.processEvents()


@cwd_at('test')
def setup_module():
    """
    Setup a QApplication and QCodeEdit which open the client module code
    """
    print('setup')
    global app, editor, window
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = QCodeEdit(window)
    window.setCentralWidget(editor)
    editor.open_file(__file__)
    window.show()
    client.start_server(editor, os.path.join(os.getcwd(), 'server.py'))
    while not client.connected(editor):
        QTest.qWait(100)


def teardown_module():
    """
    Close server and exit QApplication
    """
    print('teardown')
    global editor, app
    client.stop_server(editor)
    app.exit(0)
    QTest.qWait(1000)
    del editor
    del app


def test_goto_line():
    global editor, window
    QTest.qWaitForWindowShown(window)
    assert editor.textCursor().blockNumber() == 0
    assert editor.textCursor().columnNumber() == 0
    cursor = text.goto_line(editor, 2, 0, move=False)
    process_events()
    assert editor.textCursor().blockNumber() != cursor.blockNumber()
    assert editor.textCursor().columnNumber() == cursor.columnNumber()
    cursor = text.goto_line(editor, 2, move=True)
    process_events()
    assert editor.textCursor().blockNumber() == cursor.blockNumber() == 1
    assert editor.textCursor().columnNumber() == cursor.columnNumber()


def test_selected_text():
    global editor
    print(editor.toPlainText())
    text.goto_line(editor, 2, 1, move=True)
    process_events()
    assert text.word_under_cursor(editor).selectedText() == 'T'
    assert text.word_under_cursor(
        editor, select_whole_word=True).selectedText() == 'This'
