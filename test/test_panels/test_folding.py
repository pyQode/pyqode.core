import os
import pytest
from pyqode.core.api import TextHelper, TextBlockHelper
from pyqode.qt import QtCore
from pyqode.qt.QtTest import QTest
from pyqode.core import panels
from test.helpers import editor_open, ensure_visible


def get_panel(editor):
    return editor.panels.get(panels.FoldingPanel)


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


# @ensure_visible
# @editor_open('test/test_api/folding_cases/foo.py')
# @pytest.mark.skipif('TRAVIS' not in os.environ,
#                     reason="tested only on travis")
# @pytest.mark.xfail
# def test_mouse_move(editor):
#     panel = get_panel(editor)
#     panel.highlight_caret_scope = False
#     nb_decos = len(editor.decorations)
#     y_pos = TextHelper(editor).line_pos_from_number(8)
#     QTest.mouseMove(panel, QtCore.QPoint(3, y_pos + 5))
#     QTest.qWait(1000)
#     assert len(editor.decorations) >= 2
#     y_pos = TextHelper(editor).line_pos_from_number(14)
#     QTest.mouseMove(panel, QtCore.QPoint(3, y_pos + 5))
#     QTest.qWait(1000)
#     assert len(editor.decorations) >= 4
#     QTest.mouseMove(panel, QtCore.QPoint(0, 0))
#     panel.leaveEvent(None)
#     editor.setFocus()
#     panel.highlight_caret_scope = True


# @ensure_visible
# def toggle_fold_trigger(editor, line, panel):
#     y_pos = TextHelper(editor).line_pos_from_number(line) + 5
#     QTest.mouseMove(panel, QtCore.QPoint(3, y_pos))
#     QTest.qWait(1000)
#     QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
#                      QtCore.QPoint(3, y_pos))
#     QTest.qWait(1000)


# @ensure_visible
# @editor_open('test/test_api/folding_cases/foo.py')
# @pytest.mark.skipif('TRAVIS' not in os.environ,
#                     reason="tested only on travis")
# @pytest.mark.xfail
# def test_mouse_press(editor):
#     panel = get_panel(editor)
#     panel.highlight_caret_scope = False
#     # fold child block
#     toggle_fold_trigger(editor, 15, panel)
#     block = editor.document().findBlockByNumber(14)
#     assert TextBlockHelper.is_fold_trigger(block) is True
#     assert TextBlockHelper.is_collapsed(block) is True
#     block = block.next()
#     while block.blockNumber() < 21:
#         assert block.isVisible() is False
#         block = block.next()
#     # fold top level block
#     toggle_fold_trigger(editor, 9, panel)
#     block = editor.document().findBlockByNumber(8)
#     assert TextBlockHelper.is_fold_trigger(block)
#     block = block.next()
#     while block.blockNumber() < 27:
#         if block.blockNumber() == 14:
#             assert TextBlockHelper.is_fold_trigger(block) is True
#             assert TextBlockHelper.is_collapsed(block) is True
#         assert block.isVisible() is False
#         block = block.next()
#     # unfold it top level block
#     toggle_fold_trigger(editor, 9, panel)
#     block = editor.document().findBlockByNumber(8)
#     assert TextBlockHelper.is_fold_trigger(block)
#     block = block.next()
#     while block.blockNumber() < 27:
#         assert block.isVisible() is True
#         block = block.next()

#     # cleanup
#     QTest.mouseMove(panel, QtCore.QPoint(0, 0))
#     panel.leaveEvent(None)
#     editor.setFocus()
#     panel.highlight_caret_scope = True


# @ensure_visible
# @editor_open('test/test_api/folding_cases/foo.py')
# @pytest.mark.skipif('TRAVIS' not in os.environ,
#                     reason="tested only on travis")
# @pytest.mark.xfail
# def test_collapse_all(editor):
#     panel = get_panel(editor)
#     QTest.qWait(1000)
#     panel.collapse_all()
#     QTest.qWait(1000)
#     block = editor.document().firstBlock()
#     while block.blockNumber() < editor.document().blockCount() - 1:
#         blank_line = len(block.text().strip()) == 0
#         if TextBlockHelper.get_fold_lvl(block) > 0:
#             if not blank_line:
#                 assert block.isVisible() is False
#         else:
#             assert block.isVisible() is True
#         if TextBlockHelper.is_fold_trigger(block):
#             assert TextBlockHelper.is_collapsed(block) is True
#         block = block.next()


# @ensure_visible
# @editor_open('test/test_api/folding_cases/foo.py')
# @pytest.mark.xfail
# def test_expand_all(editor):
#     panel = get_panel(editor)
#     QTest.qWait(1000)
#     panel.collapse_all()
#     QTest.qWait(1000)
#     panel.expand_all()
#     block = editor.document().firstBlock()
#     while block.blockNumber() < editor.document().blockCount() - 1:
#         assert block.isVisible()
#         if TextBlockHelper.is_fold_trigger(block):
#             assert TextBlockHelper.is_collapsed(block) is False
#         block = block.next()
