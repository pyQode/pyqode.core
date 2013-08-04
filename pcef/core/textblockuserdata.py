"""
Contains the text block user data structure
"""
from pcef.qt import QtGui


class TextBlockUserData(QtGui.QTextBlockUserData):
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.lineNumber = -1
        # specify if the block is folded
        self.folded = False
        # specify if the block is the fold start
        self.isStartFold = False
        # specify if the block is a fold end
        self.isEndFold = False
        # specify fold indent
        self.foldIndent = -1
        self.indent = -1
        self.marker = None
        self.parenthesisInfos = []


    def __repr__(self):
        return ("#{} - Folded: {}  FoldIndent: {} - StartFold: {} - EndFold: {}"
                " - Indent: {} - Marker: {} - Parenthesis: {}"
                "".format(self.lineNumber, self.folded, self.foldIndent,
                          self.isStartFold, self.isEndFold,
                          self.indent, self.marker, self.parenthesisInfos))
