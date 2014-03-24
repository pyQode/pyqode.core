#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
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
from PyQt4 import QtGui, QtCore

from pyqode.core.editor import Mode
from pyqode.core.api.textblockuserdata import ParenthesisInfo
from pyqode.core.api.textblockuserdata import TextBlockUserData


class FoldDetector(object):
    """
    Abstract base class for fold indicators.

    A fold detector take care of detecting the folding indent of a specific
    text block.

    A code folding marker will appear the line *before* the one where the
    indention level increases. The code folding region will end in the last
    line that has the same indention level (or higher), skipping blank lines.

    You **must** override the :meth:`pyqode.core.FoldDetector.get_fold_indent`
    method to create a custom fold detector.
    """

    def get_fold_indent(self, highlighter, block, text):
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
    def is_fold_start(current_block, next_block):
        curr_usd = current_block.userData()
        next_usd = next_block.userData()
        if curr_usd.fold_indent < next_usd.fold_indent:
            return True


class IndentBasedFoldDetector(FoldDetector):
    """
    Perform folding detection based on the line indentation level.

    Suitable for languages such as python, cython, batch, data interchange
    formats such as xml and json or even markup languages (html, rst).

    It does not work well with c based languages nor with vb or ruby.
    """
    def get_fold_indent(self, highlighter, block, text):
        previous_block = block.previous()
        if previous_block:
            ptxt = previous_block.text().rstrip()
            if(ptxt.endswith("(") or ptxt.endswith(",") or
               ptxt.endswith("\\") or ptxt.endswith("+") or
               ptxt.endswith("-") or ptxt.endswith("*") or
               ptxt.endswith("/") or ptxt.endswith("and") or
               ptxt.endswith("or")):
                return previous_block.userData().fold_indent
        stripped = len(text.strip())
        if stripped:
            return int((len(text) - len(text.lstrip())))
        else:
            while (not len(previous_block.text().strip()) and
                    previous_block.isValid()):
                previous_block = previous_block.previous()
            prev_block_indent = (len(previous_block.text()) -
                                 len(previous_block.text().lstrip()))
            # check next blocks to see if their indent is >= then the last
            # block
            next_block = block.next()
            while not len(next_block.text().strip()) and next_block.isValid():
                next_block = next_block.next()
            next_block_indent = (len(next_block.text()) -
                                 len(next_block.text().lstrip()))
            if (next_block_indent >= prev_block_indent or
                    previous_block.userState() & 0x7F):
                if previous_block.userData():
                    return next_block_indent
            return -1


