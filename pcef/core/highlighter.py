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

    def highlightBlock(self, text):
        # parse line indent
        userData = self.currentBlockUserData()
        if userData is None:
            userData = TextBlockUserData()
        # update user data with parenthesis infos, indent info,...
        userData.indent = len(text) - len(text.strip())
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        logging.getLogger("pcef").info(userData)
        # set current block's user date
        if os.environ["QT_API"] == "PyQt":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
