"""
Contains the text block user data structure
"""
from pcef.qt import QtGui


class TextBlockUserData(QtGui.QTextBlockUserData):
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.blockNumber = -1
        self.folded = False
        self.indent = -1
        self.marker = None
        self.parenthesisInfos = []


    def __repr__(self):
        return ("#{} - Folded: {} - Indent: {} - Marker: {} - Parenthesis: {}"
                "".format(self.blockNumber, self.folded, self.indent,
                          self.marker, self.parenthesisInfos))
