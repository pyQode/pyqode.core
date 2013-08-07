"""
Base class for pcef syntax hightlighters
"""
import os
from pcef.core.mode import Mode
from pcef.core.textblockuserdata import TextBlockUserData
from pcef.qt import QtGui, QtCore


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

    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        Mode.__init__(self)
        self._spacesExpression = QtCore.QRegExp('\s+')
        if os.environ["QT_API"] == "PyQt":
            # there is a bug with QTextBlockUserData in PyQt4, we need to
            # keep a reference on the otherwise they are removed from memory
            self.__blocks = set()

    def __del__(self):
        self.__blocks.clear()

    def getFoldingIndent(self, text):
        """
        Return the folding indent of the block.

        This must be specialised for a specific language, it just use the
        regular indent here.

        :param text:
        :return:
        """
        pb = self.currentBlock().previous()
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
            return int((len(text) - len(text.strip())))
        else:
            return -1

    def isFoldStart(self, currentBlock, nextBlock):
        """
        Checks if the current block is a start fold block

        :param current: Current block
        :param next: Next block
        :return: True or False
        """
        currUsd = currentBlock.userData()
        nextUsd = nextBlock.userData()
        if currUsd.foldIndent < nextUsd.foldIndent:
            return True

    def highlightBlock(self, text):
        # parse line indent
        userData = self.currentBlockUserData()
        if userData is None:
            userData = TextBlockUserData()
        # update user data with parenthesis infos, indent info,...
        userData.foldIndent = self.getFoldingIndent(text)
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        if userData.lineNumber == 23:
            pass
        pb = self.currentBlock().previous()
        if pb.isValid():
            # skip blank lines
            while pb and pb.isValid() and len(pb.text().strip()) == 0:
                pb = pb.previous()
            pd = pb.userData()
            if pd:
                if userData.foldIndent > pd.foldIndent:
                    pd.foldStart = True
                    pb.setUserData(pd)
        # set current block's user date
        if os.environ["QT_API"] == "PyQt":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
