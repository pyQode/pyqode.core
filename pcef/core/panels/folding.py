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

    class _BlockFoldData(QtGui.QTextBlockUserData):
        def __init__(self, folded=False):
            QtGui.QTextBlockUserData.__init__(self)
            self.folded = folded

    @property
    def indicators(self):
        retVal = []
        for indic in self.__indicators:
            retVal.append(indic)
        return retVal

    def getSystemColor(self):
        pal = self.editor.palette()
        b = pal.window().color()
        h = pal.highlight().color()
        return mergedColors(b, h, 50)

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
        self.__decorations = []
        self.__updateRequested = False

    def _onInstall(self, editor):
        """
        Adds two properties to the editor style:
            - nativeFoldingIndicator: to use native indicators or
                                      hardcoded arrows images
            - foldIndicatorBackground: The background color of the fold
              indicator background. Use a os dependant color by default.
        """
        Panel._onInstall(self, editor)
        self.__native = self.editor.style.addProperty("nativeFoldingIndicator",
                                                      True)
        self.__color = self.editor.style.addProperty("foldIndicatorBackground",
                                                     self.getSystemColor())
        self.__decoColor = driftColor(self.editor.palette().window().color())
        self.__installActions()

    def _onStyleChanged(self, section, key):
        Panel._onStyleChanged(self, section, key)
        if key == "nativeFoldingIndicator" or not key:
            self.__native = self.editor.style.value("nativeFoldingIndicator")
            key = None
        if key == "foldIndicatorBackground" or not key:
            self.__color = self.editor.style.value("foldIndicatorBackground")
        if key == "background" or not key:
            self.__decoColor = driftColor(
                self.editor.palette().window().color())

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
        self.__updateRequested = True

    def removeIndicator(self, indicator):
        """
        Removes the marker from the panel

        :param indicator: Marker to remove
        """
        if indicator.state == indicator.FOLDED:
            self.unfold(indicator)
        self.__indicators.remove(indicator)
        self.__updateRequested = True

    def clearIndicators(self):
        """ Clears the markers list """
        for foldingIndicator in self.__indicators:
            if foldingIndicator.state == foldingIndicator.FOLDED:
                self.editor.removeDecoration(foldingIndicator._deco)
        self.__indicators[:] = []
        self.__updateRequested = True

    def fold(self, foldingIndicator):
        """
        Folds the specified folding indicator

        :param foldingIndicator: The indicator to fold.
        """
        self.__fold(foldingIndicator, fold=True)
        foldingIndicator._deco = TextDecoration(
            self.editor.textCursor(), startLine=foldingIndicator.start)
        d = TextDecoration(self.editor.textCursor(),
                           startLine=foldingIndicator.start+1,
                           endLine=foldingIndicator.end)
        foldingIndicator._deco.tooltip = d.cursor.selection().toPlainText()
        foldingIndicator._deco.cursor.select(QtGui.QTextCursor.LineUnderCursor)
        self.__decoColor = driftColor(self.editor.palette().base().color())
        foldingIndicator._deco.setOutline(self.__decoColor)
        foldingIndicator._deco.signals.clicked.connect(self.__onDecoClicked)
        self.editor.addDecoration(foldingIndicator._deco)
        foldingIndicator.state = FoldingIndicator.FOLDED

    def unfold(self, foldingIndicator):
        """
        Unfolds the specified folding indicator.

        :param foldingIndicator: The indicator to unfold.
        """
        self.__fold(foldingIndicator, fold=False)
        foldingIndicator.state = FoldingIndicator.UNFOLDED
        self.editor.removeDecoration(foldingIndicator._deco)
        foldingIndicator._deco.signals.clicked.disconnect(self.__onDecoClicked)
        self.__foldRemainings(foldingIndicator)

    def foldAll(self):
        """ Folds all indicators """
        for foldingIndicator in reversed(self.__indicators):
            if foldingIndicator.state == foldingIndicator.UNFOLDED:
                self.fold(foldingIndicator)

    def unfoldAll(self):
        """ Unfolds all indicators """
        for foldingIndicator in reversed(self.__indicators):
            if foldingIndicator.state == foldingIndicator.FOLDED:
                self.unfold(foldingIndicator)

    def __getIndicatorForLine(self, line):
        """
        Return the indicator whose start position match the line exactly.

        :param line: The start line of the researched indicator

        :return: FoldingIndicator or None
        """
        for indic in self.__indicators:
            if indic.start == line:
                return indic
        return None

    def __getNearestIndicator(self, line):
        """
        Gets the nearest indicator whose range wraps the line parameter.

        :param line: The line to researh

        :return: FoldingIndicator or None
        """
        for indic in reversed(self.__indicators):
            if indic.start <= line <= indic.end:
                return indic
        return None

    def __getIndicatorState(self, foldingIndicator):
        """
        Checks the QTextBlock states and determine if the foldingIndicator is
        folded or not.
        """
        if (not foldingIndicator.start or not foldingIndicator.end or
                foldingIndicator.start > foldingIndicator.end):
            return foldingIndicator.UNFOLDED
        for i in range(foldingIndicator.start, foldingIndicator.end):
            if not self.__isShared(i, foldingIndicator):
                block = self.editor.document().findBlockByNumber(i)
                data = block.userData()
                if data and data.folded:
                    return foldingIndicator.FOLDED
        return foldingIndicator.UNFOLDED

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
                self.__fold(indic, indic.state == FoldingIndicator.FOLDED)

    def __fold(self, foldingIndicator, fold=True):
        """
        Folds/Unfolds a block of text delimitted by start/end line numbers.

        Hides/show the text block and set a custom user data to remember its
        state.

        :param start: Start folding line (this line is not fold, only the next
        ones)

        :param end: End folding line.

        :param fold: True to fold, False to unfold
        """
        doc = self.editor.document()
        for i in range(foldingIndicator.start, foldingIndicator.end):
            block = self.editor.document().findBlockByNumber(i)
            block.setVisible(not fold)
            if not self.__isShared(i, foldingIndicator):
                block.setUserData(FoldingPanel._BlockFoldData(folded=fold))
        tc = self.editor.textCursor()
        tc.select(tc.Document)
        doc.markContentsDirty(tc.selectionStart(), tc.selectionEnd())
        self.editor.refreshPanels()

    def __isShared(self, lineNbr, owner):
        """
        Checks if a line number is shared by another FoldingIndicator.

        :param lineNbr: The line number to check

        :param owner: The current lineNumber owner (FoldingIndicator)

        :return: True if the lineNbr is shared, False if the line number is
                 only used for the owner indicator
        """
        for indic in reversed(self.__indicators):
            if indic == owner:
                return False
            if indic.start <= lineNbr <= indic.end:
                return True
        return False

    def __onDecoClicked(self, deco):
        """
        Unfolds indicator if the editor decoration is clicked

        :param deco: The clicked decoration
        """
        fi = self.__getIndicatorForLine(deco.cursor.blockNumber()+1)
        if fi and fi.state == fi.FOLDED:
            self.unfold(fi)

    def __updateIndicatorsStates(self):
        """
        Update indicators states. If the indicator state is UNFOLDED but the
        QTextBlock its uses are folded, then we fold the indicator. This allow
        to easily update the list of indicators without worrying about their
        states.

        This method is called on paint event if the user added/removed/clear
        indicators.
        """
        for indicator in self.__indicators:
            if self.__getIndicatorState(indicator) == FoldingIndicator.FOLDED:
                if indicator.state == FoldingIndicator.UNFOLDED:
                    self.fold(indicator)

    def __drawArrow(self, arrowRect, active, expanded, painter):
        """
        Draw the indicator arrow.

        If native is true, the os primitive (PE_IndicatorBranch is used), else
        custom pcef triangles are used.

        :param arrowRect: The rectangle where to draw the arrow

        :param active: Is the arrow active (mouse hover)?

        :param expanded: Is the indicator expanded (unfolded) or not (folded).

        :param painter: The widget's painter.
        """
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
        """
        Draw the background rectangle using the current style primitive color
        or foldIndicatorBackground if nativeFoldingIndicator is true.

        :param foldZoneRect: The fold zone rect to draw

        :param painter: The widget's painter.
        """
        c = self.__color
        if self.__native:
            c = self.getSystemColor()
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
        """
        Clear all decorations (scope highlight decorations)
        """
        for d in self.__decorations:
            self.editor.removeDecoration(d)
        self.__decorations[:] = []
        return

    def __addDecorationsForIndic(self, indic):
        """
        Sets a TextDecoration for the folded indicator.

        :param indic: Indic to setup.
        """
        self.__mouseOveredIndic = indic
        self.__decoColor = driftColor(self.editor.palette().base().color())
        tc = self.editor.textCursor()
        d = TextDecoration(tc, startLine=1, endLine=indic.start)
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__decorations.append(d)
        d = TextDecoration(tc, startLine=indic.end+1,
                           endLine=self.editor.lineCount())
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__decorations.append(d)

    def __installActions(self):
        """ Installs fold all and unfold all action on the editor widget. """
        self.editor.addSeparator()
        self.__actionFoldAll = QtGui.QAction("Fold all", self.editor)
        self.__actionFoldAll.setShortcut("Ctrl+Shift+-")
        self.__actionFoldAll.triggered.connect(self.foldAll)
        self.editor.addAction(self.__actionFoldAll)
        self.__actionUnfoldAll = QtGui.QAction("Unfold all", self.editor)
        self.__actionUnfoldAll.setShortcut("Ctrl+Shift++")
        self.__actionUnfoldAll.triggered.connect(self.unfoldAll)
        self.editor.addAction(self.__actionUnfoldAll)

    def paintEvent(self, event):
        """
        Paint the indicators arrow + active indicator background zone.

        :param event:
        """
        Panel.paintEvent(self, event)
        if self.__updateRequested:
            self.__updateIndicatorsStates()
            self.__updateRequested = False
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
            indic = self.__getIndicatorForLine(blockNumber)
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
        """
        Detect mouser over indicator and highlight the current scope in the
        editor (up and down decoration arround the foldable text when the mouse
        is over an indicator).

        :param event:
        """
        Panel.mouseMoveEvent(self, event)
        line = self.editor.lineNumber(event.pos().y())
        if not line:
            self.__mouseOveredIndic = None
            return
        indic = self.__getNearestIndicator(line)
        if indic != self.__mouseOveredIndic:
            self.__clearDecorations()
            if not indic:
                self.repaint()
                return
            else:
                self.__addDecorationsForIndic(indic)
                self.repaint()

    def mousePressEvent(self, event):
        """ Folds/unfolds the pressed indicator if any. """
        if self.__mouseOveredIndic:
            if self.__mouseOveredIndic.state == FoldingIndicator.UNFOLDED:
                self.fold(self.__mouseOveredIndic)
            else:
                self.unfold(self.__mouseOveredIndic)

    def leaveEvent(self, e):
        """
        Reset the mouse overed indic to None and clear scope decoration when
        the user leaves the foldingPanel
        """
        self.__mouseOveredIndic = None
        self.__clearDecorations()
        self.repaint()


if __name__ == '__main__':
    from pcef.core import QGenericCodeEdit

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
