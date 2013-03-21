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
Contains the bases classes of the project:
    - StyledObject
    - Mode
    - Panel
    - CodeEdit
    - QCodeEditorBase
"""
from pcef import styles


class StyledObject(object):
    """ Base class for objects that needs a style instance.

    Provides a property to get/set the object currentStyle. The property call an abstract
    method to force children to update their brushes, pens, colors,... (updateStyling)
    """

    def __init__(self):
        global __styleChanged
        self._style = styles.getStyle("Default")

    def __get_style(self):
        return self._style

    def __set_style(self, style):
        self._style = style
        self._onStyleChanged()

    #: Current style
    currentStyle = property(__get_style, __set_style)

    def _onStyleChanged(self):
        """
        Raises not ImplementError.

        Subclasses must overrides this method to update themselves whenever the
        style changed
        """
        raise NotImplementedError
