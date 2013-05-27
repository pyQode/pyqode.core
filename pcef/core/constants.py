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
This module holds most of the PCEF constants (enumerations, defines,...)
"""
import sys


#
# Default style values
#
#: Default editor font (monospace on GNU/Linux, Courier New on windows)
DEFAULT_FONT = "monospace"
if sys.platform == "win32":
    DEFAULT_FONT = "Consolas"
elif sys.platform == "darwin":
    DEFAULT_FONT = "Monaco"
#: Default editor font size
DEFAULT_FONT_SIZE = 10
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


#
# Default settings value
#
#: Default tab size
DEFAULT_TAB_SIZE = 4


#
# Enumerations
#
class PanelPosition:
    """
    Enumerate the possible panel positions
    """
    #
    # Panel positions
    TOP = 0  # top margin
    LEFT = 1  # left margin
    RIGHT = 2  # right margin
    BOTTOM = 3  # bottom margin