class CharBasedFoldDetector(FoldDetector):
    """
    Detects folding based on character triggers

    Suitable for c family languages (c, c++, C#, java, D, ...)
    """
    def __init__(self, start='{', end='}'):
        self._start = start
        self._end = end

    def get_fold_indent(self, highlighter, block, text):
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
                return usd.fold_indent + 1
            else:
                # fold start
                if self._start in txt and not self._end in txt:
                    stext = txt.strip()
                    if not stext.startswith(self._start):
                        return usd.fold_indent + 1
                    else:
                        return usd.fold_indent
                # fold end
                elif self._end in txt and not self._start in txt:
                    usd = pb.userData()
                    return usd.fold_indent - 1
                else:
                    # same folding level as the previous block
                    nb = block.next()
                    while nb.isValid() and not len(nb.text().strip()):
                        nb = nb.next()
                    if (nb.isValid() and self._start in nb.text() and
                            not len(text.strip())):
                        return usd.fold_indent + 1
                    return usd.fold_indent
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

    **signals**:
        - :attr:`pyqode.core.SyntaxHighlighter.block_highlight_started`
        - :attr:`pyqode.core.SyntaxHighlighter.block_highlight_finished`

    .. warning:: You should always inherit from this class to create a new
                 syntax. **Never inherit directly from QSyntaxHighlighter.**
    """
    #: Mode identifier
    IDENTIFIER = "syntaxHighlighterMode"

    #: Signal emitted at the start of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    block_highlight_started = QtCore.pyqtSignal(object, object)

    #: Signal emitted at the end of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    block_highlight_finished = QtCore.pyqtSignal(object, object)

    def __init__(self, parent, fold_detector=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        Mode.__init__(self)
        self._spaces_ptrn = QtCore.QRegExp('\s+')
        # there is a bug with QTextBlockUserData in PyQt4, we need to
        # keep a reference on them, otherwise they are removed from memory.
        self._blocks = set()
        self._fold_detector = fold_detector

    def __del__(self):
        self._blocks.clear()

    def set_fold_detector(self, fold_detector):
        """
        Setup the fold detector object to use to detect fold indents.

        :param fold_detector: FoldDetector
        :type fold_detector: pyqode.core.FoldDetector
        """
        self._fold_detector = fold_detector

    def _detect_folding(self, text, user_data):
        """
        Detect folding indents using a foldDetector.
        """
        # Collect folding informations
        if self._fold_detector:
            user_data.fold_indent = self._fold_detector.get_fold_indent(
                self, self.currentBlock(), text)
            prev_block = self.currentBlock().previous()
            if prev_block and prev_block.isValid():
                # skip blank lines
                while (prev_block and prev_block.isValid() and
                       len(prev_block.text().strip()) == 0):
                    prev_block = prev_block.previous()
                prev_usd = prev_block.userData()
                if prev_usd:
                    prev_usd.fold_start = self._fold_detector.is_fold_start(
                        prev_block, self.currentBlock())
                prev_block.setUserData(prev_usd)

    @staticmethod
    def _detect_parentheses(text, user_data):
        user_data.parentheses[:] = []
        user_data.square_brackets[:] = []
        user_data.braces[:] = []
        # todo check if bracket is not into a string litteral
        # parentheses
        left_pos = text.find("(", 0)
        while left_pos != -1:
            info = ParenthesisInfo(left_pos, "(")
            user_data.parentheses.append(info)
            left_pos = text.find("(", left_pos + 1)
        right_pos = text.find(")", 0)
        while right_pos != -1:
            info = ParenthesisInfo(right_pos, ")")
            user_data.parentheses.append(info)
            right_pos = text.find(")", right_pos + 1)
        # braces
        left_pos = text.find("{", 0)
        while left_pos != -1:
            info = ParenthesisInfo(left_pos, "{")
            user_data.braces.append(info)
            left_pos = text.find("{", left_pos + 1)
        right_pos = text.find("}", 0)
        while right_pos != -1:
            info = ParenthesisInfo(right_pos, "}")
            user_data.braces.append(info)
            right_pos = text.find("}", right_pos + 1)
        # square_brackets
        left_pos = text.find("[", 0)
        while left_pos != -1:
            info = ParenthesisInfo(left_pos, "[")
            user_data.square_brackets.append(info)
            left_pos = text.find("[", left_pos + 1)
        right_pos = text.find("]", 0)
        while right_pos != -1:
            info = ParenthesisInfo(right_pos, "]")
            user_data.square_brackets.append(info)
            right_pos = text.find("]", right_pos + 1)
        user_data.parentheses[:] = sorted(
            user_data.parentheses, key=lambda x: x.position)
        user_data.square_brackets[:] = sorted(
            user_data.square_brackets, key=lambda x: x.position)
        user_data.braces[:] = sorted(
            user_data.braces, key=lambda x: x.position)

    def highlightBlock(self, text):
        self.block_highlight_started.emit(self, text)
        # setup user data
        user_data = self.currentBlockUserData()
        if not isinstance(user_data, TextBlockUserData):
            user_data = TextBlockUserData()
            self.setCurrentBlockUserData(user_data)
        # update user data
        user_data.line_number = self.currentBlock().blockNumber() + 1
        self._blocks.add(user_data)
        self.setCurrentBlockUserData(user_data)
        self._detect_folding(text, user_data)
        self._detect_parentheses(text, user_data)
        self.highlight_block(text)
        self.block_highlight_finished.emit(self, text)

    def highlight_block(self, text):
        """
        Abstract method. Override this to apply syntax highlighting.

        :param text: Line of text to highlight.
        """
        raise NotImplementedError()
