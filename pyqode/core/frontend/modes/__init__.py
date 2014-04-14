# -*- coding: utf-8 -*-
"""
This package contains the core modes
"""
from pyqode.core.frontend.modes.autocomplete import AutoCompleteMode
from pyqode.core.frontend.modes.caret_line_highlight import \
    CaretLineHighlighterMode
from pyqode.core.frontend.modes.case_converter import CaseConverterMode
from pyqode.core.frontend.modes.checker import CheckerMode, CheckerMessage
from pyqode.core.frontend.modes.code_completion import CodeCompletionMode
from pyqode.core.frontend.modes.filewatcher import FileWatcherMode
from pyqode.core.frontend.modes.matcher import SymbolMatcherMode
from pyqode.core.frontend.modes.right_margin import RightMarginMode
from pyqode.core.frontend.modes.zoom import ZoomMode
from pyqode.core.frontend.modes.pygments_syntax_highlighter import \
    PygmentsSyntaxHighlighter
from pyqode.core.frontend.modes.pygments_syntax_highlighter import \
    PYGMENTS_STYLES
from pyqode.core.frontend.modes.autoindent import AutoIndentMode
from pyqode.core.frontend.modes.indenter import IndenterMode
from pyqode.core.frontend.modes.wordclick import WordClickMode


__all__ = ["CaretLineHighlighterMode", "CheckerMode", "CheckerMessage",
           "MSG_STATUS_ERROR", "MSG_STATUS_WARNING", "MSG_STATUS_INFO",
           "CHECK_TRIGGER_TXT_SAVED", "CHECK_TRIGGER_TXT_CHANGED",
           "CodeCompletionMode", "FileWatcherMode", "SymbolMatcherMode",
           "IndenterMode", "RightMarginMode", "ZoomMode",
           "PygmentsSyntaxHighlighter", "PYGMENTS_STYLES", "AutoIndentMode",
           "CaseConverterMode", "WordClickMode"]
