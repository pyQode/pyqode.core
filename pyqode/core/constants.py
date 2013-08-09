#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyQode - Python/Qt Code Editor widget
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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
    Enumerate the possible panel positions
    """
    #: top margin
    TOP = 0
    # left margin
    LEFT = 1
    # right margin
    RIGHT = 2
    # bottom margin
    BOTTOM = 3
