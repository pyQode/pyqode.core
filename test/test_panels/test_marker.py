from pyqode.core.api import TextHelper
from pyqode.qt import QtCore, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import panels
from test.helpers import editor_open
from test.helpers import ensure_visible


def get_panel(editor):
    return editor.panels.get(panels.MarkerPanel)


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


@ensure_visible
def test_marker_properties(editor):
    m = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                      description='Marker description')
    assert isinstance(m.icon, QtGui.QIcon)
    assert m.description == 'Marker description'
    assert m.position == 1


@ensure_visible
@editor_open(__file__)
def test_add_marker(editor):
    panel = get_panel(editor)
    marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
                           description='Marker description')
    panel.add_marker(marker)
#     QTest.qWait(500)
#     assert panel.marker_for_line(1)[0] is not None


# @ensure_visible
# @editor_open(__file__)
# def test_clear_markers(editor):
#     panel = get_panel(editor)
#     marker = panels.Marker(
#         2, icon=('edit-undo', ':/pyqode-icons/rc/edit-undo.png'),
#         description='Marker description')
#     panel.add_marker(marker)
#     panel.clear_markers()


# @editor_open(__file__)
# def test_leave_event(editor):
#     panel = get_panel(editor)
#     panel.leaveEvent()


# @editor_open(__file__)
# def test_mouse_press(editor):
#     panel = get_panel(editor)
#     panel.clear_markers()
#     marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
#                            description='Marker description')
#     panel.add_marker(marker)
#     y_pos = TextHelper(editor).line_pos_from_number(0)
#     QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
#                      QtCore.QPoint(1000, 1000))
#     QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
#                      QtCore.QPoint(3, y_pos))


# @editor_open(__file__)
# def test_mouse_move(editor):
#     panel = get_panel(editor)
#     panel.clear_markers()
#     marker = panels.Marker(1, icon=':/pyqode-icons/rc/edit-undo.png',
#                            description='Marker description')
#     panel.add_marker(marker)
#     y_pos = TextHelper(editor).line_pos_from_number(0)
#     QTest.mouseMove(panel, QtCore.QPoint(3, y_pos))
#     QTest.qWait(1000)
#     QTest.mouseMove(panel, QtCore.QPoint(1000, 1000))
