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
This package contains the core modes (language independant)
"""
from pyqode.core.modes.autocomplete import AutoCompleteMode
from pyqode.core.modes.caret_line_highlight import CaretLineHighlighterMode
from pyqode.core.modes.checker import CheckerMode, CheckerMessage
from pyqode.core.modes.checker import MSG_STATUS_ERROR
from pyqode.core.modes.checker import MSG_STATUS_INFO
from pyqode.core.modes.checker import MSG_STATUS_WARNING
from pyqode.core.modes.checker import CHECK_TRIGGER_TXT_CHANGED
from pyqode.core.modes.checker import CHECK_TRIGGER_TXT_SAVED
from pyqode.core.modes.code_completion import CodeCompletionMode
from pyqode.core.modes.code_completion import CompletionProvider
from pyqode.core.modes.code_completion import Completion
from pyqode.core.modes.code_completion import DocumentWordCompletionProvider
from pyqode.core.modes.filewatcher import FileWatcherMode
from pyqode.core.modes.matcher import SymbolMatcherMode
from pyqode.core.modes.right_margin import RightMarginMode
from pyqode.core.modes.zoom import ZoomMode
from pyqode.core.modes.pygments_syntax_highlighter import PygmentsSyntaxHighlighter
from pyqode.core.modes.pygments_syntax_highlighter import PYGMENTS_STYLES
from pyqode.core.modes.autoindent import AutoIndentMode
from pyqode.core.modes.indenter import IndenterMode
from pyqode.core.modes.wordclick import WordClickMode


__all__ = ["CaretLineHighlighterMode", "CheckerMode", "CheckerMessage",
           "MSG_STATUS_ERROR", "MSG_STATUS_WARNING", "MSG_STATUS_INFO",
           "CHECK_TRIGGER_TXT_SAVED", "CHECK_TRIGGER_TXT_CHANGED",
           "CodeCompletionMode", "CompletionProvider", "Completion",
           "DocumentWordCompletionProvider", "FileWatcherMode",
           "SymbolMatcherMode", "IndenterMode"
           "RightMarginMode", "ZoomMode", "PygmentsSyntaxHighlighter",
           "PYGMENTS_STYLES", "AutoIndentMode",
           "WordClickMode"]
