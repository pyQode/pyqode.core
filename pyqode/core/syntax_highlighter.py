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
Base class for pyqode syntax hightlighters
"""
import os
from pyqode.core.mode import Mode
from pyqode.core.textblockuserdata import TextBlockUserData, ParenthesisInfo
from pyqode.qt import QtGui, QtCore


class FoldDetector(object):
    """
    Abstract base class for fold indicators.


    A fold detector take care of detecting the folding indent of a specific text
    block.


    A code folding marker will appear the line *before* the one where the
    indention level increases. The code folding region will end in the last
    line that has the same indention level (or higher), skipping blank lines.


    You **must** override the :meth:`pyqode.core.FoldDetector.getFoldIndent`
    method to create a custom fold detector.
    """

    def getFoldIndent(self, highlighter, block, text):
        """
        Return the fold indent of a QTextBlock

        A code folding marker will appear the line *before* the one where the
        indention level increases.
        The code folding reagion will end in the last line that has the same
        indention level (or higher).

        :param highlighter: Reference to the highlighter
        :type highlighter: pyqode.core.SyntaxHighlighter

        :param block: Block to parse
        :type block: QtGui.QTextBlock

        :param text: Text of the block (for convenience)
        :type text: str

        :return: The fold indent
        :rtype: int
        """
        raise NotImplementedError()

    @staticmethod
    def isFoldStart(currentBlock, nextBlock):
        currUsd = currentBlock.userData()
        nextUsd = nextBlock.userData()
        if currUsd.foldIndent < nextUsd.foldIndent:
            return True


class IndentBasedFoldDetector(FoldDetector):
    """
    Perform folding detection based on the line indentation level.

    Suitable for languages such as python, cython, batch, data interchange
    formats such as xml and json or even markup languages (html, rst).

    It does not work well with c based languages nor with vb or ruby.
    """
    def getFoldIndent(self, highlighter, block, text):
        pb = block.previous()
        if pb:
            ptxt = pb.text().rstrip()
            if(ptxt.endswith("(") or ptxt.endswith(",") or
               ptxt.endswith("\\") or ptxt.endswith("+") or
               ptxt.endswith("-") or ptxt.endswith("*") or
               ptxt.endswith("/") or ptxt.endswith("and") or
               ptxt.endswith("or")):
                return pb.userData().foldIndent
        stripped = len(text.strip())
        if stripped:
            return int((len(text) - len(text.lstrip())))
        else:
            while not len(pb.text().strip()) and pb.isValid():
                pb = pb.previous()
            pbIndent = (len(pb.text()) - len(pb.text().lstrip()))
            # check next blocks to see if their indent is >= then the last block
            nb = block.next()
            while not len(nb.text().strip()) and nb.isValid():
                nb = nb.next()
            nbIndent = (len(nb.text()) - len(nb.text().lstrip()))
            # print(pb.userState())
            if nbIndent >= pbIndent or pb.userState() & 0x7F:
                if pb.userData():
                    return nbIndent
            return -1


class CharBasedFoldDetector(FoldDetector):
    """
    Detects folding based on character triggers

    Suitable for c family languages (c, c++, C#, java, D, ...)
    """
    def __init__(self, start='{', end='}'):
        self._start = start
        self._end = end

    def getFoldIndent(self, highlighter, block, text):
        pb = block.previous()
        if block.blockNumber() == 34:
            pass
        while pb and pb.isValid() and not len(pb.text().strip()):
            pb = pb.previous()
        if pb and pb.isValid():
            txt = pb.text()
            usd = pb.userData()
            stext = text.strip()
            if stext.startswith(self._start):
                return usd.foldIndent + 1
            else:
                # fold start
                if self._start in txt and not self._end in txt:
                    stext = txt.strip()
                    if not stext.startswith(self._start):
                        return usd.foldIndent + 1
                    else:
                        return usd.foldIndent
                # fold end
                elif self._end in txt and not self._start in txt:
                    usd = pb.userData()
                    return usd.foldIndent - 1
                else:
                    # same folding level as the previous block
                    nb = block.next()
                    while nb.isValid() and not len(nb.text().strip()):
                        nb = nb.next()
                    if nb.isValid() and self._start in nb.text() and not len(text.strip()):
                        return usd.foldIndent + 1
                    return usd.foldIndent
        else:
            return 0


class SyntaxHighlighter(QtGui.QSyntaxHighlighter, Mode):
    """
    Abstract Base class for syntax highlighter modes.

    It fills up the document with our custom user data, setup the parenthesis
    infos and run the FoldDetector on every text block. It **does not do any
    syntax highlighting**, this task is left to the sublasses such as
    :class:`pyqode.core.PygmentsSyntaxHighlighter`.

    Subclasses **must** override the
    :meth:`pyqode.core.SyntaxHighlighter.doHighlight` method to apply custom
    highlighting.

    **Signals**:
        - :attr:`pyqode.core.SyntaxHighlighter.blockHighlightStarted`
        - :attr:`pyqode.core.SyntaxHighlighter.blockHighlightFinished`

    .. warning:: You should always inherit from this class to create a new
                 syntax. **Never inherit directly from QSyntaxHighlighter.**
    """
    #: Mode identifier
    IDENTIFIER = "syntaxHighlighterMode"

    #: Signal emitted at the start of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    blockHighlightStarted = QtCore.Signal(object, object)

    #: Signal emitted at the end of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    blockHighlightFinished = QtCore.Signal(object, object)

    def __init__(self, parent, foldDetector=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        Mode.__init__(self)
        self._spacesExpression = QtCore.QRegExp('\s+')
        if os.environ["QT_API"] == "PyQt4":
            # there is a bug with QTextBlockUserData in PyQt4, we need to
            # keep a reference on them, otherwise they are removed from memory.
            self.__blocks = set()
        self._foldDetector = foldDetector

    def __del__(self):
        if os.environ["QT_API"] == "PyQt4":
            self.__blocks.clear()

    def setFoldDetector(self, foldDetector):
        """
        Setup the fold detector object to use to detect fold indents.

        :param foldDetector: FoldDetector
        :type foldDetector: pyqode.core.FoldDetector
        """
        self._foldDetector = foldDetector

    def _detectFolding(self, text, userData):
        """
        Detect folding indents using a foldDetector.
        """
        # Collect folding informations
        if self._foldDetector:
            userData.foldIndent = self._foldDetector.getFoldIndent(
                self, self.currentBlock(), text)
            prevBlock = self.currentBlock().previous()
            if prevBlock and prevBlock.isValid():
                # skip blank lines
                while (prevBlock and prevBlock.isValid() and
                               len(prevBlock.text().strip()) == 0):
                    prevBlock = prevBlock.previous()
                prevUsd = prevBlock.userData()
                if prevUsd:
                    prevUsd.foldStart = self._foldDetector.isFoldStart(
                        prevBlock, self.currentBlock())
                prevBlock.setUserData(prevUsd)

    @staticmethod
    def _detectParentheses(text, userData):
        userData.parentheses[:] = []
        userData.squareBrackets[:] = []
        userData.braces[:] = []
        # todo check if bracket is not into a string litteral
        # parentheses
        leftPos = text.find("(", 0)
        while leftPos != -1:
            info = ParenthesisInfo(leftPos, "(")
            userData.parentheses.append(info)
            leftPos = text.find("(", leftPos + 1)
        rightPos = text.find(")", 0)
        while rightPos != -1:
            info = ParenthesisInfo(rightPos, ")")
            userData.parentheses.append(info)
            rightPos = text.find(")", rightPos + 1)
        # braces
        leftPos = text.find("{", 0)
        while leftPos != -1:
            info = ParenthesisInfo(leftPos, "{")
            userData.braces.append(info)
            leftPos = text.find("{", leftPos + 1)
        rightPos = text.find("}", 0)
        while rightPos != -1:
            info = ParenthesisInfo(rightPos, "}")
            userData.braces.append(info)
            rightPos = text.find("}", rightPos + 1)
        # squareBrackets
        leftPos = text.find("[", 0)
        while leftPos != -1:
            info = ParenthesisInfo(leftPos, "[")
            userData.squareBrackets.append(info)
            leftPos = text.find("[", leftPos + 1)
        rightPos = text.find("]", 0)
        while rightPos != -1:
            info = ParenthesisInfo(rightPos, "]")
            userData.squareBrackets.append(info)
            rightPos = text.find("]", rightPos + 1)
        userData.parentheses[:] = sorted(
            userData.parentheses, key=lambda x: x.position)
        userData.squareBrackets[:] = sorted(
            userData.squareBrackets, key=lambda x: x.position)
        userData.braces[:] = sorted(
            userData.braces, key=lambda x: x.position)

    def highlightBlock(self, text):
        self.blockHighlightStarted.emit(self, text)
        # setup user data
        userData = self.currentBlockUserData()
        if not isinstance(userData, TextBlockUserData):
            userData = TextBlockUserData()
            self.setCurrentBlockUserData(userData)
        # update user data
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        if os.environ["QT_API"] == "PyQt4":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
        self._detectFolding(text, userData)
        self._detectParentheses(text, userData)
        self.doHighlightBlock(text)
        self.blockHighlightFinished.emit(self, text)

    def doHighlightBlock(self, text):
        """
        Abstract method. Override this to apply syntax highlighting.

        :param text: Line of text to highlight.
        """
        raise NotImplementedError()
