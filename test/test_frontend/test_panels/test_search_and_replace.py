from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import panels


editor = None
panel = panels.SearchAndReplacePanel()


def setup_module():
    global editor, panel
    editor = frontend.CodeEdit()
    frontend.install_panel(editor, panel, panel.Position.BOTTOM)
    editor.show()
    editor.setMinimumWidth(800)
    frontend.open_file(editor, __file__)
    QTest.qWait(1000)
    panel.checkBoxCase.setChecked(True)
    panel.checkBoxWholeWords.setChecked(True)


def teardown_module():
    global editor
    del editor


def test_enabled():
    global panel
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


def test_request_search():
    panel.request_search('import')
    QTest.qWait(1000)
    assert panel.cpt_occurences > 1


def test_action_search_triggered():
    # select word under cursor
    tc = frontend.word_under_mouse_cursor(editor)
    editor.setTextCursor(tc)
    panel.on_actionSearch_triggered()
    assert panel.isVisible()
    QTest.qWait(1000)


def test_action_search_triggered2():
    # second search with the same text
    tc = frontend.word_under_mouse_cursor(editor)
    editor.setTextCursor(tc)
    panel.on_actionSearch_triggered()
    assert panel.isVisible()
    QTest.qWait(1000)


def test_action_next():
    panel.request_search('import')
    for i in range(panel.cpt_occurences + 1):
        panel.select_next()
        QTest.qWait(100)


def test_action_previous():
    panel.request_search('import')
    for i in range(panel.cpt_occurences + 1):
        panel.select_previous()
        QTest.qWait(100)


def test_style():
    panel.request_search('import')
    QTest.qWait(1000)
    panel.background = QtGui.QColor('green')
    panel.foreground = QtGui.QColor('red')
    QTest.qWait(1000)


def test_close():
    panel.on_actionSearch_triggered()
    assert panel.isVisible()
    panel.on_pushButtonClose_clicked()
    assert not panel.isVisible()
    QTest.qWait(100)
    panel.on_actionSearch_triggered()


def test_focus_out_event():
    frontend.goto_line(editor, 1)
    tc = frontend.word_under_mouse_cursor(editor)
    editor.setTextCursor(tc)
    panel.on_actionSearch_triggered()
    panel.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.FocusOut))
    assert not panel.hasFocus()
    # reopen panel for next tests
    panel.on_actionSearch_triggered()
    panel.setFocus(True)


def test_replace():
    replacement_txt = 'REPLACEMENT_TEXT'
    panel.on_actionActionSearchAndReplace_triggered()
    panel.request_search('import')
    QTest.qWait(1000)
    panel.lineEditReplace.setText(replacement_txt)
    nb_occurences = panel.cpt_occurences
    QTest.qWait(1000)
    assert nb_occurences > 2
    panel.replace()
    assert panel.cpt_occurences == nb_occurences - 1
    panel.replace_all()
    assert panel.cpt_occurences == 0
    panel.request_search(replacement_txt)
    QTest.qWait(1000)
    assert panel.cpt_occurences == nb_occurences + 1


def test_event_filter():
    panel.on_actionActionSearchAndReplace_triggered()
    panel.request_search('import')
    QTest.qWait(1000)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Tab)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Return)
    QTest.keyPress(panel.lineEditReplace, QtCore.Qt.Key_Return)
    QTest.keyPress(panel.lineEditReplace, QtCore.Qt.Key_Return,
                   QtCore.Qt.ControlModifier)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Escape)
    assert not panel.isVisible()
