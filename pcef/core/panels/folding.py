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
from pcef.core.panel import Panel


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
        if line == 28:
            print("Break")
        for indic in reversed(self.__indicators):
            if indic.start <= line <= indic.end:
                return indic
        return None

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for top, blockNumber in self.editor.visibleBlocks:
            indic = self.getIndicatorForLine(blockNumber)
            if indic:
                arrowRect = QtCore.QRect(
                    0, top, self.sizeHint().width(), self.sizeHint().height())
                # if indic.state == FoldingIndicator.UNFOLDED:

                if indic.state == FoldingIndicator.UNFOLDED:
                    h = self.sizeHint().height() * (indic.end - indic.start + 1)
                else:
                    h = self.sizeHint().height()
                print(h)
                foldZoneRect = QtCore.QRect(
                    0, top, self.sizeHint().width(), h)
                # Draw Foldable zone rect
                opt = QtGui.QStyleOption()
                if indic == self.__mouseOveredIndic:
                    opt.rect = foldZoneRect
                    opt.state = QtGui.QStyle.State_HasFocus
                    self.style().drawPrimitive(QtGui.QStyle.PE_FrameFocusRect,
                                               opt, painter, self)
                # draw arrow
                opt.rect = QtCore.QRect(arrowRect)
                elem = QtGui.QStyle.PE_IndicatorArrowDown
                if indic.state == FoldingIndicator.FOLDED:
                    elem = QtGui.QStyle.PE_IndicatorArrowRight
                self.style().drawPrimitive(elem, opt, painter, self)

    def mouseMoveEvent(self, event):
        line = self.editor.lineNumber(event.pos().y())
        if not line:
            self.__mouseOveredIndic = None
            return
        indic = self.getNearestIndicator(line)
        if indic != self.__mouseOveredIndic:
            self.__mouseOveredIndic = indic
            print("Mouse over")
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
            self.foldingPanel.addIndicator(FoldingIndicator(18, 27))
            self.foldingPanel.addIndicator(FoldingIndicator(22, 25))
            fi = FoldingIndicator(28, 45)
            fi.state = fi.FOLDED
            self.foldingPanel.addIndicator(fi)
            self.foldingPanel.zoneOrder = -1

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())

