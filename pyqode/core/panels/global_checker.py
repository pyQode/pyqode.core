"""
This module contains the GlobalCheckerPanel.

"""
from pyqode.core import modes
from pyqode.core.api import Panel, TextHelper
from pyqode.core.qt import QtCore, QtGui


class GlobalCheckerPanel(Panel):
    """
    This panel display all errors found in the document. The user can click on
    a marker to quickly go the the error line.

    """

    def __init__(self):
        super(GlobalCheckerPanel, self).__init__()
        self.scrollable = True

    def _draw_markers(self, painter):
        checker_modes = []
        for m in self.editor.modes:
            if isinstance(m, modes.CheckerMode):
                checker_modes.append(m)
        for checker_mode in checker_modes:
            for msg in checker_mode.messages:
                block = msg.block
                color = QtGui.QColor(msg.color)
                brush = QtGui.QBrush(color)
                rect = QtCore.QRect()
                rect.setX(0)
                rect.setY(block.blockNumber() * self.get_marker_height())
                rect.setSize(self.get_marker_size())
                painter.fillRect(rect, brush)
                painter.setPen(QtGui.QPen(color.lighter()))
                painter.drawRect(rect)

    def _draw_visible_area(self, painter):
        start = self.editor.visible_blocks[0][-1]
        end = self.editor.visible_blocks[-1][-1]
        rect = QtCore.QRect()
        rect.setX(0)
        rect.setY(start.blockNumber() * self.get_marker_height())
        rect.setWidth(self.sizeHint().width())
        rect.setBottom(end.blockNumber() * self.get_marker_height())
        c = self.palette().window().color().darker(110)
        c.setAlpha(128)
        painter.fillRect(rect, c)

    def paintEvent(self, event):
        super(GlobalCheckerPanel, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        self._draw_markers(painter)
        self._draw_visible_area(painter)

    def _brush_from_message(self, msg):
        pass

    def sizeHint(self):
        return QtCore.QSize(8, 16)

    def get_marker_height(self):
        # print(self.editor.viewport().height(), self.height(), self.editor.height())
        return self.editor.viewport().height() / TextHelper(self.editor).line_count()

    def get_marker_size(self):
        h = self.get_marker_height()
        # if h < 1:
        #     h = 1
        return QtCore.QSize(self.sizeHint().width(), h)

    def mousePressEvent(self, event):
        height = event.pos().y()
        line = height//self.get_marker_height()
        TextHelper(self.editor).goto_line(line)