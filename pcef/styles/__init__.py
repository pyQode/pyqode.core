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
from pcef.styles.dark import DarkStyle
from pcef.style import Style


#: Styles map
__STYLES = {'Default': Style("Default"),
            'Dark': DarkStyle()}


def getAllStyles():
    """ Returns the list of available styles """
    global __STYLES
    return __STYLES.keys()


def addStyle(newStyle):
    """
    Add a new style to the style map (can be loaded from a json file)
    :param newStyle: Style subclass instance
    """
    global __STYLES
    __STYLES[newStyle.name] = newStyle


def getStyle(name='Default'):
    """ Returns the style instance that match the style name
    :param name: style name
    :return: Style or None
    """
    global __STYLES
    return __STYLES[name]



