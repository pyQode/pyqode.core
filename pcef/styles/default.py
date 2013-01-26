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
""" Contains the default white style """
from pcef.style import Style
from pcef.style import DEFAULT_FONT
from pcef.style import DEFAULT_FONT_SIZE


class DefaultStyle(Style):
    """ Our default style """

    def __init__(self):
        super(DefaultStyle, self).__init__("Default")
        self.pygmentsStyle = 'default'
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
