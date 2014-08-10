from pyqode.core.api import TextHelper, TextBlockHelper
from pyqode.qt import QtCore, QtWidgets, QtGui
from pyqode.qt.QtTest import QTest
from pyqode.core import panels
from test.helpers import editor_open, preserve_editor_config


def get_panel(editor):
    return editor.panels.get(panels.FoldingPanel)


def test_enabled(editor):
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


@preserve_editor_config
@editor_open('test/test_api/folding_cases/foo.py')
def test_mouse_move(editor):
    panel = get_panel(editor)
    panel.highlight_caret_scope = False
    nb_decos = len(editor.decorations)
    y_pos = TextHelper(editor).line_pos_from_number(9)
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos + 5))
    QTest.qWait(1000)
    assert len(editor.decorations) == 2 + nb_decos
    y_pos = TextHelper(editor).line_pos_from_number(15)
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos + 5))
    QTest.qWait(1000)
    assert len(editor.decorations) == 4 + nb_decos
    QTest.mouseMove(panel, QtCore.QPoint(0, 0))
    panel.leaveEvent(None)
    editor.setFocus(True)
    panel.highlight_caret_scope = True


def toggle_fold_trigger(editor, line, panel):
    y_pos = TextHelper(editor).line_pos_from_number(line) + 5
    QTest.mouseMove(panel, QtCore.QPoint(3, y_pos))
    QTest.qWait(1000)
    QTest.mousePress(panel, QtCore.Qt.RightButton, QtCore.Qt.NoModifier,
                     QtCore.QPoint(3, y_pos))
    QTest.qWait(1000)


@preserve_editor_config
@editor_open('test/test_api/folding_cases/foo.py')
def test_mouse_press(editor):
    panel = get_panel(editor)
    panel.highlight_caret_scope = False
    # fold child block
    toggle_fold_trigger(editor, 15, panel)
    block = editor.document().findBlockByNumber(14)
    assert TextBlockHelper.is_fold_trigger(block) is True
    assert TextBlockHelper.get_fold_trigger_state(block) is True
    block = block.next()
    while block.blockNumber() < 21:
        assert block.isVisible() is False
        block = block.next()
    # fold top level block
    toggle_fold_trigger(editor, 9, panel)
    block = editor.document().findBlockByNumber(8)
    assert TextBlockHelper.is_fold_trigger(block)
    block = block.next()
    while block.blockNumber() < 27:
        if block.blockNumber() == 14:
            assert TextBlockHelper.is_fold_trigger(block) is True
            assert TextBlockHelper.get_fold_trigger_state(block) is True
        assert block.isVisible() is False
        block = block.next()
    # unfold it top level block
    toggle_fold_trigger(editor, 9, panel)
    block = editor.document().findBlockByNumber(8)
    assert TextBlockHelper.is_fold_trigger(block)
    block = block.next()
    while block.blockNumber() < 27:
        if 14 < block.blockNumber() < 22:
            assert block.isVisible() is False
        else:
            assert block.isVisible() is True
        block = block.next()

    # cleanup
    QTest.mouseMove(panel, QtCore.QPoint(0, 0))
    panel.leaveEvent(None)
    editor.setFocus(True)
    panel.highlight_caret_scope = True


@preserve_editor_config
@editor_open('test/test_api/folding_cases/foo.py')
def test_collapse_all(editor):
    panel = get_panel(editor)
    QTest.qWait(1000)
    panel.collapse_all()
    QTest.qWait(1000)
    block = editor.document().firstBlock()
    while block.blockNumber() < editor.document().blockCount() - 1:
        blank_line = len(block.text().strip()) == 0
        if TextBlockHelper.get_fold_lvl(block) > 0:
            if not blank_line:
                assert block.isVisible() is False
        else:
            assert block.isVisible() is True
        if TextBlockHelper.is_fold_trigger(block):
            assert TextBlockHelper.get_fold_trigger_state(block) is True
        block = block.next()


@preserve_editor_config
@editor_open('test/test_api/folding_cases/foo.py')
def test_expand_all(editor):
    panel = get_panel(editor)
    QTest.qWait(1000)
    panel.collapse_all()
    QTest.qWait(1000)
    panel.expand_all()
    block = editor.document().firstBlock()
    while block.blockNumber() < editor.document().blockCount() - 1:
        assert block.isVisible()
        if TextBlockHelper.is_fold_trigger(block):
            assert TextBlockHelper.get_fold_trigger_state(block) is False
        block = block.next()
