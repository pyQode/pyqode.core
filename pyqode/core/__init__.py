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
This package contains the core classes of pyqode and an example of a generic
code editor widget
"""
#
# exposes public core api
#
# modules
from pyqode.core import constants
from pyqode.core import logger

# core classes
from pyqode.core.editor import QCodeEdit
from pyqode.core.mode import Mode
from pyqode.core.panel import Panel
from pyqode.core.constants import PanelPosition
from pyqode.core.properties import PropertyRegistry
from pyqode.core.decoration import TextDecoration
from pyqode.core.syntax_highlighter import SyntaxHighlighter
from pyqode.core.syntax_highlighter import FoldDetector
from pyqode.core.syntax_highlighter import IndentBasedFoldDetector
from pyqode.core.syntax_highlighter import CharBasedFoldDetector
from pyqode.core.textblockuserdata import TextBlockUserData, ParenthesisInfo
from pyqode.core.system import TextStyle
from pyqode.core.system import JobRunner
from pyqode.core.system import DelayJobRunner
from pyqode.core.system import SubprocessServer

# modes
from pyqode.core.modes import AutoCompleteMode
from pyqode.core.modes import AutoIndentMode
from pyqode.core.modes import CaretLineHighlighterMode
from pyqode.core.modes import CheckerMode, CheckerMessage
from pyqode.core.modes import MSG_STATUS_ERROR
from pyqode.core.modes import MSG_STATUS_INFO
from pyqode.core.modes import MSG_STATUS_WARNING
from pyqode.core.modes import CHECK_TRIGGER_TXT_CHANGED
from pyqode.core.modes import CHECK_TRIGGER_TXT_SAVED
from pyqode.core.modes import CodeCompletionMode
from pyqode.core.modes import CompletionProvider
from pyqode.core.modes import Completion
from pyqode.core.modes import DocumentWordCompletionProvider
from pyqode.core.modes import FileWatcherMode
from pyqode.core.modes import IndenterMode
from pyqode.core.modes import PygmentsSyntaxHighlighter, PYGMENTS_STYLES
from pyqode.core.modes import RightMarginMode
from pyqode.core.modes import SymbolMatcherMode
from pyqode.core.modes import WordClickMode
from pyqode.core.modes import ZoomMode

# panels
from pyqode.core.panels import FoldingPanel
from pyqode.core.panels import LineNumberPanel
from pyqode.core.panels import MarkerPanel, Marker
from pyqode.core.panels import SearchAndReplacePanel


#: pyqode.core version
__version__ = "1.1"


#
# Example of a generic code editor widget
#
class QGenericCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels.

    **Panels:**
        * :class:`pyqode.core.FoldingPanel`
        * :class:`pyqode.core.LineNumberPanel`
        * :class:`pyqode.core.SearchAndReplacePanel`

    **Modes:**
        * :class:`pyqode.core.AutoCompleteMode`
        * :class:`pyqode.core.FileWatcherMode`
        * :class:`pyqode.core.CaretLineHighlighterMode`
        * :class:`pyqode.core.RightMarginMode`
        * :class:`pyqode.core.PygmentsSyntaxHighlighter`
        * :class:`pyqode.core.ZoomMode`
        * :class:`pyqode.core.AutoIndentMode`
        * :class:`pyqode.core.CodeCompletionMode`
        * :class:`pyqode.core.IndenterMode`
        * :class:`pyqode.core.SymbolMatcherMode`
    """
    def __init__(self, parent=None):
        QCodeEdit.__init__(self, parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("pyQode - Generic Editor")

        self.installPanel(FoldingPanel(), PanelPosition.LEFT)
        self.installPanel(LineNumberPanel(), PanelPosition.LEFT)
        self.installPanel(SearchAndReplacePanel(), PanelPosition.BOTTOM)

        self.installMode(AutoCompleteMode())
        self.installMode(FileWatcherMode())
        self.installMode(CaretLineHighlighterMode())
        self.installMode(RightMarginMode())
        self.installMode(PygmentsSyntaxHighlighter(self.document()))
        self.installMode(ZoomMode())
        self.installMode(AutoIndentMode())
        self.installMode(CodeCompletionMode())
        self.installMode(IndenterMode())
        self.codeCompletionMode.addCompletionProvider(
            DocumentWordCompletionProvider())
        self.installMode(SymbolMatcherMode())


__all__ = ["__version__", "constants", "logger", "Mode", "Panel", "QCodeEdit",
           "SyntaxHighlighter",
           "LineNumberPanel", "MarkerPanel", "Marker", "FoldingPanel",
           "SearchAndReplacePanel", "CaretLineHighlighterMode", "CheckerMode",
           "CheckerMessage", "MSG_STATUS_INFO", "MSG_STATUS_ERROR",
           "MSG_STATUS_WARNING", "FoldDetector", "IndentBasedFoldDetector",
           "CharBasedFoldDetector",
           "CHECK_TRIGGER_TXT_CHANGED", "CHECK_TRIGGER_TXT_SAVED",
           "CodeCompletionMode", "CompletionProvider", "Completion",
           "DocumentWordCompletionProvider", "FileWatcherMode",
           "RightMarginMode", "ZoomMode", "PygmentsSyntaxHighlighter",
           "AutoIndentMode", "PanelPosition", "TextDecoration", "IndenterMode",
           "PropertyRegistry", "TextStyle", "QGenericCodeEdit", "JobRunner",
           "DelayJobRunner", "TextBlockUserData", "ParenthesisInfo",
           "WordClickMode",
           "PYGMENTS_STYLES", "memoized", "SubprocessServer", "SymbolMatcherMode"]
