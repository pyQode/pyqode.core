"""
Base class for pcef syntax hightlighters
"""
import logging
import os
from pcef.core.textblockuserdata import TextBlockUserData
from pcef.qt import QtGui, QtCore


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """
    This is the base class for any pcef syntax higlighter. It takes care
    of filling the document with our custum user data.
    """

    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
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
        return len(text) - len(text.strip())

    def isStartFolder(self, text, userData):
        """
        Checks if the block is a start folder
        """
        fi = self.currentBlock().next().userData().foldIndent
        return userData.foldIndent < fi

    def isEndFolder(self, text, userData):
        fi = self.currentBlock().next().userData().foldIndent
        return userData.foldIndent > fi

    def highlightBlock(self, text):
        # parse line indent
        userData = self.currentBlockUserData()
        if userData is None:
            userData = TextBlockUserData()
        # update user data with parenthesis infos, indent info,...
        userData.indent = len(text) - len(text.strip())
        userData.foldIndent = self.getFoldingIndent(text)
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        logging.getLogger("pcef").info(userData)
        # set current block's user date
        if os.environ["QT_API"] == "PyQt":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
