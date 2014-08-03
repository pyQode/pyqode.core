# -*- coding: utf-8 -*-
"""
This module contains the marker panel
"""
import logging
import os
import sys
from pyqode.core.api import TextBlockHelper, folding, TextDecoration
from pyqode.core.api.folding import FoldScope
from pyqode.core.api.panel import Panel
from pyqode.core.qt import QtCore, QtWidgets, QtGui
from pyqode.core.api.utils import TextHelper, drift_color


def _logger():
    """ Gets module's logger """
    return logging.getLogger(__name__)


class FoldingPanel(Panel):
    """
    Code folding panel display the document oultine and allow user to collapse
    or expand blocks of code.

    The data represented by the panel come from the text block user state and
    is set by the SyntaxHighlighter mode.

    The panel does not expose any function that you can use directly. To
    interact with the fold tree, you need to modify text block fold level or
    trigger state using :class:`pyqode.core.api.utils.TextBlockHelper` or
    :mod:`pyqode.core.api.folding`
    """
    #: Signal emitted when the user clicked in a place where there is no
    #: marker.
    add_marker_requested = QtCore.Signal(int)
    #: Signal emitted when the user clicked on an existing marker.
    remove_marker_requested = QtCore.Signal(int)

    def __init__(self):
        Panel.__init__(self)
        self._indic_size = 16
        #: the list of deco used to highlight the current fold region (
        #: surrounding regions are darker)
        self._scope_decos = []
        #: the list of folded blocs decorations
        self._block_decos = []
        self.setMouseTracking(True)
        self.scrollable = True
        self._mouse_over_line = None
        self._current_scope = None
        self._prev_cursor = None
        self.context_menu = None
        self.action_collapse = None
        self.action_expand = None
        self.action_collapse_all = None
        self.action_expand_all = None

    def on_install(self, editor):
        super().on_install(editor)
        self.context_menu = QtWidgets.QMenu('Folding', self.editor)
        action = self.action_collapse = QtWidgets.QAction(
            'Collapse', self.context_menu)
        action.triggered.connect(self._on_action_toggle)
        self.context_menu.addAction(action)
        action = self.action_expand = QtWidgets.QAction('Expand', self.context_menu)
        action.triggered.connect(self._on_action_toggle)
        self.context_menu.addAction(action)
        self.context_menu.addSeparator()
        action = self.action_collapse_all = QtWidgets.QAction(
            'Collapse all', self.context_menu)
        action.triggered.connect(self._on_action_collapse_all_triggered)
        self.context_menu.addAction(action)
        action = self.action_expand_all = QtWidgets.QAction(
            'Expand all', self.context_menu)
        action.triggered.connect(self._on_action_expand_all_triggered)
        self.context_menu.addAction(action)
        self.editor.add_menu(self.context_menu)

    def sizeHint(self):
        """ Returns the widget size hint (based on the editor font size) """
        fm = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(fm.height(), fm.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        # Draw background over the selected non collapsed fold region
        if self._mouse_over_line:
            block = self.editor.document().findBlockByNumber(
                self._mouse_over_line - 1)
            self._draw_fold_region_background(block, painter)
        # Draw fold triggers
        for top_position, line_number, block in self.editor.visible_blocks:
            if TextBlockHelper.is_fold_trigger(block):
                collapsed = TextBlockHelper.get_fold_trigger_state(block)
                mouse_over = self._mouse_over_line == line_number
                self._draw_fold_indicator(
                    top_position, mouse_over, collapsed, painter)

    def _draw_fold_region_background(self, block, painter):
        """
        Draw the fold region when the mouse is over and non collapsed
        indicator.

        :param top: Top position
        :param block: Current block.
        :param painter: QPainter
        """
        r = folding.FoldScope(block)
        th = TextHelper(self.editor)
        start, end = r.get_range(ignore_blank_lines=True)
        if start > 0:
            top = th.line_pos_from_number(start)
        else:
            top = 0
        bottom = th.line_pos_from_number(end + 1)
        h = bottom - top
        if h == 0:
            h = self.sizeHint().height()
        w = self.sizeHint().width()
        self._draw_rect(QtCore.QRectF(0, top, w, h), painter)

    def _draw_rect(self, rect, painter):
        """
        Draw the background rectangle using the current style primitive color
        or foldIndicatorBackground if nativeFoldingIndicator is true.

        :param rect: The fold zone rect to draw

        :param painter: The widget's painter.
        """
        # c = self.__color
        # if self.__native:
        c = self.get_system_color()
        grad = QtGui.QLinearGradient(rect.topLeft(),
                                     rect.topRight())
        grad.setColorAt(0, c.lighter(100))
        grad.setColorAt(1, c.lighter(110))
        outline = c.darker(110)
        painter.fillRect(rect, grad)
        painter.setPen(QtGui.QPen(outline))
        painter.drawLine(rect.topLeft() +
                         QtCore.QPointF(1, 0),
                         rect.topRight() -
                         QtCore.QPointF(1, 0))
        painter.drawLine(rect.bottomLeft() +
                         QtCore.QPointF(1, 0),
                         rect.bottomRight() -
                         QtCore.QPointF(1, 0))
        painter.drawLine(rect.topRight() +
                         QtCore.QPointF(0, 1),
                         rect.bottomRight() -
                         QtCore.QPointF(0, 1))
        painter.drawLine(rect.topLeft() +
                         QtCore.QPointF(0, 1),
                         rect.bottomLeft() -
                         QtCore.QPointF(0, 1))

    def get_system_color(self):
        def merged_colors(colorA, colorB, factor):
            maxFactor = 100
            colorA = QtGui.QColor(colorA)
            colorB = QtGui.QColor(colorB)
            tmp = colorA
            tmp.setRed((tmp.red() * factor) / maxFactor +
                       (colorB.red() * (maxFactor - factor)) / maxFactor)
            tmp.setGreen((tmp.green() * factor) / maxFactor +
                         (colorB.green() * (maxFactor - factor)) / maxFactor)
            tmp.setBlue((tmp.blue() * factor) / maxFactor +
                        (colorB.blue() * (maxFactor - factor)) / maxFactor)
            return tmp

        pal = self.editor.palette()
        b = pal.window().color()
        h = pal.highlight().color()
        return merged_colors(b, h, 50)

    def _draw_fold_indicator(self, top, mouse_over, collapsed, painter):
        """
        Draw the fold indicator/trigger (arrow).

        :param top: Top position
        :param mouse_over: Whether the mouse is over the indicator
        :param collapsed: Whether the trigger is collapsed or not.
        :param painter: QPainter
        """
        if os.environ['QT_API'].lower() != 'pyqt5':
            opt = QtGui.QStyleOptionViewItemV2()
        else:
            opt = QtWidgets.QStyleOptionViewItem()
        opt.rect = QtCore.QRect(0, top, self.sizeHint().width(),
                                self.sizeHint().height())
        opt.state = (QtWidgets.QStyle.State_Active |
                     QtWidgets.QStyle.State_Item |
                     QtWidgets.QStyle.State_Children)
        if not collapsed:
            opt.state |= QtWidgets.QStyle.State_Open
        if mouse_over:
            opt.state |= (QtWidgets.QStyle.State_MouseOver |
                          QtWidgets.QStyle.State_Enabled |
                          QtWidgets.QStyle.State_Selected)
            opt.palette.setBrush(QtGui.QPalette.Window,
                                 self.palette().highlight())
        opt.rect.translate(-2, 0)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_IndicatorBranch,
                                   opt, painter, self)

    def find_parent_scope(self, block):
        original = block
        if not TextBlockHelper.is_fold_trigger(block):
            # search level of next non blank line
            while block.text().strip() == '' and block.isValid():
                block = block.next()
            ref_lvl = TextBlockHelper.get_fold_lvl(block) - 1
            block = original
            while (block.blockNumber() and
                   (not TextBlockHelper.is_fold_trigger(block) or
                    TextBlockHelper.get_fold_lvl(block) > ref_lvl)):
                block = block.previous()
        return block

    def _clear_scope_decos(self):
        for deco in self._scope_decos:
            self.editor.decorations.remove(deco)
        self._scope_decos[:] = []

    def _get_scope_highlight_color(self):
        color = self.editor.background
        if color.lightness() > 128:
            return drift_color(self.editor.background, 105)
        else:
            return drift_color(self.editor.background, 130)

    def _add_scope_decoration(self, start, end):
        """
        Show a scope decoration on the editor widget

        :param start: Start line
        :param end: End line
        """
        color = self._get_scope_highlight_color()
        tc = self.editor.textCursor()
        if start != 1:
            d = TextDecoration(tc, start_line=1, end_line=start)
            d.set_full_width(True, clear=False)
            d.draw_order = 1
            d.set_background(color)
            self.editor.decorations.append(d)
            self._scope_decos.append(d)
        start_line= end + 1
        end_line= self.editor.document().blockCount()
        if start_line < end_line:
            d = TextDecoration(tc, start_line=start_line, end_line=end_line)
            d.set_full_width(True, clear=False)
            d.draw_order = 1
            d.set_background(color)
            self.editor.decorations.append(d)
            self._scope_decos.append(d)

    def _highlight_surrounding_scopes(self, block):
        scope = FoldScope(block)
        if (self._current_scope is None or
                self._current_scope.get_range() != scope.get_range()):
            self._current_scope = scope
            self._clear_scope_decos()
            # highlight surrounding parent scopes with a darker color
            start, end = scope.get_range()
            if not TextBlockHelper.get_fold_trigger_state(block):
                self._add_scope_decoration(start, end)

    def mouseMoveEvent(self, event):
        """
        Detect mouser over indicator and highlight the current scope in the
        editor (up and down decoration arround the foldable text when the mouse
        is over an indicator).

        :param event: event
        """
        super().mouseMoveEvent(event)
        th = TextHelper(self.editor)
        line = th.line_nbr_from_position(event.pos().y())
        if line:

            block = self.find_parent_scope(
                self.editor.document().findBlockByNumber(line - 1))
            if TextBlockHelper.is_fold_trigger(block):
                self._mouse_over_line = block.blockNumber() + 1
                self._highlight_surrounding_scopes(block)
            else:
                self._mouse_over_line = None
            self._highlight_active_indicator()

    def _highlight_active_indicator(self):
        self.repaint()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._clear_scope_decos()
        self._mouse_over_line = None
        self._current_scope = None
        self.editor.repaint()

    def _add_fold_decoration(self, block, region):
        deco = TextDecoration(block)
        deco.signals.clicked.connect(self._on_fold_deco_clicked)
        deco.tooltip = region.text(max_lines=25)
        deco.draw_order = 2
        deco.block = block
        deco.select_line()
        deco.set_outline(drift_color(
            self._get_scope_highlight_color(), 110))
        deco.set_background(self._get_scope_highlight_color())
        deco.set_foreground(QtGui.QColor('#808080'))
        self._block_decos.append(deco)
        self.editor.decorations.append(deco)

    def toggle_fold_trigger(self, block):
        """
        Toggle a fold trigger block (expand or collapse it).

        :param block: The QTextBlock to expand/collapse
        """
        if not TextBlockHelper.is_fold_trigger(block):
            return
        region = FoldScope(block)
        if region.collapsed:
            region.unfold()
            deco = None
            for deco in self._block_decos:
                if deco.block == block:
                    break
            if deco is not None:
                self._block_decos.remove(deco)
                self.editor.decorations.remove(deco)
                del deco
            if self._mouse_over_line:
                self._add_scope_decoration(*region.get_range())
        else:
            region.fold()
            # add folded deco
            self._add_fold_decoration(block, region)
            self._clear_scope_decos()
        TextHelper(self.editor).mark_whole_doc_dirty()
        self.editor.repaint()

    def mousePressEvent(self, event):
        """ Folds/unfolds the pressed indicator if any. """
        if self._mouse_over_line:
            block = self.editor.document().findBlockByNumber(
                self._mouse_over_line - 1)
            self.toggle_fold_trigger(block)

    def _on_fold_deco_clicked(self, deco):
        self.toggle_fold_trigger(deco.block)

    def on_state_changed(self, state):
        """
        On state changed we (dis)connect to the cursorPositionChanged signal
        """
        if state:
            # self.editor.cursorPositionChanged.connect(
            #     self.refresh_decorations)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            # self.editor.cursorPositionChanged.disconnect(
            #     self.refresh_decorations)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _select_scope(self, block, c):
        start_block = block
        _, end = FoldScope(block).get_range()
        end_block = self.editor.document().findBlockByNumber(end)
        c.beginEditBlock()
        c.setPosition(start_block.position())
        c.setPosition(end_block.position(), c.KeepAnchor)
        c.deleteChar()
        c.endEditBlock()

    def _on_key_pressed(self, event):
        keys = [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]
        if event.key() in keys:
            c = self.editor.textCursor()
            assert isinstance(c, QtGui.QTextCursor)
            if c.hasSelection():
                for deco in self._block_decos:
                    if c.selectedText() == deco.cursor.selectedText():
                        block = deco.block
                        self._select_scope(block, c)
                        event.accept()

    def refresh_decorations(self, force=False):
        cursor = self.editor.textCursor()
        # todo, see how it works with the if in big files after a collapse all
        if (self._prev_cursor is None or force or
                self._prev_cursor.blockNumber() != cursor.blockNumber()):
            for deco in self._block_decos:
                self.editor.decorations.remove(deco)
            for deco in self._block_decos:
                deco.set_outline(drift_color(
                    self._get_scope_highlight_color(), 110))
                deco.set_background(self._get_scope_highlight_color())
                self.editor.decorations.append(deco)
        self._prev_cursor = cursor

    def _show_previous_blank_lines(self, block):
        # set previous blank lines visibles
        pblock = block.previous()
        while (pblock.text().strip() == '' and
                       pblock.blockNumber() >= 0):
            pblock.setVisible(True)
            pblock = pblock.previous()

    def collapse_all(self):
        """
        Collapses all triggers and makes all blocks with fold level > 0
        invisible.
        """
        block = self.editor.document().firstBlock()
        last = self.editor.document().lastBlock()
        while block.isValid():
            lvl = TextBlockHelper.get_fold_lvl(block)
            trigger = TextBlockHelper.is_fold_trigger(block)
            if trigger:
                if lvl == 0:
                    self._show_previous_blank_lines(block)
                TextBlockHelper.set_fold_trigger_state(block, True)
                self._add_fold_decoration(block, FoldScope(block))
            block.setVisible(lvl == 0)
            if block == last and block.text().strip() == '':
                block.setVisible(True)
                self._show_previous_blank_lines(block)
            block = block.next()
        TextHelper(self.editor).mark_whole_doc_dirty()
        self.editor.repaint()

    def expand_all(self):
        block = self.editor.document().firstBlock()
        while block.isValid():
            TextBlockHelper.set_fold_trigger_state(block, False)
            block.setVisible(True)
            block = block.next()
        for deco in self._block_decos:
            self.editor.decorations.remove(deco)
        self._block_decos.clear()
        TextHelper(self.editor).mark_whole_doc_dirty()
        self.editor.repaint()

    def _on_action_toggle(self):
        block = self.find_parent_scope(self.editor.textCursor().block())
        self.toggle_fold_trigger(block)

    def _on_action_collapse_all_triggered(self):
        self.collapse_all()

    def _on_action_expand_all_triggered(self):
        self.expand_all()
