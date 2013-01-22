#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains the definition of the PCEF style options
"""
import sys
from pygments.styles import get_style_by_name

#
# Constants
#
#: Default editor font (monospace on GNU/Linux, Courier New on windows)
DEFAULT_FONT = "monospace"
if sys.platform == "win32":
    DEFAULT_FONT = "Courier New"
#: Default editor font size
DEFAULT_FONT_SIZE = 10


class Style(object):
    """Visual style options placeholder.

    This class contains the style options needed by all the components of
    PCEF project (from text edit widget to panels,...)

    Style options mainly consists of colors and the font definition.

    User can extend this class to define their own style or to add extra options
    needed by their own modes/widgets.
    """

    def __init__(self):
        #: Pygments syntax highlighting style (used by SyntaxHighlighting Mode)
        self.pygmentsStyle = ''
        #: Right margin color (used by
        self.marginColor = ''
        #: Right margin pos
        self.marginPos = 80
        #: The active line color
        self.activeLineColor = ''
        #: The selection background color
        self.selectionBackgroundColor = ''
        #: The selection text color
        self.selectionTextColor = ''
        #: the line nbr color
        self.lineNbrColor = ''
        #: A default panel background color
        self.panelsBackgroundColor = ''
        #: A default panel separator color
        self.panelSeparatorColor = ''
        #: A default font
        self.fontName = ''
        #: Search results foreground
        self.searchColor = ''
        #: Search results background
        self.searchBackgroundColor = ''
        #: A default font size
        self.fontSize = 10
        # Show whitespaces
        self.showWhitespaces = True

    @property
    def backgroundColor(self):
        """
        Return the style background color as defined by the pygmentsStyle
        """
        style = self.pygmentsStyle
        if isinstance(self.pygmentsStyle, str):
            style = get_style_by_name(self.pygmentsStyle)
        return style.background_color

    def tokenColor(self, token):
        """
        Get a token color out of the pygmentsStyle.
        If the toke color is not found or null, the method returns '#000000'
        :return: str -- the color string formatted as html color (#RRggBB)
        """
        style = self.pygmentsStyle
        if isinstance(self.pygmentsStyle, str):
            style = get_style_by_name(self.pygmentsStyle)
        c = style.style_for_token(token)['color']
        if c is None:
            c = '000000'
        return "#{0}".format(c)
