"""
Base class for pyqode syntax hightlighters
"""
import os
from pyqode.core.mode import Mode
from pyqode.core.textblockuserdata import TextBlockUserData, ParenthesisInfo
from pyqode.qt import QtGui, QtCore


class FoldDetector(object):
    """
    A fold detector take care of detecting the folding indent of a specific text
    block.

    A code folding marker will appear the line *before* the one where the
    indention level increases. The code folding region will end in the last
    line that has the same indention level (or higher), skipping blank lines.

    You must override the getFoldIndent method to create a custom fold detector.

    The base implementation does not perform any detection.
    """
    def getFoldIndent(self, highlighter, block, text):
        """
        Return the fold indent of a QTextBlock

        A code folding marker will appear the line *before* the one where the
        indention level increases.
        The code folding reagion will end in the last line that has the same
        indention level (or higher).

        :param highlighter: Reference to the highlighter

        :param block: Block to parse
        :param text: Text of the block (for convenience)

        :return: int
        """
        return -1

    def isFoldStart(self, currentBlock, nextBlock):
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
                    return pb.userData().foldIndent
            return -1


class CharBasedFoldDetector(FoldDetector):
    """
    Detects folding based on character triggers

    Suitable for c family languages (c, c++, C#, java, D, ...)
    """
    def __init__(self, starts='{', ends='}'):
        """
        :param starts: Start triggering character
        :param starts: Start triggering character
        """
        self._start = starts
        self._end = ends

    def getFoldIndent(self, highlighter, block, text):
        pb = block.previous()
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
                    return usd.foldIndent
        else:
            return 0


class SyntaxHighlighter(QtGui.QSyntaxHighlighter, Mode):
    """
    Base class for syntax highlighter modes.

    It takes care of filling the document with our custom user data.

    It also provides signal that you can hook to apply apply custom
    highlighting
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
        if os.environ["QT_API"] == "PyQt":
            # there is a bug with QTextBlockUserData in PyQt4, we need to
            # keep a reference on the otherwise they are removed from memory
            self.__blocks = set()
        self._foldDetector = foldDetector

    def __del__(self):
        self.__blocks.clear()

    def setFoldDetector(self, foldDetector):
        self._foldDetector = foldDetector

    def detectFolding(self, text, userData):
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

    def detectParentheses(self, text, userData):
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

    def highlightBlock(self, text):
        self.blockHighlightStarted.emit(self, text)
        # setup user data
        userData = self.currentBlockUserData()
        if userData is None:
            userData = TextBlockUserData()
            self.setCurrentBlockUserData(userData)
        # update user data
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        self.detectFolding(text, userData)
        self.detectParentheses(text, userData)

        if os.environ["QT_API"] == "PyQt":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
        self.doHighlightBlock(text)
        self.blockHighlightFinished.emit(self, text)

    def doHighlightBlock(self, text):
        raise NotImplementedError()
