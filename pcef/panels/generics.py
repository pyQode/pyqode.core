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
from PySide.QtCore import Qt
from PySide.QtCore import QPoint
from PySide.QtCore import QRect
from PySide.QtCore import QSize
from PySide.QtCore import QTimer
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from PySide.QtGui import QFont
from PySide.QtGui import QColor
from PySide.QtGui import QFontMetricsF
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QBrush
from PySide.QtGui import QToolTip
from PySide.QtGui import QKeyEvent
from PySide.QtGui import QTextCursor
from PySide.QtGui import QTextDocument
from pygments.token import Text
from pcef.base import QEditorPanel
from pcef.base import TextDecoration
from pcef.promoted_widgets import QPlainCodeEdit
from pcef.ui import search_panel_ui


class QLineNumberPanel(QEditorPanel):
    """ This panel show the line numbers """

    #: Panel identifier
    IDENTIFIER = "LineNumberPanel"

    def __init__(self, parent=None):
        QEditorPanel.__init__(
            self, self.IDENTIFIER, "Display text line numbers", parent)

    def install(self, editor):
        QEditorPanel.install(self, editor)
        self.editor.textEdit.visibleBlocksChanged.connect(self.update)
        self.editor.textEdit.blockCountChanged.connect(self.updateGeometry)

    def updateStyling(self):
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

    def updateStyling(self):
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
        active = self.editor.textEdit.textCursor().blockNumber()
        for vb in self.editor.textEdit.visible_blocks:
            l = vb.row
#            if l == active + 1:
#                painter.fillRect(vb.rect, self.active_line_brush)
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


class FoldIndicator(object):
    """
    A fold marker is used by the QFoldPanel to display code folding indicators.

    A fold marker is defined by two line number (start and end) and a boolean
    property that tells whether the code block is folded or not.

    Fields:
        - start: start line nbr(where the +/- indicator is drawn)
        - end: end line nbr (wher |_ is drawn)
    """
    def __init__(self, start, end):
        #: Start line
        self.start = start
        #: End line
        self.end = end
        #: Is folded ?
        self.folded = False
        #: Is hover ?
        self.hover = False


class QFoldPanel(QEditorPanel):
    """ This panel display folding indicators and folds/unfolds text """
    #: Panel identifier
    IDENTIFIER = "QFoldPanel"

    def __init__(self, parent=None):
        QEditorPanel.__init__(
            self, self.IDENTIFIER, "Display code folding indicators", parent)
        self.fold_indicators = []
        self.setMouseTracking(True)
        self.logger = logging.getLogger(
            __name__ + "." + self.__class__.__name__)

    def addIndicator(self, start, end):
        """
        Adds a fold indicator
        :param start: Start line (1 based)
        :param end: End line
        """
        self.fold_indicators.append(FoldIndicator(start, end))
        self.update()

    def removeIndicator(self, indicator):
        """
        Remove a fold indicator
        :param indicator: Indicator to remove
        """
        self.fold_indicators.remove(indicator)
        self.update()

    def clearIndicators(self):
        """ Remove all indicators """
        self.fold_indicators[:] = []
        self.update()

    def install(self, editor):
        """ Install the panel on the editor """
        QEditorPanel.install(self, editor)
        self.editor.textEdit.visibleBlocksChanged.connect(self.update)
        self.updateCursorPos()
        self.font = QFont(self.currentStyle.fontName, 7)
        self.font.setBold(True)
        fm = QFontMetricsF(self.editor.textEdit.font())
        self.size_hint = QSize(fm.height(), fm.height())
        editor.textEdit.blockCountChanged.connect(self.onBlockCountChanged)
        self.bc = self.editor.textEdit.blockCount()
        self.editor.textEdit.newTextSet.connect(self.onNewTextSet)
        self.editor.textEdit.keyPressed.connect(self.updateCursorPos)

    def updateStyling(self):
        """ Updates brushes and pens """
        style = self.currentStyle
        self.back_brush = QBrush(QColor(style.panelsBackgroundColor))
        self.active_line_brush = QBrush(QColor(style.activeLineColor))
        self.separator_pen = QPen(QColor(style.panelSeparatorColor))
        self.normal_pen = QPen(QColor(style.lineNbrColor))
        self.highlight_pen = QPen(QColor(style.tokenColor(Text)))
        self.updateGeometry()

    def sizeHint(self):
        """ Returns a fixed size hint (16x16) """
        self.size_hint = QSize(16, 16)
        return self.size_hint

    def onNewTextSet(self):
        self.clearIndicators()

    def getIndicatorForLine(self, line):
        """ Returns the fold indicator whose start position equals the line
        :param line: Line nbr of the start position of the indicator to get.
        :return: FoldIndicator or None
        """
        for m in self.fold_indicators:
            if m.start == line:
                return m
        return None

    def updateCursorPos(self):
        self.tcPos = self.editor.textEdit.textCursor().blockNumber() + 1
        self.tcPosInBlock = self.editor.textEdit.textCursor().positionInBlock()

    def onBlockCountChanged(self, num=-1):
        """ Handles line added/removed event """
        # a line has been inserted or removed
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
        # offset each line after the tcPos by nbLines
        for marker in self.fold_indicators:
            if marker.start >= self.tcPos:
                marker.start += nbLines
                marker.end += nbLines
        self.tcPos = tcPos
        self.tcPosInBlock = tcPosInBlock
        self.update()

    def onLinesRemoved(self, nbLines, tcPos, tcPosInBlock):
        """ Offsets markers positions with the number of line removed """
        for marker in self.fold_indicators:
            if marker.start >= self.tcPos:
                marker.start -= nbLines
                marker.end -= nbLines
                if marker.start < 1:
                    self.removeIndicator(marker)
        self.tcPos = tcPos
        self.tcPosInBlock = tcPosInBlock
        self.update()

    def paintEvent(self, event):
        """ Paints the widget """
        QEditorPanel.paintEvent(self, event)
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.back_brush)

