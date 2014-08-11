"""
This module tests the CodeEdit class
"""
import mimetypes
import os
import platform
import pytest

from pyqode.core.api.panel import Panel
from pyqode.core.api.utils import TextHelper
from pyqode.core import panels, modes

from pyqode.qt import QtWidgets, QtCore, QtGui
from pyqode.qt.QtTest import QTest



from test.helpers import log_test_name, preserve_style, preserve_settings, preserve_editor_config
from test.helpers import editor_open


foo = {}  # just there to cover code that matches '{' with '}'
original_text = None


@editor_open(__file__)
@log_test_name
def test_set_plain_text(editor):
    with pytest.raises(TypeError):
        editor.setPlainText('Some text')
    editor.setPlainText('Some text', mimetypes.guess_type('file.py')[0],
                        'utf-8')
    assert editor.toPlainText() == 'Some text'


@editor_open(__file__)
@log_test_name
def test_actions(editor):
    # 13 default shortcuts
    nb_actions_expected = 21  # 13 default actions + search panel actions + case converter,...
    assert len(editor.actions()) == nb_actions_expected
    action = QtWidgets.QAction('my_action', editor)
    editor.add_action(action)
    nb_actions_expected += 1
    assert len(editor.actions()) == nb_actions_expected
    editor.add_separator()
    nb_actions_expected += 1
    assert len(editor.actions()) == nb_actions_expected


@editor_open(__file__)
@log_test_name
def test_duplicate_line(editor):
    editor.duplicate_line()
    assert editor.toPlainText().startswith(get_first_line(editor) + '\n' +
                                           get_first_line(editor))
    editor.setPlainText('foo', '', 'utf-8')
    editor.duplicate_line()
    assert editor.toPlainText() == 'foo\nfoo'
    assert editor.textCursor().position() == 4


def test_bug_duplicate_line_undo_stack(editor):
    """
    See github issue #142 where the duplicate line messup the undo stack
    """
    editor.setPlainText('foo\nbar', '', 'utf-8')
    editor.textCursor().setPosition(0)
    editor.indent()
    editor.duplicate_line()
    editor.undo()
    assert editor.toPlainText() == '    foo\nbar'
    assert editor.textCursor().position() == 4


@editor_open(__file__)
@log_test_name
def test_show_tooltip(editor):
    editor.show_tooltip(QtCore.QPoint(0, 0), 'A tooltip')


@editor_open(__file__)
@preserve_editor_config
@log_test_name
def test_margin_size(editor):
    for panel in editor.panels:
        panel.enabled = False
        panel.hide()

    # we really need to show the window here to get correct margin size.
    editor.show()
    QTest.qWaitForWindowActive(editor)
    for position in Panel.Position.iterable():
        # there is no panel on this widget, all margin must be 0
        assert editor.panels.margin_size(position) == 0
    panel = panels.LineNumberPanel()
    editor.panels.append(panel, position=panel.Position.LEFT)
    panel.setVisible(True)
    QTest.qWait(300)
    # as the window is not visible, we need to refresh panels manually
    assert editor.panels.margin_size(Panel.Position.LEFT) != 0
    for panel in editor.panels:
        panel.enabled = True


@editor_open(__file__)
@preserve_style
@log_test_name
def test_zoom(editor):
    assert editor.font_size == 10
    editor.zoom_in()
    assert editor.font_size == 11
    editor.reset_zoom()
    assert editor.font_size == 10
    editor.zoom_out()
    assert editor.font_size == 9

    while editor.font_size > 1:
        editor.zoom_out()
        if editor.font_size == 1:
            editor.zoom_out()
            assert editor.font_size == 1


def get_first_line(editor):
    return editor.toPlainText().splitlines()[0]


@editor_open(__file__)
@log_test_name
def test_indent(editor):
    editor.modes.get(modes.IndenterMode).enabled = False
    TextHelper(editor).goto_line(1, move=True)
    first_line = get_first_line(editor)
    editor.indent()
    # no indenter mode -> indent should not do anything
    assert get_first_line(editor) == first_line
    editor.un_indent()
    assert get_first_line(editor) == first_line
    # append indenter mode, call to indent/un_indent should now work
    editor.modes.get(modes.IndenterMode).enabled = True
    TextHelper(editor).goto_line(1)
    TextHelper(editor).goto_line(1)
    editor.indent()
    assert get_first_line(editor) == '    ' + first_line
    editor.un_indent()
    assert get_first_line(editor) == first_line


@editor_open(__file__)
@preserve_settings
@log_test_name
def test_whitespaces(editor):
    assert not editor.show_whitespaces
    editor.show_whitespaces = True
    assert editor.show_whitespaces


@editor_open(__file__)
@preserve_style
@log_test_name
def test_font_name(editor):
    system = platform.system().lower()
    assert editor.font_name == 'Source Code Pro'
    editor.font_name = 'deja vu sans'
    assert editor.font_name == 'deja vu sans'


@editor_open(__file__)
@preserve_style
@log_test_name
def test_font_size(editor):
    assert editor.font_size != 20
    editor.font_size = 20
    assert editor.font_size == 20


@editor_open(__file__)
@preserve_style
@log_test_name
def test_foreground(editor):
    assert editor.foreground.name()


@editor_open(__file__)
@preserve_style
@log_test_name
def test_whitespaces_foreground(editor):
    assert editor.whitespaces_foreground.name()
    editor.whitespaces_foreground = QtGui.QColor("#FF0000")
    assert editor.whitespaces_foreground.name() == QtGui.QColor(
        "#FF0000").name()


