# -*- coding: utf-8 -*-
"""
This module contains most of the constants of the api (default colors, default
icons, ...)
"""
import sys

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
EDITOR_BACKGROUND = "#FFFFFF"
EDITOR_FOREGROUND = "#000000"
EDITOR_WS_FOREGROUND = "#dddddd"
SELECTION_BACKGROUND = "#6182F3"
SELECTION_FOREGROUND = "#ffffff"
PANEL_BACKGROUND = "#F2F1F0"
PANEL_FOREGROUND = "#888888"
PANEL_HIGHLIGHT = "#dddddd"
CARET_LINE_BACKGROUND = "#E4EDF8"
SEARCH_OCCURRENCES_BACKGROUND = "#FFFF00"
SEARCH_OCCURRENCES_FOREGROUND = "#000000"

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
ACTIONS = {
    "Undo": (":/pyqode-icons/rc/edit-undo.png", "Ctrl+Z", "edit-undo"),
    "Redo": (":/pyqode-icons/rc/edit-redo.png", "Ctrl+Y", "edit-redo"),
    "Copy": (":/pyqode-icons/rc/edit-copy.png", "Ctrl+C", "edit-copy"),
    "Cut": (":/pyqode-icons/rc/edit-cut.png", "Ctrl+X", "edit-cut"),
    "Paste": (":/pyqode-icons/rc/edit-paste.png", "Ctrl+V", "edit-paste"),
    "Delete": (":/pyqode-icons/rc/edit-delete.png", "Delete", "edit-delete"),
    "Select all": (":/pyqode-icons/rc/edit-select-all.png", "Ctrl+A",
                   "edit-select-all"),
    "Indent": (":/pyqode-icons/rc/format-indent-more.png", "Tab",
               "format-indent-more"),
    "Un-indent": (":/pyqode-icons/rc/format-indent-less.png", "Shift+Tab",
                  "format-indent-less"),
    "Go to line": (":/pyqode-icons/rc/goto-line.png", "Ctrl+G", "start-here")
}

ICONS = {
    "Find": ":/pyqode-icons/rc/edit-find.png",
    "Replace": ":/pyqode-icons/rc/edit-find-replace.png",
    "Next": ":/pyqode-icons/rc/go-down.png",
    "Previous": ":/pyqode-icons/rc/go-up.png",
    "Close": ":/pyqode-icons/rc/close.png"
}

for k, v in ACTIONS.items():
    ICONS[k] = v[0]


# non native folding icons
ICON_ARROW_RIGHT = (":/pyqode-icons/rc/arrow_right_off.png",
                    ":/pyqode-icons/rc/arrow_right_on.png")
ICON_ARROW_DOWN = (":/pyqode-icons/rc/arrow_down_off.png",
                   ":/pyqode-icons/rc/arrow_down_on.png")


# Checker mode constants

class CheckerMessages:
    #: Status value for an information message.
    INFO = 0
    #: Status value for a warning message.
    WARNING = 1
    #: Status value for an error message.
    ERROR = 2


class CheckerTriggers:
    #: Check is triggered when text has changed.
    TXT_CHANGED = 0
    #: Check is triggered when text has been saved.
    TXT_SAVED = 1
