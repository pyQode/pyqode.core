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
This module holds all the pyQode constants (enumerations, defines,...)
"""
import sys
from pyqode.core.system import TextStyle
from pyqode.qt.QtGui import QColor

#
# Default style values
#
#: Default editor font (monospace on GNU/Linux, Courier New on windows)
FONT = "monospace"
if sys.platform == "win32":
    FONT = "Consolas"
elif sys.platform == "darwin":
    FONT = "Monaco"
#: Default editor font size
FONT_SIZE = 10
# Colors
EDITOR_BACKGROUND = QColor("#FFFFFF")
EDITOR_FOREGROUND = QColor("#000000")
EDITOR_WS_FOREGROUND = QColor("#dddddd")
SELECTION_BACKGROUND = QColor("#6182F3")
SELECTION_FOREGROUND = QColor("#ffffff")
PANEL_BACKGROUND = QColor("#F2F1F0")
PANEL_FOREGROUND = QColor("#888888")
PANEL_HIGHLIGHT = QColor("#dddddd")
CARET_LINE_BACKGROUND = QColor("#E4EDF8")
SEARCH_OCCURRENCES_BACKGROUND = QColor("#FFFF00")
SEARCH_OCCURRENCES_FOREGROUND = QColor("#000000")

WORD_SEPARATORS = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                   '+', '{', '}', '|', ':', '"', "'", "<", ">", "?", ",",
                   ".", "/", ";", '[', ']', '\\', '\n', '\t', '=', '-', ' ']

#
# Default settings value
#
#: Default tab size
TAB_SIZE = 4
MARGIN_POS = 80

#
# Icons
#
ICONS = []
ACTION_UNDO = (":/pyqode-icons/rc/edit-undo.png", "Ctrl+Z")
ICONS.append(ACTION_UNDO)
ACTION_REDO = (":/pyqode-icons/rc/edit-redo.png", "Ctrl+Y")
ICONS.append(ACTION_REDO)
ACTION_COPY = (":/pyqode-icons/rc/edit-copy.png", "Ctrl+C")
ICONS.append(ACTION_COPY)
ACTION_CUT = (":/pyqode-icons/rc/edit-cut.png", "Ctrl+X")
ICONS.append(ACTION_CUT)
ACTION_PASTE = (":/pyqode-icons/rc/edit-paste.png", "Ctrl+V")
ICONS.append(ACTION_PASTE)
ACTION_DELETE = (":/pyqode-icons/rc/edit-delete.png", "Delete")
ICONS.append(ACTION_DELETE)
ACTION_SELECT_ALL = (":/pyqode-icons/rc/edit-select-all.png", "Ctrl+A")
ICONS.append(ACTION_SELECT_ALL)
ACTION_INDENT = (":/pyqode-icons/rc/format-indent-more.png", "Tab")
ICONS.append(ACTION_INDENT)
ACTION_UNINDENT = (":/pyqode-icons/rc/format-indent-less.png", "Shift+Tab")
ICONS.append(ACTION_UNINDENT)
ACTION_GOTO_LINE = (":/pyqode-icons/rc/goto-line.png", "Ctrl+G")
ICONS.append(ACTION_GOTO_LINE)

ICON_ARROW_RIGHT = (":/pyqode-icons/rc/arrow_right_off.png",
                    ":/pyqode-icons/rc/arrow_right_on.png")
ICON_ARROW_DOWN = (":/pyqode-icons/rc/arrow_down_off.png",
                   ":/pyqode-icons/rc/arrow_down_on.png")


#
# Enumerations
#
class PanelPosition(object):
    """
    Enumerates the possible panel positions
    """
    #: Top margin
    TOP = 0
    #: Left margin
    LEFT = 1
    #: Right margin
    RIGHT = 2
    #: Bottom margin
    BOTTOM = 3
