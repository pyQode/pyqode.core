import pytest
from pyqode.qt import QtCore, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core.api import TextHelper
from pyqode.core import panels
from test.helpers import editor_open, ensure_connected


def get_panel(editor):
    return editor.panels.get(panels.SearchAndReplacePanel)


@editor_open(__file__)
def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


@editor_open(__file__)
@ensure_connected
@pytest.mark.xfail
def test_request_search(editor):
    assert editor.backend.running
    panel = get_panel(editor)
    panel.request_search('import')
    QTest.qWait(2000)
    assert panel.cpt_occurences > 1


@editor_open(__file__)
@ensure_connected
def test_action_search_triggered(editor):
    panel = get_panel(editor)
    # select word under cursor
    tc = TextHelper(editor).word_under_mouse_cursor()
    editor.setTextCursor(tc)
    panel.on_search()
    editor.show()
    QTest.qWait(1000)
    assert panel.isVisible()
    panel.checkBoxCase.setChecked(True)
    panel.checkBoxWholeWords.setChecked(True)
    panel.on_search()
    assert panel.isVisible()
    QTest.qWait(1000)


@editor_open(__file__)
@ensure_connected
def test_action_search_triggered2(editor):
    panel = get_panel(editor)
    # second search with the same text
    tc = TextHelper(editor).word_under_mouse_cursor()
    editor.setTextCursor(tc)
    panel.on_search()
    editor.show()
    QTest.qWait(1000)
    assert panel.isVisible()


@editor_open(__file__)
@ensure_connected
def test_action_next(editor):
    panel = get_panel(editor)
    panel.request_search('import')
    for i in range(panel.cpt_occurences + 1):
        panel.select_next()
        QTest.qWait(100)


@editor_open(__file__)
@ensure_connected
def test_action_previous(editor):
    panel = get_panel(editor)
    panel.request_search('import')
    for i in range(panel.cpt_occurences + 1):
        panel.select_previous()
        QTest.qWait(100)


@editor_open(__file__)
@ensure_connected
def test_style(editor):
    panel = get_panel(editor)
    panel.request_search('import')
    QTest.qWait(1000)
    panel.background = QtGui.QColor('green')
    panel.foreground = QtGui.QColor('red')
    QTest.qWait(1000)


@editor_open(__file__)
@ensure_connected
def test_close(editor):
    panel = get_panel(editor)
    panel.on_search()
    editor.show()
    QTest.qWait(1000)
    assert panel.isVisible()
    panel.on_close()
    assert not panel.isVisible()
    QTest.qWait(100)
    panel.on_search()


@editor_open(__file__)
@ensure_connected
def test_focus_out_event(editor):
    panel = get_panel(editor)
    TextHelper(editor).goto_line(0)
    tc = TextHelper(editor).word_under_mouse_cursor()
    editor.setTextCursor(tc)
    panel.on_search()
    panel.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.FocusOut))
    assert not panel.hasFocus()
    # reopen panel for next tests
    panel.on_search()
    panel.setFocus()


@editor_open(__file__)
@ensure_connected
@pytest.mark.xfail
def test_replace(editor):
    panel = get_panel(editor)
    replacement_txt = 'REPLACEMENT_TEXT'
    panel.on_search_and_replace()
    panel.request_search('import')
    QTest.qWait(5000)
    panel.lineEditReplace.setText(replacement_txt)
    nb_occurences = panel.cpt_occurences
    QTest.qWait(5000)
    assert nb_occurences > 2
    panel.replace()
    assert panel.cpt_occurences == nb_occurences - 1
    panel.replace_all()
    assert panel.cpt_occurences == 0
    panel.request_search(replacement_txt)
    QTest.qWait(5000)
    assert panel.cpt_occurences == nb_occurences + 1


@editor_open(__file__)
@ensure_connected
def test_event_filter(editor):
    panel = get_panel(editor)
    panel.on_search_and_replace()
    panel.request_search('import')
    QTest.qWait(1000)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Tab)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Return)
    QTest.keyPress(panel.lineEditReplace, QtCore.Qt.Key_Return)
    QTest.keyPress(panel.lineEditReplace, QtCore.Qt.Key_Return,
                   QtCore.Qt.ControlModifier)
    QTest.keyPress(panel.lineEditSearch, QtCore.Qt.Key_Escape)
    editor.show()
    QTest.qWait(1000)
    assert not panel.isVisible()
