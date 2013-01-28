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
import logging
from PySide.QtCore import QPoint
from PySide.QtCore import QRect
from PySide.QtCore import QSize
from PySide.QtCore import QTimer
from PySide.QtCore import Signal
from PySide.QtGui import QColor
from PySide.QtGui import QFontMetricsF
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QBrush
from PySide.QtGui import QToolTip
from pygments.token import Text
from pcef.base import QEditorPanel


class Marker(object):
    """
    A marker is a rect drawn on a QMarkersPanel at a specific block position.

    Fields:
        - position: block count
        - icon: QIcon to draw
        - tooltip: text shown when mouse is over the marker
    """

    def __init__(self, position, icon, tooltip=""):
        self.position = position
        self.icon = icon
        self.tooltip = tooltip


class QMarkersPanel(QEditorPanel):
    """
    Panel used to draw a collection of marker.
    A marker is 16x16 icon placed at a specific line number.

    A marker is added/removed when the user click on the the widget or
    programmatically. Actually if there is no marker where the user clicked, the
    markerAddRequested signal is emitted as we don't known the marker
    properties. When a marker is removed by the user, the markerRemoved is
    emitted.

    .. note:: The markers position is updated whenever a line is added/removed.
    .. note:: The markers list is cleared when a new text is set on the text
        edit (see QCodeEdit.newTextSet signal)

    .. note:: If a marker goes out of documents (line number <= 0) the
    markerOutOfDoc is emitted.
    """

    #: Stylesheet
    QSS = """QToolTip {
         background-color: %(back)s;
         color: %(color)s;
         border: 1px solid %(color)s;
         padding: 2px;
         opacity: 220;
    }
    """

    #: Signal emitted with the line number where the marker must be added
    addMarkerRequested = Signal(QEditorPanel, int)
    #: Signal emitted when a marker is removed by the user.
    markerRemoved = Signal(QEditorPanel, Marker)
    #: Signal emitted when a marker is out of the document. This usually
    #  happen when the user delete lines from the beginning of the doc.
    markerOutOfDoc = Signal(QEditorPanel, Marker)
    #: Signal emitted before clearing the markers when a new text is set to give
    #  a chance to the user to save the markers list.
    clearingMarkers = Signal(QEditorPanel)

    def __init__(self, name, markersReadOnly=False, parent=None):
        QEditorPanel.__init__(
            self, name, "Display markers foreach line", parent)
        self.markers = []
        #: prevent user from adding/removing markers with mouse click
        self.markersReadOnly = markersReadOnly
        self.setMouseTracking(True)
        self.timer = QTimer()
        self._tooltipPos = -1
        self._prev_line = -1
        self.logger = logging.getLogger(
            __name__ + "." + self.__class__.__name__)

    def addMarker(self, marker):
        """ Adds a marker to be displayed """
        self.markers.append(marker)
        self.update()

    def removeMarker(self, marker):
        """ Remove a marker """
        self.markers.remove(marker)
        self.update()

    def clearMarkers(self, emit=False):
        """ Clear marker list """
        self.clearingMarkers.emit(self)
        self.markers[:] = []
        self.update()

    def install(self, editor):
        QEditorPanel.install(self, editor)
        self.editor.textEdit.visibleBlocksChanged.connect(self.update)
        fm = QFontMetricsF(self.editor.textEdit.font())
        self.size_hint = QSize(fm.height(), fm.height())
        editor.textEdit.blockCountChanged.connect(self.onBlockCountChanged)
        self.bc = self.editor.textEdit.blockCount()
        self.editor.textEdit.newTextSet.connect(self.onNewTextSet)
        self.editor.textEdit.keyPressed.connect(self.updateCursorPos)
        self.updateCursorPos()

    def _onStyleChanged(self):
        """ Updates stylesheet and brushes. """
        style = self.currentStyle
        self.back_brush = QBrush(QColor(style.panelsBackgroundColor))
        self.active_line_brush = QBrush(QColor(style.activeLineColor))
        self.separator_pen = QPen(QColor(style.panelSeparatorColor))
        qss = self.QSS % {"back": style.activeLineColor,
                          "color": style.tokenColor(Text)}
        self.setStyleSheet(qss)
        self.updateGeometry()

    def sizeHint(self):
        """ Returns the widget size hint (based on the editor font size) """
        fm = QFontMetricsF(self.editor.textEdit.font())
        self.size_hint = QSize(fm.height(), fm.height())
        return self.size_hint

    def onNewTextSet(self):
        """ Clears markers when a new text is set """
        self.clearMarkers(True)

    def getMarkerForLine(self, l):
        """ Retusn the marker for the line l if any, else return None """
        for m in self.markers:
            if m.position == l:
                return m
        return None

    def updateCursorPos(self):
        """ Update cursor pos variables """
        self.tcPos = self.editor.textEdit.textCursor().blockNumber() + 1
        self.tcPosInBlock = self.editor.textEdit.textCursor().positionInBlock()

    def onBlockCountChanged(self, num):
        """ Handles lines added/removed events """
        # a l has beeen inserted or removed
        tcPos = self.editor.textEdit.textCursor().blockNumber() + 1
        tcPosInBlock = self.editor.textEdit.textCursor().positionInBlock()
        bc = self.bc
        if bc < num:
            self.onLinesAdded(num - bc, tcPos, tcPosInBlock)
        else:
            self.onLinesRemoved(bc - num, tcPos, tcPosInBlock)
        self.tcPosInBlock = self.tcPosInBlock
        self.bc = num

    def onLinesAdded(self, nbLines, tcPos, tcPosInBlock):
        """ Offsets markers positions with the number of line added """
        if self.tcPosInBlock > 0:
            self.tcPos += 1
            # offset each l after the tcPos by nbLines
        for marker in self.markers:
            if marker.position >= self.tcPos:
                marker.position += nbLines
        self.tcPos = tcPos
        self.tcPosInBlock = tcPosInBlock
        self.update()

    def onLinesRemoved(self, nbLines, tcPos, tcPosInBlock):
        """ Offsets markers positions with the number of line removed """
        for marker in self.markers:
            if marker.position >= self.tcPos:
                marker.position -= nbLines
                if marker.position < 1:
                    self.markerOutOfDoc.emit(self, marker)
        self.tcPos = tcPos
        self.tcPosInBlock = tcPosInBlock
        self.update()

    def paintEvent(self, event):
        """ Paints the widget """
        QEditorPanel.paintEvent(self, event)
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.back_brush)
        for vb in self.editor.textEdit.visible_blocks:
            l = vb.row
            marker = self.getMarkerForLine(l)
            if marker:
                if marker.icon is not None:
                    r = QRect()
                    r.setX(vb.rect.x())
                    r.setY(vb.rect.y())
                    r.setWidth(self.size_hint.width())
                    r.setHeight(self.size_hint.height())
                    marker.icon.paint(painter, r)
        return

    def leaveEvent(self, event):
        """ Resets prev line to -1 when we leave otherwise the tooltip won't be
        shown next time we hover the marker """
        self._prev_line = -1

    def mouseMoveEvent(self, event):
        """ Shows a tooltip """
        pos = event.pos()
        y = pos.y()
        for vb in self.editor.textEdit.visible_blocks:
            top = vb.top
            height = vb.height
            if top < y < top + height:
                marker = self.getMarkerForLine(vb.row)
                if (marker is not None and
                    marker.tooltip is not None and
                    marker.tooltip != ""):
                    if self._prev_line != vb.row:
                        self.timer.stop()
                        self._tooltip = marker.tooltip
                        centerX = self.size_hint.width()
                        centerY = vb.rect.y()
                        self._tooltipPos = QPoint(centerX, centerY)
                        self._prev_line = vb.row
                        self.timer.singleShot(1500, self.displayTooltip)
                return

    def mouseReleaseEvent(self, event):
        """
        Adds/Remove markers on click
        """
        if self.markersReadOnly is True:
            return
        pos = event.pos()
        y = pos.y()
        for vb in self.editor.textEdit.visible_blocks:
            top = vb.top
            height = vb.height
            if top < y < top + height:
                marker = self.getMarkerForLine(vb.row)
                if marker is not None:
                    self.removeMarker(marker)
                    self.markerRemoved.emit(self, marker)
                    self.logger.debug("Marker removed")
                else:
                    self.logger.debug("Marker add requested (l: %d)" % vb.row)
                    self.addMarkerRequested.emit(self, vb.row)

    def displayTooltip(self):
        """ Display the tooltip """
        QToolTip.showText(self.mapToGlobal(self._tooltipPos),
                          self._tooltip,
                          self)