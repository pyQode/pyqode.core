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
""" Contains a dark style inspired the darcula theme from Jetbrains """
from pygments.style import Style as PygmentsStyle
from pygments.token import *
from pcef.style import Style
from pcef.style import DEFAULT_FONT
from pcef.style import DEFAULT_FONT_SIZE


class PygmentsWhiteStyle(PygmentsStyle):
    """
    Pygments theme inspired by the darcula theme (Pycharm)
    """
    background_color = '#ffffff'
    styles = {
        Token:                  "noinherit #202020",
        Text:                   'noinherit #202020',
        Whitespace:             'noinherit #dddddd',
        Error:                  'noinherit #CC0000 underline',
        Keyword:                'noinherit #204a87',
        Name.Function:          'noinherit #c4a000 bold',
        Name.Class:             'noinherit #5c3566 bold',
        Name.Decorator:         'noinherit #204a87',
        String:                 'noinherit #4e9a06 italic',
        String.Doc:             'noinherit #4e9a06 italic',
        Number:                 'noinherit #845902',
        Operator:               'noinherit #f57900',
        Operator.Word:          'noinherit #204a87',
        Punctuation:            'noinherit #202020',
        Comment:                'noinherit #888a85',
        Name.Builtin:           'noinherit #204a87',
        Name.Builtin.Pseudo:    'noinherit #94558D'}


class WhiteStyle(Style):
    """ Our default dark style"""

    def __init__(self):
        super(WhiteStyle, self).__init__("White")
        self.pygmentsStyle = PygmentsWhiteStyle
        self.marginColor = '#FF0000'
        self.activeLineColor = '#E4EDF8'
        self.selectionBackgroundColor = '#3465a4'
        self.selectionTextColor = '#ffffff'
        self.lineNbrColor = '#888a85'
        self.panelSeparatorColor = '#babdb6'
        self.panelsBackgroundColor = '#eeeeec'
        self.fontName = DEFAULT_FONT
        self.fontSize = DEFAULT_FONT_SIZE
        self.searchColor = '#000000'
        self.searchBackgroundColor = '#FFFF00'
        self.warningColor = "#4040FF"
        self.errorColor = "#CC4040"