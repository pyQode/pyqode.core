#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the marker panel
"""
from pyqode.qt import QtCore, QtGui
from pyqode.core import constants
from pyqode.core.panel import Panel
from pyqode.core.decoration import TextDecoration
from pyqode.core.system import mergedColors, driftColor, DelayJobRunner


class _FoldingIndicator(object):
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

    def __init__(self):
        #: Indicator start position
        self.start = -1
        #: Indicator end position
        self.end = -1
        #: Indicator state (folded, unfolded)
        self.folded = False
        self.foldIndent = -1  # the fold indent value for the region to fold

    def __repr__(self):
        return "%d - %d" % (self.start, self.end)


class FoldingPanel(Panel):
    """
    This panel draws folding indicators and manage user interaction with those
    indicators.

    All you have to do is setup a :class:`pyqode.core.FoldDetector` on the
    syntax highlighter (the pygments highlighter does this automatically for
    you if you let him do) and install a folding panel.

    Here the properties added by the mode to
    :attr:`pyqode.core.QCodeEdit.style`:

    .. note:: This panel does not detect foldables blocks of the document,
              it only renders them and let the user fold/unfold a block
    """
    #: The panel descriptip,
    DESCRIPTION = "Manage and draw folding indicators"
    #: The panel identifier
    IDENTIFIER = "foldingPanel"

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
        self.__hoveredStartLine = -1
        self.__rightArrowIcon = (QtGui.QIcon(constants.ICON_ARROW_RIGHT[0]),
                                 QtGui.QIcon(constants.ICON_ARROW_RIGHT[1]))
        self.__downArrowIcon = (QtGui.QIcon(constants.ICON_ARROW_DOWN[0]),
                                QtGui.QIcon(constants.ICON_ARROW_DOWN[1]))
        self.__scopeDecorations = []
        self.__foldDecorations = []
        self.__updateRequested = False
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=1000)
        self._foldedBoxes = []

        self.__previousBoxLine = -1

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

    def _onStateChanged(self, state):
        Panel._onStateChanged(self, state)
        if state:
            self.editor.painted.connect(self._drawFoldedPopup)
            self.editor.mouseMoved.connect(self.__onEditorMouseMove)
            self.editor.mousePressed.connect(self.__onEditorMousePress)
            self.editor.updateRequest.connect(self.__updateDirtyLines)
        else:
            self.editor.painted.disconnect(self._drawFoldedPopup)
            self.editor.mouseMoved.disconnect(self.__onEditorMouseMove)
            self.editor.mousePressed.disconnect(self.__onEditorMousePress)

    def _onStyleChanged(self, section, key):
        Panel._onStyleChanged(self, section, key)
        if key == "nativeFoldingIndicator" or not key:
            self.__native = self.editor.style.value("nativeFoldingIndicator")
            key = None
            self.repaint()
        if key == "foldIndicatorBackground" or not key:
            self.__color = self.editor.style.value("foldIndicatorBackground")
            self.repaint()
        if key == "background" or not key:
            self.__decoColor = driftColor(
                self.editor.palette().window().color())
            self.repaint()

    def resetIndicatorsBackground(self):
        """
        Resets the indicators background to the system (os dependant) color.
        """
        self.editor.style.setValue(
            "foldIndicatorBackground", self.__systemColor)

    @staticmethod
    def __foldBlock(b):
        usd = b.userData()
        usd.folded = True
        b.setUserData(usd)

    @staticmethod
    def __unfoldBlock(b):
        usd = b.userData()
        if usd:
            usd.folded = False
            b.setUserData(usd)

    def fold(self, foldingIndicator):
        """
        Folds the specified folding indicator

        :param foldingIndicator: The indicator to fold.
        """
        b = self.editor.document().findBlockByNumber(foldingIndicator.start - 1)
        self.__foldBlock(b)
        last = -1
        for i in range(foldingIndicator.start, foldingIndicator.end):
            last = i
            block = self.editor.document().findBlockByNumber(i)
            usrData = block.userData()
            if (usrData.foldIndent >= foldingIndicator.foldIndent or
                    not len(block.text().strip()) or usrData.foldIndent == -1):
                block.setVisible(False)
                if usrData.foldIndent == foldingIndicator.foldIndent:
                    if not usrData.foldStart:
                        usrData.folded = True
                block.setUserData(usrData)
            else:
                break
        # unfold last blank lines
        for i in reversed(range(foldingIndicator.start, last)):
            block = self.editor.document().findBlockByNumber(i)
            foldIndent = block.userData().foldIndent
            if not len(block.text().strip()) and foldIndent != foldingIndicator.foldIndent:
                block.setVisible(True)
            else:
                break
        self.editor.markWholeDocumentDirty()
        self.__collectIndicators()
        self.__clearScopeDecorations()
        self.__addScopeDecoration(foldingIndicator.start,
                                  foldingIndicator.start)
        # self.repaint()
        self.editor.refreshPanels()

    def unfoldChild(self, end, i, usrData):
        for j in range(i + 1, end):
            b = self.editor.document().findBlockByNumber(j)
            ud = b.userData()
            if ud.foldIndent <= usrData.foldIndent:
                return
            if len(b.text().strip()):
                if ud.foldStart:
                    b.setVisible(not usrData.folded)
                    if not ud.folded:
                        self.unfoldChild(end, j, ud)
                else:
                    if not ud.folded:
                        b.setVisible(not usrData.folded)
                    else:
                        b.setVisible(not ud.folded)
            else:
                b.setVisible(True)

    def unfold(self, indic):
        """
        Unfolds the specified folding indicator.

        :param indic: The indicator to unfold.
        """
        start = indic.start
        end = indic.end
        foldIndent = indic.foldIndent
        b = self.editor.document().findBlockByNumber(start - 1)
        self.__unfoldBlock(b)
        for i in range(start, end):
            if i == 64:
                pass
            block = self.editor.document().findBlockByNumber(i)
            usrData = block.userData()
            if usrData.foldIndent == foldIndent:
                block.setVisible(True)
                if usrData.foldStart:
                    self.unfoldChild(end, i, usrData)
                else:
                    usrData.folded = False
            elif not len(block.text().strip()):
                if usrData.foldIndent == -1:
                    block.setVisible(True)
                else:
                    block.setVisible(False)
            block.setUserData(usrData)
        self.editor.markWholeDocumentDirty()
        self.__collectIndicators()
        self.__clearScopeDecorations()
        self.__addScopeDecoration(start, end)
        # self.repaint()
        self.editor.refreshPanels()

    @staticmethod
    def __unfoldPreviousBlankLines(b):
        # unfold previous blank lines as they are on the level 0
        prevBlock = b.previous()
        while prevBlock and prevBlock.isValid() and \
                        len(prevBlock.text().strip()) == 0:
            prevBlock.setVisible(True)
            pusd = prevBlock.userData()
            pusd.folded = False
            prevBlock = prevBlock.previous()

    def foldAll(self):
        """ Folds all indicators who have a fold indent > 0 """
        b = self.editor.document().firstBlock()
        while b and b.isValid():
            if b.blockNumber() == 602:
                pass
            usd = b.userData()
            if usd.foldIndent == 0:  # indicator start
                self.__unfoldPreviousBlankLines(b)
                self.__foldBlock(b)
            else:
                if b != self.editor.document().lastBlock():
                    b.setVisible(False)
                    usd.folded = True
                    if usd.foldStart:
                        self.__foldBlock(b)
                else:
                    # unfold previous blank lines
                    self.__unfoldPreviousBlankLines(b)
            b = b.next()
        self.editor.markWholeDocumentDirty()
        self.editor.updateVisibleBlocks(None)
        self.__collectIndicators()
        self.editor.refreshPanels()

    def unfoldAll(self):
        """ Unfolds all indicators who have a fold indent > 0 """
        b = self.editor.document().firstBlock()
        while b and b.isValid():
            usd = b.userData()
            # if usd.foldIndent > 0 or len(b.text().strip()) == 0:
            b.setVisible(True)
            usd.folded = False
            b = b.next()
            # if usd.foldStart:
            self.__unfoldBlock(b)
        self.editor.markWholeDocumentDirty()
        self.editor.updateVisibleBlocks(None)
        self.__collectIndicators()
        self.editor.update()

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

    def __getIndicatorForStart(self, line):
        for indic in self.__indicators:
            if indic.start == line:
                return indic
        return None

    def __drawArrow(self, arrowRect, active, expanded, painter):
        """
        Draw the indicator arrow.

        If native is true, the os primitive (PE_IndicatorBranch is used), else
        custom pyqode triangles are used.

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
                         QtCore.QPointF(1, 0),
                         foldZoneRect.topRight() -
                         QtCore.QPointF(1, 0))
        painter.drawLine(foldZoneRect.bottomLeft() +
                         QtCore.QPointF(1, 0),
                         foldZoneRect.bottomRight() -
                         QtCore.QPointF(1, 0))
        painter.drawLine(foldZoneRect.topRight() +
                         QtCore.QPointF(0, 1),
                         foldZoneRect.bottomRight() -
                         QtCore.QPointF(0, 1))
        painter.drawLine(foldZoneRect.topLeft() +
                         QtCore.QPointF(0, 1),
                         foldZoneRect.bottomLeft() -
                         QtCore.QPointF(0, 1))

    def __clearScopeDecorations(self):
        """
        Clear all decorations (scope highlight decorations)
        """
        for d in self.__scopeDecorations:
            self.editor.removeDecoration(d)
        self.__scopeDecorations[:] = []
        return

    def __addScopeDecoration(self, start, end):
        """
        Show a scope decoration on the editor widget

        :param start: Start line
        :param end: End line
        """
        self.__decoColor = driftColor(self.editor.palette().base().color())
        tc = self.editor.textCursor()
        d = TextDecoration(tc, startLine=1, endLine=start)
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__scopeDecorations.append(d)
        d = TextDecoration(tc, startLine=end + 1,
                           endLine=self.editor.lineCount())
        d.setFullWidth(True, clear=False)
        d.setBackground(self.__decoColor)
        self.editor.addDecoration(d)
        self.__scopeDecorations.append(d)

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

    @staticmethod
    def __findNextValidBlock(block):
        bl = block.next()
        while len(bl.text().strip()) == 0:
            n = bl.next()
            if n.isValid():
                bl = n
            else:
                break
        return bl

    def __collectIndicators(self):
        self.__indicators = []
        for i, b in enumerate(self.editor.visibleBlocks):
            top, line, block = b[0], b[1], b[2]
            if not len(block.text()):
                continue
            bl = self.__findNextValidBlock(block)
            nxtUsrData = bl.userData()
            usrData = block.userData()
            if nxtUsrData and usrData and usrData.foldIndent != -1:
                # is it a folding start
                if nxtUsrData.foldIndent > usrData.foldIndent:
                    arrowRect = QtCore.QRect(0, top, self.sizeHint().width(),
                                             self.sizeHint().height())
                    fi = _FoldingIndicator()
                    fi.start = line
                    fi.folded = usrData.folded
                    fi.end = self.editor.lineCount() - 1
                    fi.rect = arrowRect
                    fi.active = False
                    fi.foldIndent = nxtUsrData.foldIndent
                    fi.text = block.text()
                    # find its end
                    stopAtEnds = True
                    nline = 0
                    nblock = None
                    for ntop, nline, nblock in self.editor.visibleBlocks[
                                               i + 1:len(
                                                       self.editor.visibleBlocks) - 1]:
                        if not len(nblock.text().strip()):
                            continue
                        nUsrData = nblock.userData()
                        if usrData.foldIndent >= nUsrData.foldIndent:
                            stopAtEnds = False
                            break
                    if not stopAtEnds:
                        # avoid empty lines
                        stop = nline - 1
                        lastBlock = nblock.previous()
                        while len(lastBlock.text().strip()) == 0:
                            lastBlock = lastBlock.previous()
                            stop -= 1
                        fi.end = stop
                    # select code
                    d = TextDecoration(self.editor.textCursor(),
                                   startLine=fi.start+1,
                                   endLine=fi.end)
                    fi.tooltip = d.cursor.selection().toPlainText()
                    self.__indicators.append(fi)

    def __drawActiveIndicatorBackground(self, fi, painter):
        # draw background rect
        if not fi.folded:
            top = (self.editor.linePos(fi.start) -
                   self.sizeHint().height())
        else:
            top = self.editor.linePos(fi.start)
        bottom = self.editor.linePos(fi.end)
        h = bottom - top
        w = self.sizeHint().width()
        self.__drawBackgroundRect(QtCore.QRectF(0, top, w, h), painter)

    def _drawFoldedPopup(self):
        #if self.editor.hasFocus():
        self.__collectIndicators()
        self._foldedBoxes[:] = []
        painter = QtGui.QPainter(self.editor.viewport())
        for fi in self.__indicators:
            if fi.folded:
                font = self.editor.currentCharFormat().font()
                fm = QtGui.QFontMetricsF(font)
                pos = len(fi.text)
                offset = self.editor.contentOffset().x() + \
                    self.editor.document().documentMargin()
                charW = fm.width(' ')
                left = round(charW * pos) + offset + charW
                top = fi.rect.top() + 1
                w = 5 * charW
                h = fi.rect.height() - 2
                rect = QtCore.QRectF(left, top, w, h)
                painter.drawRoundedRect(rect, 3, 3)
                painter.drawText(left + charW, top + 2 * h / 3, "...")
                self._foldedBoxes.append((fi, rect))

    def __onEditorMouseMove(self, event):
        for fi, box in self._foldedBoxes:
            result = box.contains(event.posF())
            l = self.editor.lineNumber(event.pos().y())
            if result:
                if l != self.__previousBoxLine:
                    self.editor.setCursor(QtCore.Qt.PointingHandCursor)
                    self.__previousBoxLine = l
                return
        if self.__previousBoxLine != -1:
            self.__previousBoxLine = -1
            self.editor.setCursor(QtCore.Qt.IBeamCursor)

    def __onEditorMousePress(self, event):
        for fi, box in self._foldedBoxes:
            result = box.contains(event.posF())
            if result:
                self.unfold(fi)
                self.__clearScopeDecorations()

    def paintEvent(self, event):
        """
        Paint the indicators arrow + active indicator background zone.

        :param event:
        """
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for d in self.__foldDecorations:
            self.editor.removeDecoration(d)
        self.__foldDecorations[:] = []
        for fi in self.__indicators:
            fi.active = False
            if fi.start == self.__hoveredStartLine:
                fi.active = True
                self.__drawActiveIndicatorBackground(fi, painter)
            self.__drawArrow(fi.rect, fi.active, not fi.folded, painter)

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
            # self.__mouseOveredIndic = None
            return
        indic = self.__getNearestIndicator(line)
        if not indic:
            self.__hoveredStartLine = -1
            self.__clearScopeDecorations()
            self.repaint()
            self.editor.repaint()
        else:
            if self.__hoveredStartLine != indic.start:
                self.__clearScopeDecorations()
                self.__hoveredStartLine = indic.start
                self.__addScopeDecoration(indic.start, indic.end)
                self.repaint()

    def mousePressEvent(self, event):
        """ Folds/unfolds the pressed indicator if any. """
        if self.__hoveredStartLine != -1:
            indic = self.__getIndicatorForStart(self.__hoveredStartLine)
            if not indic:
                return
            if indic.folded:
                # pass
                self.unfold(indic)
                # indic.folded = False
            else:
                self.fold(indic)
            indic.folded = not indic.folded

    def leaveEvent(self, e):
        """
        Reset the mouse overed indic to None and clear scope decoration when
        the user leaves the foldingPanel
        """
        self.__hoveredStartLine = None
        self.__clearScopeDecorations()
        self.repaint()

    def __updateDirtyLines(self, rect, dy):
        if dy:
            self.editor.updateVisibleBlocks(None)
            for top, line, block in self.editor.visibleBlocks:
                usd = block.userData()
                if usd.foldStart and usd.folded:
                    self.editor.markWholeDocumentDirty()


if __name__ == '__main__':
    from pyqode.core import QGenericCodeEdit

    class Example(QGenericCodeEdit):
        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.installPanel(FoldingPanel())
            self.foldingPanel.addIndicator(_FoldingIndicator(21, 40))
            self.foldingPanel.addIndicator(_FoldingIndicator(33, 40))
            fi = _FoldingIndicator(43, 351)
            self.foldingPanel.addIndicator(fi)
            self.foldingPanel.fold(fi)
            self.foldingPanel.zoneOrder = -1

    import sys

    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
