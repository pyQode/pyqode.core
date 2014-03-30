# -*- coding: utf-8 -*-
"""
Contains the text block user data structure
"""
from PyQt4 import QtGui


class ParenthesisInfo(object):
    """
    Stores information about a parenthesis in a line of code.
    """
    def __init__(self, pos, char):
        #: Position of the parenthesis, expressed as a number of character
        self.position = pos
        #: The parenthesis character, one of "(", ")", "{", "}", "[", "]"
        self.character = char


class TextBlockUserData(QtGui.QTextBlockUserData):
    """
    Custom text block data. pyQode use text block data for many purposes:
        - folding detection
        - symbols matching
        - mar

    You can also add your own
    """
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        #: Line number of the data, for convenience
        self.line_number = -1
        #: Specify if the block is folded
        self.folded = False
        #: Specify if the block is a fold start
        self.fold_start = False
        #: The block's fold indent
        self.fold_indent = -1
        #: The :class:`pyqode.core.Marker` associated with the text block
        self.marker = None
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "(" and ")"
        #: symbols
        self.parentheses = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "[" and "]"
        #: symbols
        self.square_brackets = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "{" and "}"
        #: symbols
        self.braces = []
        #: Zones were Code completion is disabled. List of tuple. Each tuple
        #: contains the start column and the end column.
        self.cc_disabled_zones = []

    def __repr__(self):
        return ("#{} - Folded: {}  FoldIndent: {} - FoldStart: {}"
                "".format(self.line_number, self.folded, self.fold_indent,
                          self.fold_start))
