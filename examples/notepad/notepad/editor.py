# -*- coding: utf-8 -*-
import os
import sys

from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels

from . import server


class GenericCodeEdit(frontend.CodeEdit):
    """
    A generic code editor widget. This is just a CodeEdit with a preconfigured
    set of modes and panels.

    It does not have any language specific feature.
    """
    def __init__(self, parent):
        super().__init__(parent)
        if hasattr(sys, "frozen"):
            frontend.start_server(self, os.path.join(os.getcwd(), 'server.exe'))
        else:
            frontend.start_server(self, server.__file__)

        # add panels
        frontend.install_panel(self, panels.LineNumberPanel())
        frontend.install_panel(self, panels.SearchAndReplacePanel(),
                               panels.SearchAndReplacePanel.Position.BOTTOM)

        # add modes
        frontend.install_mode(self, modes.AutoCompleteMode())
        frontend.install_mode(self, modes.CaseConverterMode())
        frontend.install_mode(self, modes.FileWatcherMode())
        frontend.install_mode(self, modes.CaretLineHighlighterMode())
        frontend.install_mode(self, modes.RightMarginMode())
        frontend.install_mode(self, modes.PygmentsSyntaxHighlighter(
            self.document()))
        frontend.install_mode(self, modes.ZoomMode())
        frontend.install_mode(self, modes.CodeCompletionMode())
        frontend.install_mode(self, modes.AutoIndentMode())
        frontend.install_mode(self, modes.IndenterMode())
        frontend.install_mode(self, modes.SymbolMatcherMode())
