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
from pcef.core.decoration import TextDecoration
from pcef.core.system import mergedColors, driftColor


class FoldingIndicator(object):
    """
    Defines a folding indicator. A folding indicator, defined by a start and a
    end position can be set in two states:
        - FoldingIndicator.FOLDED
        - FoldingIndicaotr.UNFOLDED
    """
    #: Block unfolded
    UNFOLDED = 0
    #: Block folded
    FOLDED = 1

    def __init__(self, start, end):
        #: Indicator start position
        self.start = start
        #: Indicator end position
        self.end = end
        #: Indicator state (folded, unfolded)
        self.state = FoldingIndicator.UNFOLDED
        self._deco = None


class FoldingPanel(Panel):
    """
    Panel used to draw and fold/unfold text blocks.

    **This panel does not detect foldables blocks of the document, it only
    renders them and let the user fold/unfold a block**

    Client code must manage the folding indicators themselves by using the
    addIndicator, removeIndicator or clearIndicators.

    Client code can also fold/unfold code blocks using the fold and unfold
    method.
    """
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
        """
        Adds two properties to the editor style:
            - nativeFoldingIndicator: to use native indicators or
                                      hardcoded arrows images
            - foldIndicatorBackground: The background color of the fold
              indicator background. Use a os dependant color by default.
        """
        Panel.install(self, editor)
        self.__native = self.editor.style.addProperty("nativeFoldingIndicator",
                                                      True)
        self.__color = self.editor.style.addProperty("foldIndicatorBackground",
                                                     self.__systemColor)
        self.__decoColor = driftColor(
            self.editor.style.value("panelBackground"))

    def onStyleChanged(self, section, key, value):
        Panel.onStyleChanged(self, section, key, value)
        if key == "nativeFoldingIndicator":
            self.__native = self.editor.style.value_from_str(value)
        elif key == "foldIndicatorBackground":
            self.__color = QtGui.QColor(value)
        elif key == "panelBackground":
            self.__decoColor = driftColor(QtGui.QColor(value))

    def resetIndicatorsBackground(self):
        """
        Reset the indicators background to the system (os dependant) color.
        """
        self.editor.style.setValue(
            "foldIndicatorBackground", self.__systemColor)

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

    def getIndicatorForLine(self, line):
        """
        Return the indicator whose start position match the line exactly.

        :param line: The start line of the researched indicator

        :return: FoldingIndicator or None
        """
        for indic in self.__indicators:
            if indic.start == line:
                return indic
        return None

    def getNearestIndicator(self, line):
        """
        Gets the nearest indicator whose range wraps the line parameter.

        :param line: The line to researh

        :return: FoldingIndicator or None
        """
        for indic in reversed(self.__indicators):
            if indic.start <= line <= indic.end:
                return indic
        return None

    def fold(self, foldingIndicator):
        """
        Folds the specified folding indicator

        :param foldingIndicator: The indicator to fold.
        """
        self.__fold(foldingIndicator.start, foldingIndicator.end, fold=True)
        foldingIndicator._deco = TextDecoration(
            self.editor.textCursor(), startLine=foldingIndicator.start)
        foldingIndicator._deco.setOutline(self.__decoColor)
        foldingIndicator._deco.setFullWidth(True)
        self.editor.addDecoration(foldingIndicator._deco)
        foldingIndicator.state = FoldingIndicator.FOLDED

    def unfold(self, foldingIndicator):
        """
        Unfolds the specified folding indicator.

        :param foldingIndicator: The indicator to unfold.
        """
        self.__fold(foldingIndicator.start, foldingIndicator.end, fold=False)
        foldingIndicator.state = FoldingIndicator.UNFOLDED
        self.editor.removeDecoration(foldingIndicator._deco)
        self.__foldRemainings(foldingIndicator)

    def __foldRemainings(self, foldingIndicator):
        """
        Folds the remaining indicator (in case some were folded, unfolding the
        parent will unfold children so we have to restore it).
        """
        found = False
        for indic in self.__indicators:
            if indic == foldingIndicator:
                found = True
                continue
            if found:
                self.__fold(indic.start, indic.end,
                            indic.state == FoldingIndicator.FOLDED)

    def __fold(self, start, end, fold=True):
        """ Folds/Unfolds a block of text delimitted by start/end line numbers

        :param start: Start folding line (this line is not fold, only the next
        ones)

        :param end: End folding line.

        :param fold: True to fold, False to unfold
        """
        print(fold)
        doc = self.editor.document()
        for i in range(start, end):
            block = self.editor.document().findBlockByNumber(i)
            block.setVisible(not fold)
            doc.markContentsDirty(block.position(), block.length())
        self.editor.refreshPanels()

    def __drawArrow(self, arrowRect, active, expanded, painter):
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

    def __drawBackgroundRect(self, foldZoneRect, painter):
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

    def __clearDecorations(self):
        for d in self.__decorations:
            self.editor.removeDecoration(d)
        self.__decorations[:] = []
        return

    def __addDecorationsForIndic(self, indic):
        self.__mouseOveredIndic = indic
        tc = self.editor.textCursor()
        d = TextDecoration(tc, startLine=1, endLine=indic.start)
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__decorations.append(d)
        print(self.editor.lineCount())
        d = TextDecoration(tc, startLine=indic.end+1,
                           endLine=self.editor.lineCount())
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__decorations.append(d)

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)

        if self.__mouseOveredIndic:
            indic = self.__mouseOveredIndic
            h = 0
            if indic.state == FoldingIndicator.UNFOLDED:
                top = (self.editor.linePos(indic.start) -
                       self.sizeHint().height())
            else:
                top = self.editor.linePos(indic.start)
            bottom = self.editor.linePos(indic.end)
            h = bottom - top
            w = self.sizeHint().width()
            self.__drawBackgroundRect(QtCore.QRect(0, top, w, h), painter)

        for top, blockNumber in self.editor.visibleBlocks:
            indic = self.getIndicatorForLine(blockNumber)
            if indic:
                # compute rectangles
                arrowRect = QtCore.QRect(
                    0, top, self.sizeHint().width(), self.sizeHint().height())
                expanded = indic.state == FoldingIndicator.UNFOLDED
                active = indic == self.__mouseOveredIndic
                self.__drawArrow(arrowRect, active, expanded, painter)

    def sizeHint(self):
        """ Returns the widget size hint (based on the editor font size) """
        fm = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(fm.height(), fm.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def mouseMoveEvent(self, event):
        line = self.editor.lineNumber(event.pos().y())
        if not line:
            self.__mouseOveredIndic = None
            return
        indic = self.getNearestIndicator(line)
        if indic != self.__mouseOveredIndic:
            self.__clearDecorations()
            if not indic:
                self.repaint()
                return
            else:
                print("Mouse over")
                self.__addDecorationsForIndic(indic)
                self.repaint()

    def mousePressEvent(self, event):
        if self.__mouseOveredIndic:
            if self.__mouseOveredIndic.state == FoldingIndicator.UNFOLDED:
                self.fold(self.__mouseOveredIndic)
            else:
                self.unfold(self.__mouseOveredIndic)

    def leaveEvent(self, e):
        self.__mouseOveredIndic = None
        self.__clearDecorations()
        self.repaint()


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit, constants

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.installPanel(FoldingPanel())
            self.foldingPanel.addIndicator(FoldingIndicator(21, 40))
            self.foldingPanel.addIndicator(FoldingIndicator(33, 40))
            fi = FoldingIndicator(43, 351)
            self.foldingPanel.addIndicator(fi)
            self.foldingPanel.fold(fi)
            self.foldingPanel.zoneOrder = -1

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())

