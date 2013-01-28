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
Contains miscellaneous panels not used by the editors but that could be useful for the end user
(at least them are examples or custom panels)
"""
from PySide.QtGui import QIcon
from pcef.panels.marker import QMarkersPanel
from pcef.panels.marker import Marker


class QUserMarkersPanel(QMarkersPanel):
    """ A simple marker panel that let the user add/remove marker using mouse clicks.
    This could be used for bookmarks, breakpoints,...
    """
    def __init__(self, icon=":/icons/rc/bookmark.png", parent=None):
        QMarkersPanel.__init__(self, "User markers", False, parent)
        self.addMarkerRequested.connect(self.addUserMarker)
        #: marker icon
        self._icon = icon

    def addUserMarker(self, panel, lineNbr):
        panel.addMarker(Marker(lineNbr, QIcon(self._icon), None))
