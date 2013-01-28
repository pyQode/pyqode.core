#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains the generic panels (used by the generic code editor widget)
"""
from PySide.QtCore import Qt
from PySide.QtCore import QSize
from PySide.QtGui import QFont
from PySide.QtGui import QColor
from PySide.QtGui import QFontMetricsF
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QBrush
from pcef.base import QEditorPanel


class QLineNumberPanel(QEditorPanel):
    """ This panel show the line numbers """

    #: Panel identifier
    IDENTIFIER = "Line numbers"

    def __init__(self, parent=None):
        QEditorPanel.__init__(
            self, self.IDENTIFIER, "Display text line numbers", parent)

    def install(self, editor):
        QEditorPanel.install(self, editor)

    def _onStateChanged(self, state):
        QEditorPanel._onStateChanged(self, state)
        if state is True:
            self.editor.textEdit.visibleBlocksChanged.connect(self.update)
            self.editor.textEdit.blockCountChanged.connect(self.updateGeometry)
        else:
            self.editor.textEdit.visibleBlocksChanged.disconnect(self.update)
            self.editor.textEdit.blockCountChanged.disconnect(self.updateGeometry)

    def _onStyleChanged(self):
        """ Updates brushes and pens """
        if self.editor is not None:
            self.font = self.editor.textEdit.font()
            self.back_brush = QBrush(QColor(
                self.currentStyle.panelsBackgroundColor))
            self.text_pen = QPen(QColor(self.currentStyle.lineNbrColor))
            self.separator_pen = QPen(QColor(
                self.currentStyle.panelSeparatorColor))
            self.active_line_brush = QBrush(QColor(
                self.currentStyle.activeLineColor))
            self.updateGeometry()
        self.repaint()

    def sizeHint(self):
        """
        Return the size hint of the widget (depends on the editor font)
        """
        s = str(self.editor.textEdit.blockCount())
        fm = QFontMetricsF(self.font)
        # +1 needed on window xp! (not needed on seven nor on GNU/Linux)
        return QSize(fm.width('A') * (len(s) + 1), 0)

    def paintEvent(self, event):
        """ Paints the widgets:
         - paints the background
         - paint each visible blocks that intersects the widget bbox.
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.back_brush)
        painter.setPen(self.text_pen)
        painter.setFont(self.font)
        w = self.width() - 2
        # better name lookup speed
        painter_drawText = painter.drawText
        align_right = Qt.AlignRight
        normal_font = painter.font()
        bold_font = QFont(normal_font)
        bold_font.setBold(True)
        active = self.editor.textEdit.textCursor().blockNumber()
        for vb in self.editor.textEdit.visible_blocks:
            row = vb.row
            if row == active + 1:
                painter.setFont(bold_font)
            else:
                painter.setFont(normal_font)
            painter_drawText(0, vb.top, w , vb.height, align_right,
                             str(row))
        return QEditorPanel.paintEvent(self, event)
