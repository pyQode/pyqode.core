                  #!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the marker panel
"""
from pcef.qt import QtCore, QtGui
from pcef.core import constants
from pcef.core.panel import Panel
from pcef.core.system import mergedColors, driftColor


class FoldingIndicator(object):
    UNFOLDED = 0
    FOLDED = 1

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.state = FoldingIndicator.UNFOLDED


class FoldingPanel(Panel):
    DESCRIPTION = "Manage and draw folding indicators"
    IDENTIFIER = "foldingPanel"

    def __init__(self):
        Panel.__init__(self)
        self.__indicators = []
        self.scrollable = True
        self.setMouseTracking(True)
        self.__mouseOveredIndic = None
        self.__rightArrowIcon = (QtGui.QIcon(constants.ICON_ARROW_RIGHT[0]),
                                 QtGui.QIcon(constants.ICON_ARROW_RIGHT[1]))
        self.__downArrowIcon = (QtGui.QIcon(constants.ICON_ARROW_DOWN[0]),
                                QtGui.QIcon(constants.ICON_ARROW_DOWN[1]))
        # get the native fold scope color
        pal = self.palette()
        b = pal.base().color()
        h = pal.highlight().color()
        self.__systemColor = mergedColors(b, h, 50)
        self.__decorations = []

    def install(self, editor):
        Panel.install(self, editor)
        self.__native = self.editor.style.addProperty("nativeFoldingIndicator",
                                                      True)
        self.__color = self.editor.style.addProperty("foldScopeBackground",
                                                     self.__systemColor)

    def onStyleChanged(self, section, key, value):
        Panel.onStyleChanged(self, section, key, value)
        if key == "nativeFoldingIndicator":
            self.__native = value
        elif key == "foldScopeBackground":
            self.__color = QtGui.QColor(value)

    def resetScopeColor(self):
        self.editor.style.setValue("foldScopeBackground", self.__systemColor)

    def addIndicator(self, indicator):
        """
        Adds the marker to the panel.

        :param indicator: Marker to add
        """
        self.__indicators.append(indicator)
        self.repaint()

    def removeIndicator(self, indicator):
        """
        Removes the marker from the panel

        :param indicator: Marker to remove
        """
        self.__indicators.remove(indicator)
        self.repaint()

    def clearIndicators(self):
        """ Clears the markers list """
        self.__indicators[:] = []
        self.repaint()

    def sizeHint(self):
        """ Returns the widget size hint (based on the editor font size) """
        fm = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(fm.height(), fm.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def getIndicatorForLine(self, line):
        for indic in self.__indicators:
            if indic.start == line:
                return indic
        return None

    def getNearestIndicator(self, line):
        for indic in reversed(self.__indicators):
            if indic.start <= line <= indic.end:
                return indic
        return None

    def drawArrow(self, arrowRect, active, expanded, painter):
        if self.__native:
            opt = QtGui.QStyleOptionViewItemV2()
            opt.rect = arrowRect
            opt.state = (QtGui.QStyle.State_Active |
                         QtGui.QStyle.State_Item |
                         QtGui.QStyle.State_Children)
            if expanded:
                opt.state |= QtGui.QStyle.State_Open
            if active:
                opt.state |= (QtGui.QStyle.State_MouseOver |
                              QtGui.QStyle.State_Enabled |
                              QtGui.QStyle.State_Selected)
                opt.palette.setBrush(QtGui.QPalette.Window,
                                     self.palette().highlight())
            opt.rect.translate(-2, 0)
            self.style().drawPrimitive(QtGui.QStyle.PE_IndicatorBranch,
                                       opt, painter, self)
        else:
            index = 0
            if active:
                index = 1
            if expanded:
                self.__downArrowIcon[index].paint(painter, arrowRect)
            else:
                self.__rightArrowIcon[index].paint(painter, arrowRect)

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for top, blockNumber in self.editor.visibleBlocks:
            indic = self.getIndicatorForLine(blockNumber)
            if indic:
                # compute rectangles
                arrowRect = QtCore.QRect(
                    0, top, self.sizeHint().width(), self.sizeHint().height())
                if indic.state == FoldingIndicator.UNFOLDED:
                    h = self.sizeHint().height() * (indic.end - indic.start + 1)
                else:
                    h = self.sizeHint().height()
                foldZoneRect = QtCore.QRect(
                    0, top, self.sizeHint().width(), h)
                # Draw Foldable zone rect
                active = False
                expanded = indic.state == FoldingIndicator.UNFOLDED
                if indic == self.__mouseOveredIndic:
                    active = True
                    c = self.__color
                    grad = QtGui.QLinearGradient(foldZoneRect.topLeft(),
                                                 foldZoneRect.topRight())
                    grad.setColorAt(0, c.lighter(110))
                    grad.setColorAt(1, c.lighter(130))
                    outline = c
                    painter.fillRect(foldZoneRect, grad)
                    painter.setPen(QtGui.QPen(outline))
                    painter.drawLine(foldZoneRect.topLeft() +
                                     QtCore.QPoint(1, 0),
                                     foldZoneRect.topRight() -
                                     QtCore.QPoint(1, 0))
                    painter.drawLine(foldZoneRect.bottomLeft() +
                                     QtCore.QPoint(1, 0),
                                     foldZoneRect.bottomRight() -
                                     QtCore.QPoint(1, 0))
                    painter.drawLine(foldZoneRect.topRight() +
                                     QtCore.QPoint(0, 1),
                                     foldZoneRect.bottomRight() -
                                     QtCore.QPoint(0, 1))
                    painter.drawLine(foldZoneRect.topLeft() +
                                     QtCore.QPoint(0, 1),
                                     foldZoneRect.bottomLeft() -
                                     QtCore.QPoint(0, 1))

                # draw arrow
                self.drawArrow(arrowRect, active, expanded, painter)

    def __clearDecorations(self):
        for d in self.__decorations:
            self.editor.removeDecoration(d)
        self.__decorations[:] = []
        return

    def mouseMoveEvent(self, event):
        line = self.editor.lineNumber(event.pos().y())
        if not line:
            self.__mouseOveredIndic = None
            return
        indic = self.getNearestIndicator(line)
        if indic != self.__mouseOveredIndic:
            self.__mouseOveredIndic = indic
            self.repaint()

    def leaveEvent(self, e):
        self.__mouseOveredIndic = None
        self.repaint()


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit, constants, DelayJobRunner

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.installPanel(FoldingPanel())
            self.foldingPanel.addIndicator(FoldingIndicator(20, 29))
            self.foldingPanel.addIndicator(FoldingIndicator(24, 27))
            fi = FoldingIndicator(30, 45)
            fi.state = fi.FOLDED
            self.foldingPanel.addIndicator(fi)
            self.foldingPanel.zoneOrder = -1

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())