#        # paint active line first
#        active = self.editor.textEdit.textCursor().blockNumber()
#        for vb in self.editor.textEdit.visible_blocks:
#            if vb.row == active + 1:
#                painter.fillRect(vb.rect, self.active_line_brush)

        for vb in self.editor.textEdit.visible_blocks:
            line = vb.row
            # paint marker for line
            marker = self.getIndicatorForLine(line)
            if marker is None:
                continue
            # use the normal pen to draw the fold indicator
            drawLines = False
            pen = self.normal_pen
            if marker.hover is True:
                pen = self.highlight_pen
                drawLines = True
            painter.setPen(pen)
            # get the text to draw
            txt = '-'
            if marker.folded is True:
                drawLines = False
                txt = '+'
            offset = 4
            h = self.size_hint.height()
            fm = QFontMetricsF(self.editor.textEdit.font())
            hoffset = (fm.height() - h) / 2.0
            r = QRect(vb.rect.x(), vb.rect.y() + hoffset, self.size_hint.width(), self.size_hint.height())
            painter.setFont(self.font)
            painter.drawText(r, Qt.AlignVCenter | Qt.AlignHCenter, txt)
            w = self.size_hint.width() - 2 * offset
            h = self.size_hint.width() - 2 * offset
            hoffset = (fm.height() - h) / 2.0
            r.setX(vb.rect.x() + offset)
            r.setY(vb.rect.y() + hoffset)
            r.setWidth(w)
            r.setHeight(h)
            painter.drawRect(r)
            if drawLines is True:
                top = (vb.rect.x() + self.size_hint.width() / 2.0,
                       vb.rect.y() + hoffset + offset * 2)
                delta = ((marker.end - marker.start) * vb.height)  # - (vb.rect.height() / 2.0)
                bottom = (top[0], top[1] + delta)
                painter.drawLine(top[0], top[1], bottom[0], bottom[1])
                painter.drawLine(bottom[0], bottom[1], bottom[0] + self.size_hint.width() / 2.0, bottom[1])

        return

    def leaveEvent(self, event):
        """ Clears indicator hover states and repaint """
        for m in self.fold_indicators:
            m.hover = False
        self.repaint()

    def mouseMoveEvent(self, event):
        """ Detects indicator hover states """

        pos = event.pos()
        y = pos.y()
        repaint = False
        for m in self.fold_indicators:
            if m.hover is True:
                m.hover = False
                repaint = True
        for vb in self.editor.textEdit.visible_blocks:
            top = vb.top
            height = vb.height
            if top < y < top + height:
                marker = self.getIndicatorForLine(vb.row)
                if marker is not None:
                    # mark it as hover and repaint
                    marker.hover = True
                    repaint = True
        if repaint is True:
            self.repaint()

    def mouseReleaseEvent(self, event):
        """
        Folds/Unfolds code blocks
        """
        pos = event.pos()
        y = pos.y()
        for vb in self.editor.textEdit.visible_blocks:
            top = vb.top
            height = vb.height
            if top < y < top + height:
                marker = self.getIndicatorForLine(vb.row)
                if marker is not None:
                    marker.folded = not marker.folded
                    self.editor.textEdit.fold(marker.start - 1, marker.end, marker.folded)
                    self.repaint()


