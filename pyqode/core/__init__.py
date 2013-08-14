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
This package contains the core classes of pyqode and an example of a generic
code editor widget
"""
#
# exposes public core api
#
import os
from pyqode.core import constants
from pyqode.core import logger
from pyqode.core.constants import PanelPosition
from pyqode.core.decoration import TextDecoration
from pyqode.core.editor import QCodeEdit
from pyqode.core.syntax_highlighter import SyntaxHighlighter
from pyqode.core.syntax_highlighter import FoldDetector
from pyqode.core.syntax_highlighter import IndentBasedFoldDetector
from pyqode.core.syntax_highlighter import CharBasedFoldDetector
from pyqode.core.mode import Mode
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
from pyqode.core.panel import Panel
from pyqode.core.modes import PygmentsSyntaxHighlighter, PYGMENTS_STYLES
from pyqode.core.modes import RightMarginMode
from pyqode.core.modes import SymbolMatcherMode
from pyqode.core.modes import ZoomMode
from pyqode.core.panels import FoldingPanel
from pyqode.core.panels import LineNumberPanel
from pyqode.core.panels import MarkerPanel, Marker
from pyqode.core.panels import SearchAndReplacePanel
from pyqode.core.properties import PropertyRegistry
from pyqode.core.system import indexByName
from pyqode.core.system import indexMatching
from pyqode.core.system import TextStyle
from pyqode.core.system import JobRunner
from pyqode.core.system import DelayJobRunner
from pyqode.core.system import SubprocessServer
from pyqode.core.system import memoized
from pyqode.qt.ui import importRc


#: pyqode-core version
__version__ = "1.0b"


def getUiDirectory():
    """
    Gets the pyqode-core ui directory
    """
    return os.path.join(os.path.abspath(os.path.join(__file__, "..")), "ui")


def getRcDirectory():
    """
    Gets the pyqode-core rc directory
    """
    return os.path.join(os.path.abspath(os.path.join(__file__, "..")), "ui",
                        "rc")

# import the core rc modules
if os.environ["QT_API"] == "PyQt4":
    from pyqode.core.ui import pyqode_icons_pyqt_rc
else:
    from pyqode.core.ui import pyqode_icons_pyside_rc

#
# Example of a generic code editor widgey
#
class QGenericCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels.

    **Panels:**
        * line number panel
        * search and replace panel

    **Modes:**
        * document word completion
        * generic syntax highlighter (pygments)
    """
    def __init__(self, parent=None):
        QCodeEdit.__init__(self, parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("pyQode - Generic Editor")
        self.installPanel(FoldingPanel(), PanelPosition.LEFT)
        self.installPanel(LineNumberPanel(), PanelPosition.LEFT)
        self.installPanel(SearchAndReplacePanel(), PanelPosition.BOTTOM)
        self.installMode(FileWatcherMode())
        self.installMode(CaretLineHighlighterMode())
        self.installMode(RightMarginMode())
        self.installMode(PygmentsSyntaxHighlighter(self.document()))
        self.installMode(ZoomMode())
        self.installMode(AutoIndentMode())
        self.installMode(CodeCompletionMode())
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
           "DocumentWordCompletionProvider" "FileWatcherMode",
           "RightMarginMode", "ZoomMode", "PygmentsSyntaxHighlighter",
           "AutoIndentMode", "PanelPosition", "TextDecoration",
           "PropertyRegistry", "TextStyle", "QGenericCodeEdit", "JobRunner",
           "DelayJobRunner", "getUiDirectory", "getRcDirectory",
           "PYGMENTS_STYLES", "indexByName", "indexMatching", "memoized",
           "SubprocessServer", "SymbolMatcherMode"]
