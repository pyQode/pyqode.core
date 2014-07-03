# -*- coding: utf-8 -*-
import os
import sys
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from . import server


class GenericCodeEdit(api.CodeEdit):
    """
    A generic code editor widget. This is just a CodeEdit with a preconfigured
    set of modes and panels.

    It does not have any language specific feature.
    """
    def __init__(self, parent):
        super().__init__(parent)
        if hasattr(sys, "frozen"):
            # start the frozen server on Windows
            self.backend.start(os.path.join(os.getcwd(), 'server.exe'))
        else:
            self.backend.start(server.__file__)

        # append panels
        self.panels.append(panels.LineNumberPanel())
        self.panels.append(panels.SearchAndReplacePanel(),
                        api.Panel.Position.BOTTOM)

        # append modes
        self.modes.append(modes.AutoCompleteMode())
        self.modes.append(modes.CaseConverterMode())
        self.modes.append(modes.FileWatcherMode())
        self.modes.append(modes.CaretLineHighlighterMode())
        self.modes.append(modes.RightMarginMode())
        self.modes.append(modes.PygmentsSyntaxHighlighter(
            self.document()))
        self.modes.append(modes.ZoomMode())
        self.modes.append(modes.CodeCompletionMode())
        self.modes.append(modes.AutoIndentMode())
        self.modes.append(modes.IndenterMode())
        self.modes.append(modes.SymbolMatcherMode())
