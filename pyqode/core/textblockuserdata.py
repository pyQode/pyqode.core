#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
Contains the text block user data structure
"""
from pyqode.qt import QtGui


class ParenthesisInfo(object):
    def __init__(self, pos, char):
        self.position = pos
        self.character = char


class TextBlockUserData(QtGui.QTextBlockUserData):
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.lineNumber = -1
        # specify if the block is folded
        self.folded = False
        # specify if the block is the fold start
        self.foldStart = False
        self.foldIndent = -1
        self.marker = None
        #: list of ParenthesisInfo, pne foreach character type
        self.parentheses = []  # ()
        self.squareBrackets = []  # []
        self.braces = []  # ()

    def __repr__(self):
        return ("#{} - Folded: {}  FoldIndent: {} - FoldStart: {}"
                "".format(self.lineNumber, self.folded, self.foldIndent,
                          self.foldStart))
