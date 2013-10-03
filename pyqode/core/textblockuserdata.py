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
Contains the text block user data structure
"""
from pyqode.qt import QtGui


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
        self.lineNumber = -1
        #: Specify if the block is folded
        self.folded = False
        #: Specify if the block is a fold start
        self.foldStart = False
        #: The block's fold indent
        self.foldIndent = -1
        #: The :class:`pyqode.core.Marker` associated with the text block
        self.marker = None
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "(" and ")"
        #: symbols
        self.parentheses = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "[" and "]"
        #: symbols
        self.squareBrackets = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "{" and "}"
        #: symbols
        self.braces = []

    def __repr__(self):
        return ("#{} - Folded: {}  FoldIndent: {} - FoldStart: {}"
                "".format(self.lineNumber, self.folded, self.foldIndent,
                          self.foldStart))
