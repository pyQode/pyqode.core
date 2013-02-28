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


class PygmentsDarkStyle(PygmentsStyle):
    """
    Pygments theme inspired by the darcula theme (Pycharm)
    """
    background_color = '#2b2b2b'
    styles = {
        Token:                  "noinherit #A9B7C6",
        Text:                   'noinherit #A9B7C6',
        Whitespace:             'noinherit #3A3A3A',
        Error:                  'noinherit #CC0000 underline',
        Keyword:                'noinherit #CC7832',
        Name.Function:          'noinherit #A9B7C6 bold',
        Name.Class:             'noinherit #A9B7C6 bold',
        Name.Decorator:         'noinherit #BBB529',
        String:                 'noinherit #A5C261 italic',
        String.Doc:             'noinherit #629755 italic',
        Number:                 'noinherit #6897B3',
        Operator:               'noinherit #A9B7C6',
        Operator.Word:          'noinherit #CC7832',
        Punctuation:            'noinherit #A9B7C6',
        Comment:                'noinherit #808080',
        Name.Builtin:           'noinherit #cc7832',
        Name.Builtin.Pseudo:    'noinherit #94558D'}


class DarkStyle(Style):
    """ Our default dark style"""

    def __init__(self):
        super(DarkStyle, self).__init__("Dark")
        self.pygmentsStyle = PygmentsDarkStyle
        self.marginColor = '#FF0000'
        self.activeLineColor = '#323232'
        self.selectionBackgroundColor = '#2142A3'
        self.selectionTextColor = '#ffffff'
        self.lineNbrColor = '#808080'
        self.panelSeparatorColor = '#3F4145'
        self.panelsBackgroundColor = '#343739'
        self.fontName = DEFAULT_FONT
        self.fontSize = DEFAULT_FONT_SIZE
        self.searchColor = '#000000'
        self.searchBackgroundColor = '#FFFF00'
        self.warningColor = "#CCCC20"
        self.errorColor = "#CC4040"