class QSearchPanel(QEditorPanel):
    """
    Search (& replace) panel. Allow the user to search for content in the editor
    All occurrences are highlighted using the pygments syntax highlighter.
    The occurrence under the cursor is selected using the find method of the
    plain text edit. User can go backward and forward.

    The panel add a few actions to the editor menu(search, replace, next,
    previous, replace, replace all)

    The panel is show with ctrl-f for a search, ctrl-r for a search and replace.
    The panel is hidden with ESC or by using the close button (white cross).

    .. note:: The widget use a custom stylesheet similar to the search panel of
              Qt Creator.
    """
    #: Stylesheet
    QSS = """QWidget
    {
        background-color: %(bck)s;
        color: %(color)s;
    }

    QLineEdit
    {
        background-color: %(txt_bck)s;
        border: 1px solid %(highlight)s;
        border-radius: 3px;
    }

    QLineEdit:hover, QLineEdit:focus
    {
        border: 1px solid %(color)s;
        border-radius: 3px;
    }

    QPushButton
    {
        background-color: transparent;
    }

    QPushButton:hover
    {
        background-color: %(highlight)s;
        border: none;
        border-radius: 5px;
        color: %(color)s;
    }

    QPushButton:pressed
    {
        background-color: %(highlight)s;
        border: 2px black;
        border-radius: 5px;
        color: %(color)s;
    }

    QPushButton:disabled
    {
        color: %(highlight)s;
    }

    QCheckBox:hover
    {
            background-color: %(highlight)s;
            color: %(color)s;
            border-radius: 5px;
    }
    """

    #: Emitted when the nbr of occurences has changed
    numOccurrencesChanged = Signal()

    def __get_numOccurrences(self):
        return self._numOccurrences

    def __set_numOccurrences(self, numOccurrences):
        if self._numOccurrences != numOccurrences:
            self._numOccurrences = numOccurrences
            self.numOccurrencesChanged.emit()

    #: Nb occurences detected
    numOccurrences = property(__get_numOccurrences, __set_numOccurrences)

    def __init__(self, parent=None):
        QEditorPanel.__init__(self, "SearchPanel",
                              "The search and replace panel", parent)
        self.ui = search_panel_ui.Ui_SearchPanel()
        self.ui.setupUi(self)
        self._decorations = []
        self._numOccurrences = 0
        self._processing = False
        self.numOccurrencesChanged.connect(self.updateUi)
        self.ui.actionFindNext.triggered.connect(self.findNext)
        self.ui.actionFindPrevious.triggered.connect(self.findPrevious)
        self.ui.actionSearch.triggered.connect(self.showSearchPanel)
        self.ui.actionActionSearchAndReplace.triggered.connect(
            self.showSearchAndReplacePanel)
        self.hide()
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

    def showSearchPanel(self):
        """ Shows the search panel """
        self.show()
        self.ui.widgetSearch.show()
        self.ui.widgetReplace.hide()
        selectedText = self.editor.textEdit.textCursor().selectedText()
        if selectedText != "":
            self.ui.lineEditSearch.setText(selectedText)
        self.ui.lineEditSearch.setFocus()

    def showSearchAndReplacePanel(self):
        """ Shows the search and replace panel """
        self.show()
        self.ui.widgetSearch.show()
        self.ui.widgetReplace.show()
        selectedText = self.editor.textEdit.textCursor().selectedText()
        if selectedText != "":
            self.ui.lineEditSearch.setText(selectedText)
        self.ui.lineEditReplace.setFocus()

    def updateUi(self):
        """ Updates user interface (checkbox states, nb matches, ...) """
        # update matches label
        self.ui.labelMatches.setText("%d matches" % self.numOccurrences)
        color = "#CC0000"
        if self.numOccurrences > 0:
            color = "#00CC00"
        self.ui.labelMatches.setStyleSheet("color: %s" % color)

        # update replace buttons state
        replaceTxt = self.ui.lineEditReplace.text()
        enableReplace = (self.numOccurrences > 0 and replaceTxt != "")
        self.ui.pushButtonReplaceAll.setEnabled(enableReplace)
        self.ui.pushButtonReplace.setEnabled(enableReplace)

        # update navigation buttons state
        enableNavigation = (self.numOccurrences > 0)
        self.ui.pushButtonDown.setEnabled(enableNavigation)
        self.ui.pushButtonUp.setEnabled(enableNavigation)

    def updateStyling(self):
        """ Change stylesheet """
        qss = self.QSS % {"bck": self.currentStyle.panelsBackgroundColor,
                          "txt_bck": self.currentStyle.backgroundColor,
                          "color": self.currentStyle.tokenColor(Text),
                          "highlight": self.currentStyle.panelSeparatorColor}
        self.setStyleSheet(qss)

    def install(self, editor):
        """  Install the panel on the editor """
        QEditorPanel.install(self, editor)
        self.editor.textEdit.cursorPositionChanged.connect(self.onCursorMoved)
        self.editor.textEdit.textChanged.connect(self.updateSearchResults)
        self.updateUi()
        self.installActions()

    def installActions(self):
        """ Installs actions on the editor context menu """
        editor = self.editor.textEdit
        assert isinstance(editor, QPlainCodeEdit)
        editor.addSeparator()
        editor.addAction(self.ui.actionSearch)
        editor.addAction(self.ui.actionActionSearchAndReplace)
        editor.addAction(self.ui.actionFindPrevious)
        editor.addAction(self.ui.actionFindNext)

    @Slot()
    def updateSearchResults(self):
        """  Updates the search results """
        txt = self.ui.lineEditSearch.text()
        self.highlightOccurrences(txt)

    def findNext(self):
        """ Finds the next occurrence """
        txt = self.ui.lineEditSearch.text()
        sf = self.getUserSearchFlag()
        if not self.editor.textEdit.find(txt, sf):
            # restart from start
            tc = self.editor.textEdit.textCursor()
            tc.movePosition(QTextCursor.Start)
            self.editor.textEdit.setTextCursor(tc)
            self.editor.textEdit.find(txt, sf)

    @Slot()
    def on_pushButtonDown_clicked(self):
        """ Finds the next occurrence """
        self.findNext()

    def findPrevious(self):
        """ Finds the previous occurrence """
        txt = self.ui.lineEditSearch.text()
        sf = self.getUserSearchFlag()
        sf |= QTextDocument.FindBackward
        if not self.editor.textEdit.find(txt, sf):
            # restart from end
            tc = self.editor.textEdit.textCursor()
            tc.movePosition(QTextCursor.End)
            self.editor.textEdit.setTextCursor(tc)
            self.editor.textEdit.find(self.ui.lineEditSearch.text(), sf)

    @Slot()
    def on_pushButtonUp_clicked(self):
        """ Finds the previous occurrence """
        self.findPrevious()

    @Slot()
    def on_pushButtonClose_clicked(self):
        """ Hides the panel """
        self.hide()
        self.ui.lineEditSearch.setText("")

    @Slot(int)
    def on_checkBoxCase_stateChanged(self, state):
        """ Re-highlight occurences """
        if self._processing is False:
            self.highlightOccurrences(self.ui.lineEditSearch.text())

    @Slot(int)
    def on_checkBoxWholeWords_stateChanged(self, state):
        """ Re-highlight occurences """
        if self._processing is False:
            self.highlightOccurrences(self.ui.lineEditSearch.text())

    def keyPressEvent(self, event):
        """ Handles key pressed: Return = next occurence, Esc = close panel """
        assert isinstance(event, QKeyEvent)
        if event.key() == Qt.Key_Escape:
            self.on_pushButtonClose_clicked()
        if event.key() == Qt.Key_Return:
            if self.ui.lineEditSearch.hasFocus():
                self.findNext()
            if self.ui.lineEditReplace.hasFocus():
                self.on_pushButtonReplace_clicked()

    @Slot(unicode)
    def on_lineEditSearch_textChanged(self, text):
        """ Re-highlight occurences """
        if self._processing is False:
            self.highlightOccurrences(text, True)

    @Slot(unicode)
    def on_lineEditReplace_textChanged(self, text):
        """ Updates user interface """
        self.updateUi()

    @Slot()
    def on_pushButtonReplace_clicked(self):
        """ Replace current selection and select first next occurence """
        txt = self.ui.lineEditReplace.text()
        self.editor.textEdit.insertPlainText(txt)
        self.selectFirst()

    @Slot()
    def on_pushButtonReplaceAll_clicked(self):
        """ Replace all occurences """
        txt = self.ui.lineEditReplace.text()
        if not self.ui.checkBoxCase.isChecked() and txt.upper() == self.ui.lineEditSearch.text().upper():
            return
        while self.numOccurrences > 0:
            self.editor.textEdit.insertPlainText(txt)
            self.selectFirst()

    def onCursorMoved(self):
        """ Re-highlight occurences """
        if self._processing is False:
            self.highlightOccurrences(self.ui.lineEditSearch.text())

    def selectFirst(self):
        """ Select the first next occurences """
        searchFlag = self.getUserSearchFlag()
        txt = self.ui.lineEditSearch.text()
        tc = self.editor.textEdit.textCursor()
        tc.movePosition(QTextCursor.Start)
        self.editor.textEdit.setTextCursor(tc)
        self.editor.textEdit.find(txt, searchFlag)

    def createDecoration(self, tc):
        """ Creates the text occurence decoration """
        deco = TextDecoration(tc)
        deco.setBackground(QBrush(QColor(
            self.currentStyle.searchBackgroundColor)))
        deco.setForeground(QBrush(QColor(
            self.currentStyle.searchColor)))
        return deco

    def highlightAllOccurrences(self):
        """ Highlight all occurrences """
        if not self.isVisible():
            return
        searchFlag = self.getUserSearchFlag()
        txt = self.ui.lineEditSearch.text()
        tc = self.editor.textEdit.textCursor()
        doc = self.editor.textEdit.document()
        tc.movePosition(QTextCursor.Start)
        cptMatches = 0
        tc = doc.find(txt, tc, searchFlag)
        while not tc.isNull():
            deco = self.createDecoration(tc)
            self._decorations.append(deco)
            self.editor.textEdit.addDecoration(deco)
            tc.setPosition(tc.position() + 1)
            tc = doc.find(txt, tc, searchFlag)
            cptMatches += 1
        self.numOccurrences = cptMatches

    def clearDecorations(self):
        """ Remove all decorations """
        for deco in self._decorations:
            self.editor.textEdit.removeDecoration(deco)
        self._decorations[:] = []

    def getUserSearchFlag(self):
        """ Returns the user search flag """
        searchFlag = 0
        if self.ui.checkBoxCase.isChecked():
            searchFlag |= QTextDocument.FindCaseSensitively
        if self.ui.checkBoxWholeWords.isChecked():
            searchFlag |= QTextDocument.FindWholeWords
        return searchFlag

    def highlightOccurrences(self, txt, selectFirst=False):
        """ Highlight occurences
        :param txt: Text to highlight
        :param selectFirst: True to select the first occurence
        """
        self._processing = True
        self.clearDecorations()
        self.highlightAllOccurrences()
        if selectFirst:
            self.selectFirst()
        self._processing = False
