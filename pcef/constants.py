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
EDITOR_BACKGROUND = "#FFFFFF"
EDITOR_FOREGROUND = "#000000"
EDITOR_WS_FOREGROUND = "#dddddd"
SELECTION_BACKGROUND = "#6182F3"
SELECTION_FOREGROUND = "#ffffff"
LINE_NBR_BACKGROUND = "#dddddd"
LINE_NBR_FOREGROUND = "#888888"

# Default highlighter styles values, mostly for the python highlighter but they
# may be shared between different highlighter/languages
DEFAULT_STYLES = {
    'keyword': '#808000 bold',
    'operator': 'orange',
    'punctuation': 'darkGray',
    'decorator': '#808000',
    'brace': '#404040',
    'class': '#800080 bold',
    'function': '#800080',
    'string': '#008000',
    'docstring': '#000080',
    'comment': '#008000 italic',
    'self': '#94558D italic',
    'numbers': '#000080',
    'predefined': 'maroon',
    'docstringTag': '#0000FF bold underlined',
}

DEFAULT_DARK_STYLES = {
    'keyword': '#CC7832 bold',
    'operator': '#A9B7C6',
    'punctuation': '#A9B7C6',
    'decorator': '#BBB529',
    'brace': '#AAAAAA',
    'class': '#A9B7C6 bold',
    'function': '#A9B7C6 bold',
    'string': '#A5C261',
    'docstring': '#629755',
    'comment': '#808080 italic',
    'self': '#94558D italic',
    'numbers': '#6897B3',
    'predefined': '#CC7832',
    'docstringTag': '#427735 bold underlined'
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

