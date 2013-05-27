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
""" Contains the definition of the PCEF style options """
import json
import sys
from pygments.styles import get_style_by_name
#
# Constants
#
#: Default editor font (monospace on GNU/Linux, Courier New on windows)
DEFAULT_FONT = "monospace"
if sys.platform == "win32":
    DEFAULT_FONT = "Consolas"
elif sys.platform == "darwin":
    DEFAULT_FONT = "Monaco"
#: Default editor font size
DEFAULT_FONT_SIZE = 10


class Style(object):
    """
    Defines style options used by all pcef widgets to setup their style.

    It mainly consists of a font definition, a pygments style and a series of colors used for various purposes.

    A style can be serialised to a JSON file using :func:`pcef.style.toJSON` and :func:`pcef.style.fromJSON`
    """

    def __init__(self, name):
        self.name = name
        #: Pygments syntax highlighting style (used by SyntaxHighlighting Mode)
        self.pygmentsStyle = ''
        #: Right margin color (used by
        self.marginColor = ''
        #: The active line color
        self.activeLineColor = ''
        #: The selection background color
        self.selectionBackgroundColor = ''
        #: The selection text color
        self.selectionTextColor = ''
        #: the line nbr color
        self.lineNbrColor = ''
        #: A default Panel background color
        self.panelsBackgroundColor = ''
        #: A default Panel separator color
        self.panelSeparatorColor = ''
        #: A default font
        self.fontName = ''
        #: Search results foreground
        self.searchColor = ''
        #: Search results background
        self.searchBackgroundColor = ''
        #: Warning color
        self.warningColor = ""
        #: Error color
        self.errorColor = ""
        #: A default font size
        self.fontSize = 10
        # Show whitespaces
        self.showWhitespaces = True
        self.resetDefault()

    def resetDefault(self):
        """
        Reset the style to the default white style.
        """
        self.pygmentsStyle = 'default'
        self.marginColor = '#FF0000'
        self.marginPos = 120
        self.activeLineColor = '#E4EDF8'
        self.selectionBackgroundColor = '#6182F3'
        self.selectionTextColor = '#ffffff'
        self.lineNbrColor = '#808080'
        self.panelSeparatorColor = '#cccccc'
        self.panelsBackgroundColor = '#dddddd'
        self.fontName = DEFAULT_FONT
        self.fontSize = DEFAULT_FONT_SIZE
        self.searchColor = '#000000'
        self.searchBackgroundColor = '#FFFF00'
        self.warningColor = "#8080FF"
        self.errorColor = "#CC4040"

    @property
    def backgroundColor(self):
        """
        Returns the style background color as defined in the pygmentsStyle.
        """
        style = self.pygmentsStyle
        if (isinstance(self.pygmentsStyle, str) or
                isinstance(self.pygmentsStyle, unicode)):
            style = get_style_by_name(self.pygmentsStyle)
        return style.background_color

    def tokenColor(self, token):
        """
        Gets a token color out of the pygmentsStyle.
        If the toke color is not found or null, the method returns '#000000'

        :return: The color string formatted as html color (#RRggBB)
        :rtype: str
        """
        style = self.pygmentsStyle
        if (isinstance(self.pygmentsStyle, str) or
                isinstance(self.pygmentsStyle, unicode)):
            style = get_style_by_name(self.pygmentsStyle)
        c = style.style_for_token(token)['color']
        if c is None:
            c = '000000'
        return "#{0}".format(c)


def toJSON(style):
    """
    Serialises a style to a json file

    :param style: style to serialise
    :type style: pcef.style.Style
    """
    assert isinstance(style, Style)
    with open("{0}.json".format(style.name), "w") as jsonFile:
        json.dump(style.__dict__, jsonFile, indent=4)


def fromJSON(filename):
    """
    :returns: A style instance read from a json file

    :param filename: style json filename

    :rtype: pcef.style.Style or None
    """
    style = Style("")
    with open(filename, "r") as jsonFile:
        style.__dict__ = json.load(jsonFile)
    return style
