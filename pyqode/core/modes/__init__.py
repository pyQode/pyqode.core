# -*- coding: utf-8 -*-
"""
This package contains the core modes
"""
from pyqode.core.modes.autocomplete import AutoCompleteMode
from pyqode.core.modes.caret_line_highlight import CaretLineHighlighterMode
from pyqode.core.modes.case_converter import CaseConverterMode
from pyqode.core.modes.checker import CheckerMode, CheckerMessage
from pyqode.core.modes.code_completion import CodeCompletionMode
from pyqode.core.modes.filewatcher import FileWatcherMode
from pyqode.core.modes.matcher import SymbolMatcherMode
from pyqode.core.modes.right_margin import RightMarginMode
from pyqode.core.modes.zoom import ZoomMode
from pyqode.core.modes.pygments_syntax_highlighter import \
    PygmentsSyntaxHighlighter
from pyqode.core.modes.pygments_syntax_highlighter import PYGMENTS_STYLES
from pyqode.core.modes.autoindent import AutoIndentMode
from pyqode.core.modes.indenter import IndenterMode
from pyqode.core.modes.wordclick import WordClickMode


__all__ = ["CaretLineHighlighterMode", "CheckerMode", "CheckerMessage",
           "MSG_STATUS_ERROR", "MSG_STATUS_WARNING", "MSG_STATUS_INFO",
           "CHECK_TRIGGER_TXT_SAVED", "CHECK_TRIGGER_TXT_CHANGED",
           "CodeCompletionMode", "FileWatcherMode", "SymbolMatcherMode",
           "IndenterMode", "RightMarginMode", "ZoomMode",
           "PygmentsSyntaxHighlighter", "PYGMENTS_STYLES", "AutoIndentMode",
           "CaseConverterMode", "WordClickMode"]
