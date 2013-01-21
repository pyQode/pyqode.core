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
Contains default styles definitions (both for the PCEF and pygmens)
"""
from pygments.style import Style as PygmentsStyle
from pygments.token import *

from pcef.config.style import Style, DEFAULT_FONT, DEFAULT_FONT_SIZE


#
# Builtin pygments styles
#
class PygmentsWhiteStyle(PygmentsStyle):
    """
    Our default white pygments style definition
    """
    background_color = '#ffffff'
    styles = {
        Token:                  "noinherit #121212",
        Text:                   'noinherit #121212',
        Whitespace:             'noinherit #dddddd',
        Error:                  'noinherit #CC0000 underline',
        Keyword:                'noinherit #4174fa bold',
        Name.Function:          'noinherit #FFBB09 bold',
        Name.Class:             'noinherit #008080 bold',
        Name.Decorator:         'noinherit #4174fa',
        String:                 'noinherit #9A1016 italic',
        String.Doc:             'noinherit #8080FF italic',
        Number:                 'noinherit #FF12D7',
        Operator:               'noinherit #FF6466',
        Punctuation:            'noinherit #222222',
        Comment:                'noinherit #128026',
        Name.Builtin:           'noinherit #4174fa',
        Name.Builtin.Pseudo:    'noinherit #94558D'}


#class PygmentsDarkStyle(PygmentsStyle):
#    """
#    Our default dark pygments styles definition
#    """
#    background_color = '#1a1d1f'
#    styles = {
#        Token:                  "noinherit #bcbcbc",
#        Text:                   'noinherit #bcbcbc',
#        Whitespace:             'noinherit #3a3a3a',
#        Error:                  'noinherit #CC0000 underline',
#        Keyword:                'noinherit #4174fa bold',
#        Name.Function:          'noinherit #FFBB09',
#        Name.Class:             'noinherit #008080 bold',
#        Name.Decorator:         'noinherit #4174fa',
#        String:                 'noinherit #9A1016 italic',
#        String.Doc:             'noinherit #8080FF italic',
#        Number:                 'noinherit #FF12D7',
#        Operator:               'noinherit #FF6466',
#        Punctuation:            'noinherit #BCBCBC',
#        Comment:                'noinherit #128026',
#        Name.Builtin:           'noinherit #4174fa',
#        Name.Builtin.Pseudo:    'noinherit #94558D'}


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
        Punctuation:            'noinherit #A9B7C6',
        Comment:                'noinherit #808080',
        Name.Builtin:           'noinherit #cc7832',
        Name.Builtin.Pseudo:    'noinherit #94558D'}


class DefaultWhiteStyle(Style):
    """ Our default style """

    def __init__(self):
        super(DefaultWhiteStyle, self).__init__()
        #: Pygments syntax highlighting style
        self.pygmentsStyle = PygmentsWhiteStyle
        #: Right margin color
        self.marginColor = '#FF0000'
        self.marginPos = 80
        self.activeLineColor = '#FFFFC0'
        self.selectionBackgroundColor = '#6182F3'
        self.selectionTextColor = '#ffffff'
        self.lineNbrColor = '#808080'
        self.panelSeparatorColor = '#dddddd'
        self.panelsBackgroundColor = '#eeeeee'
        self.fontName = DEFAULT_FONT
        self.fontSize = DEFAULT_FONT_SIZE
        self.searchColor = '#000000'
        self.searchBackgroundColor = '#FFFF00'


class DefaultDarkStyle(Style):
    """ Our default dark style"""

    def __init__(self):
        super(DefaultDarkStyle, self).__init__()
        #: Pygments syntax highlighting style
        self.pygmentsStyle = PygmentsDarkStyle
        #: Right margin color
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