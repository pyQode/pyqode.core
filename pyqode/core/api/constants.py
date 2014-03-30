# -*- coding: utf-8 -*-
"""
This module contains most of the constants of the api (default colors, default
icons, ...)
"""
import sys

WORD_SEPARATORS = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                   '+', '{', '}', '|', ':', '"', "'", "<", ">", "?", ",",
                   ".", "/", ";", '[', ']', '\\', '\n', '\t', '=', '-', ' ']

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
