# -*- coding: utf-8 -*-
"""
This module contains the marker panel
"""
import logging
import os
from pyqode.core.api import TextBlockHelper
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
        for top_position, line_number, block in self.editor.visible_blocks:
            if TextBlockHelper.is_fold_trigger(block):
                active = self._mouse_over_line == line_number
                # draw the fold indicator
                self._draw_fold_indicator(
                    top_position, active,
                    TextBlockHelper.get_fold_trigger_state(block), painter)

    def _draw_fold_indicator(self, top, active, collapsed, painter):
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
        if active:
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
        self._mouse_over_line = th.line_nbr_from_position(event.pos().y())
        if self._mouse_over_line:
            block = self.editor.document().findBlockByNumber(
                self._mouse_over_line - 1)
            if TextBlockHelper.is_fold_trigger(block):
                # if self.__hoveredStartLine != indic.start:
                #     self.__clearScopeDecorations()
                #     self.__hoveredStartLine = indic.start
                #     self.__addScopeDecoration(indic.start, indic.end)
                self.repaint()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._mouse_over_line = None
        self.repaint()
