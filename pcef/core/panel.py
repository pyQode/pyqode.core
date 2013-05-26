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
This module contains the definition of a panel extension
"""
import pcef
from pcef.core.extension import Extension


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


class Panel(pcef.QtGui.QWidget, Extension):
    """
    Base class for editor Panel widgets.

    A Panel is a QWidget and :class:`pcef.Extension` that can be installed
    around the text edit widget (in the document margin).
    """
    def __init__(self, name, description, parent):
        pcef.Extension.__init__(self, name, description)
        pcef.QtGui.QWidget.__init__(self, parent)

    def install(self, editor):
        Extension.install(self, editor)
        self.setParent(editor)

    def onStateChanged(self, state):
        """ Shows/Hides the Panel

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        print "On state changed"
        if state is True:
            self.show()
        else:
            self.hide()
