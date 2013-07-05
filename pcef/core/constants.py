#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module holds all the PCEF constants (enumerations, defines,...)
"""
import sys
from pcef.core.system import TextStyle
from pcef.qt.QtGui import QColor

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
#: Editor stylesheet
CODE_EDIT_STYLESHEET = """QCodeEdit
{
    background-color: %(background)s;
    color: %(foreground)s;
    selection-background-color: %(selectionBackground)s;
    selection-color: %(selectionForeground)s;
    border: none;
    border-radius: 0px;
}
"""
# Colors
EDITOR_BACKGROUND = QColor("#FFFFFF")
EDITOR_FOREGROUND = QColor("#000000")
EDITOR_WS_FOREGROUND = QColor("#dddddd")
SELECTION_BACKGROUND = QColor("#6182F3")
SELECTION_FOREGROUND = QColor("#ffffff")
PANEL_BACKGROUND = QColor("#dddddd")
PANEL_FOREGROUND = QColor("#888888")
PANEL_HIGHLIGHT = QColor("#cccccc")
CARET_LINE_BACKGROUND = QColor("#E4EDF8")

# Default highlighter styles values, mostly for the python highlighter but they
# may be shared between different highlighter/languages
DEFAULT_STYLES = {
    'keyword': TextStyle('#808000 bold nitalic nunderlined'),
    'builtins': TextStyle('#808000 nbold nitalic nunderlined'),
    'operator': TextStyle('darkGray nbold nitalic nunderlined'),
    'punctuation': TextStyle('darkGray nbold nitalic nunderlined'),
    'decorator': TextStyle('#808000 nbold nitalic nunderlined'),
    'brace': TextStyle('#404040 nbold nitalic nunderlined'),
    'class': TextStyle('#800080 bold nitalic nunderlined'),
    'function': TextStyle('#800080 nbold nitalic nunderlined'),
    'string': TextStyle('#008000 nbold nitalic nunderlined'),
    'docstring': TextStyle('#000080 nbold nitalic nunderlined'),
    'comment': TextStyle('#008000 nbold italic nunderlined'),
    'self': TextStyle('#94558D nbold italic nunderlined'),
    'numbers': TextStyle('#000080 nbold nitalic nunderlined'),
    'predefined': TextStyle('#B200B2 nbold nitalic nunderlined'),
    'docstringTag': TextStyle('#0000FF bold nitalic underlined'),
}

DEFAULT_DARK_STYLES = {
    'keyword': TextStyle('#CC7832 bold nitalic nunderlined'),
    'builtins': TextStyle('#CC7832 nbold nitalic nunderlined'),
    'operator': TextStyle('#A9B7C6 nbold nitalic nunderlined'),
    'punctuation': TextStyle('#A9B7C6 nbold nitalic nunderlined'),
    'decorator': TextStyle('#BBB529 nbold nitalic nunderlined'),
    'brace': TextStyle('#AAAAAA nbold nitalic nunderlined'),
    'class': TextStyle('#A9B7C6 bold nitalic nunderlined'),
    'function': TextStyle('#A9B7C6 bold nitalic nunderlined'),
    'string': TextStyle('#A5C261 nbold nitalic nunderlined'),
    'docstring': TextStyle('#629755 nbold nitalic nunderlined'),
    'comment': TextStyle('#808080 nbold italic nunderlined'),
    'self': TextStyle('#94558D nbold italic nunderlined'),
    'numbers': TextStyle('#6897B3 nbold nitalic nunderlined'),
    'predefined': TextStyle('#B200B2 nbold nitalic nunderlined'),
    'docstringTag': TextStyle('#427735 bold nitalic underlined')
}

#
# Default settings value
#
#: Default tab size
TAB_SIZE = 4
MARGIN_POS = 80


#
# Enumerations
#
class PanelPosition:
    """
    Enumerate the possible panel positions
    """
    #: top margin
    TOP = 0
    # left margin
    LEFT = 1
    # right margin
    RIGHT = 2
    # bottom margin
    BOTTOM = 3

