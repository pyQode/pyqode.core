from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes, panels


editor = None
panel = panels.MarkerPanel()


def setup_module():
    global editor, panel
    editor = frontend.CodeEdit()
    frontend.install_mode(editor, modes.PygmentsSyntaxHighlighter(
        editor.document()))
    frontend.install_panel(editor, panel, panel.Position.LEFT)
    editor.show()
    editor.setMinimumWidth(800)
    frontend.open_file(editor, __file__)
    QTest.qWait(1000)


def teardown_module():
    global editor
    del editor


def test_enabled():
    global panel
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


def test_marker_properties():
    m = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                      description='Marker description')
    assert m.icon == ':/pyqode-icons/rc/edit-undo.png'
    assert m.description == 'Marker description'
    assert m.position == 1


def test_add_marker():
    marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                           description='Marker description')
    panel.add_marker(marker)
    QTest.qWait(500)
    assert panel.marker_for_line(1) == marker


def test_clear_markers():
    marker = panels.Marker(
        2, icon=('edit-undo', ':/pyqode-icons/rc/edit-undo.png'),
        description='Marker description')
    panel.add_marker(marker)
    panel.clear_markers()


def test_make_marker_icon():
    # other tests already test icon from tuple or from string
    # we still need to test empty icons -> None
    assert panel.make_marker_icon(None) == (None, None)


def test_leave_event():
    panel.leaveEvent()


def test_mouse_press():
    panel.clear_markers()
    marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                           description='Marker description')
    panel.add_marker(marker)
    y_pos = frontend.line_pos_from_number(editor, 1)
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(1000, 1000))
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(3, y_pos))


def test_mouse_move():
    panel.clear_markers()
    marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                           description='Marker description')
    panel.add_marker(marker)
    y_pos = frontend.line_pos_from_number(editor, 1)
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos + 3))
    QTest.qWait(1000)
    QTest.mouseMove(panel, QtCore.QPoint(1000, 1000))