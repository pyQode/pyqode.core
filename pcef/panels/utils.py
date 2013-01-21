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
Contains utils panel that are not used by any editor but could be useful to
ide writers:
    - QBookmarkPanel
"""
from PySide.QtGui import QIcon
from pcef.panels.generics import QMarkersPanel, Marker


class QBookmarkPanel(QMarkersPanel):

    def __init__(self, icon=":/icons/rc/bookmark.png", parent=None):
        QMarkersPanel.__init__(self, "BookmarksPanel", False, parent)
        self.addMarkerRequested.connect(self.addUserMarker)
        #: marker icon
        self._icon = icon

    def addUserMarker(self, panel, lineNbr):
        panel.addMarker(Marker(lineNbr, QIcon(self._icon), None))
