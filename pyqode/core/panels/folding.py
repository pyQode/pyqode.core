# -*- coding: utf-8 -*-
"""
This module contains the marker panel
"""
import logging
import os
from pyqode.core.api import TextBlockHelper, folding
from pyqode.core.api.panel import Panel
from pyqode.core.qt import QtCore, QtWidgets, QtGui
from pyqode.core.api.utils import TextHelper


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
        self._indicators = []
        self.setMouseTracking(True)
        self.scrollable = True
        self._mouse_over_line = None

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
            collapsed = TextBlockHelper.get_fold_trigger_state(block)
            if not collapsed:
                self._draw_fold_region_background(block, painter)

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
        r = folding.FoldRegion(block)
        th = TextHelper(self.editor)
        start, end = r.get_range(ignore_blank_lines=True)
        top = th.line_pos_from_number(start - 1)
        bottom = th.line_pos_from_number(end)
        h = bottom - top
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
        grad.setColorAt(0, c.lighter(110))
        grad.setColorAt(1, c.lighter(130))
        outline = c
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
            original = block = self.editor.document().findBlockByNumber(line - 1)
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
            if TextBlockHelper.is_fold_trigger(block):
                self._mouse_over_line = block.blockNumber() + 1
            else:
                self._mouse_over_line = None
            self._highlight_active_indicator()

    def _highlight_active_indicator(self):
        self.repaint()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._mouse_over_line = None
        self.repaint()