@editor_open(__file__)
@preserve_style
@log_test_name
def test_selection_background(editor):
    assert editor.selection_background.name()
    editor.selection_background = QtGui.QColor("#FF0000")
    assert editor.selection_background.name() == QtGui.QColor(
        "#FF0000").name()


@editor_open(__file__)
@preserve_style
@log_test_name
def test_selection_foreground(editor):
    assert editor.selection_foreground.name()
    editor.selection_foreground = QtGui.QColor("#FF0000")
    assert editor.selection_foreground.name() == QtGui.QColor(
        "#FF0000").name()


@editor_open(__file__)
@log_test_name
def test_file_attribs(editor):
    # cannot change path directly, use save/open
    with pytest.raises(AttributeError):
        editor.file.path = __file__
    assert editor.file.path == __file__
    assert editor.file.name in editor.file.path


@editor_open(__file__)
@log_test_name
def test_setPlainText(editor):
    editor.setPlainText('', 'text/x-python', 'utf-8')
    assert editor.toPlainText() == ''


@editor_open(__file__)
@log_test_name
def test_delete(editor):
    txt = editor.toPlainText()
    TextHelper(editor).select_lines(1, 1)
    editor.delete()
    assert txt != editor.toPlainText()


@editor_open(__file__)
@log_test_name
def test_rehighlight(editor):
    editor.rehighlight()


@editor_open(__file__)
@log_test_name
def test_key_pressed_event(editor):
    QTest.keyPress(editor, QtCore.Qt.Key_Tab)
    QTest.keyPress(editor, QtCore.Qt.Key_Backtab)
    QTest.keyPress(editor, QtCore.Qt.Key_Home)
    QTest.keyPress(editor, QtCore.Qt.Key_Return)


@editor_open(__file__)
@log_test_name
def test_key_released_event(editor):
    QTest.keyRelease(editor, QtCore.Qt.Key_Tab)


@editor_open(__file__)
@log_test_name
def test_focus_out(editor):
    editor.save_on_focus_out = True
    editor.dirty = True
    assert editor.dirty is True
    editor.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.FocusOut))


@editor_open(__file__)
@log_test_name
def test_mouse_events(editor):
    editor.mousePressEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseButtonPress, QtCore.QPoint(10, 10),
        QtCore.Qt.RightButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
    editor.mouseReleaseEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseButtonRelease, QtCore.QPoint(10, 10),
        QtCore.Qt.RightButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
    if os.environ['QT_API'].lower() == 'pyqt5':
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), editor.mapToGlobal(QtCore.QPoint(10, 10)),
            QtCore.QPoint(0, 1), QtCore.QPoint(0, 1), 1,
            QtCore.Qt.Vertical, QtCore.Qt.MidButton, QtCore.Qt.NoModifier))
    else:
        editor.wheelEvent(QtGui.QWheelEvent(
            QtCore.QPoint(10, 10), 1, QtCore.Qt.MidButton,
            QtCore.Qt.NoModifier))
    editor.mouseMoveEvent(QtGui.QMouseEvent(
        QtCore.QEvent.MouseMove, QtCore.QPoint(10, 10),
        QtCore.Qt.RightButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
    editor.verticalScrollBar().setValue(editor.verticalScrollBar().maximum()/2.0)


@log_test_name
@editor_open(__file__)
def test_show_context_menu(editor):
    assert isinstance(editor, QtWidgets.QPlainTextEdit)
    editor.customContextMenuRequested.emit(QtCore.QPoint(10, 10))
    editor._mnu.hide()


@editor_open(__file__)
@log_test_name
def test_multiple_panels(editor):
    # append a fourth panel on the top zone
    class SearchPanel(panels.SearchAndReplacePanel):
        pass

    class RightMarkerPanel(panels.MarkerPanel):
        pass

    p = SearchPanel()
    editor.panels.append(p, p.Position.TOP)
    p.show()
    editor.panels.append(RightMarkerPanel(), p.Position.TOP)


@log_test_name
def test_resize(editor):
    editor.resize(700, 500)
    QTest.qWait(1000)
    editor.resize(800, 600)
    QTest.qWait(1000)


@log_test_name
def test_unknown_mimetype(editor):
    editor.clear()
    editor.setPlainText('dd', 'xyzbqdhb', 'utf-8')


def accept_mbox():
    print('accept')
    widgets = QtWidgets.QApplication.instance().topLevelWidgets()
    for w in widgets:
        print(w)
        if isinstance(w, QtWidgets.QDialog):
            QTest.keyPress(w, QtCore.Qt.Key_Return)
            QTest.keyPress(w, QtCore.Qt.Key_Enter)
            QTest.keyPress(w, QtCore.Qt.Key_Space)


def reject_mbox():
    print('reject')
    widgets = QtWidgets.QApplication.instance().topLevelWidgets()
    for w in widgets:
        print(w)
        if isinstance(w, QtWidgets.QDialog):
            QTest.keyPress(w, QtCore.Qt.Key_Escape)


# @log_test_name
# def test_goto_line_dlg(editor):
#     QtCore.QTimer.singleShot(1500, accept_mbox)
#     editor.goto_line()
#     QTest.qWait(1000)
#     QtCore.QTimer.singleShot(1500, reject_mbox)
#     editor.goto_line()
#     QTest.qWait(1000)
