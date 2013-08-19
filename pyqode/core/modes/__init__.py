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
This package contains the core modes (language independant)
"""
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
from pyqode.core.modes.indenter import AutoIndentMode


__all__ = ["CaretLineHighlighterMode", "CheckerMode", "CheckerMessage",
           "MSG_STATUS_ERROR", "MSG_STATUS_WARNING", "MSG_STATUS_INFO",
           "CHECK_TRIGGER_TXT_SAVED", "CHECK_TRIGGER_TXT_CHANGED",
           "CodeCompletionMode", "CompletionProvider", "Completion",
           "DocumentWordCompletionProvider", "FileWatcherMode",
           "SymbolMatcherMode",
           "RightMarginMode", "ZoomMode", "PygmentsSyntaxHighlighter",
           "PYGMENTS_STYLES", "AutoIndentMode"]
