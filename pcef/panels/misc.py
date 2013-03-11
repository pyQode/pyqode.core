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
from pcef.panels.marker import MarkersPanel
from pcef.panels.marker import Marker


class UserMarkersPanel(MarkersPanel):
    """ A simple marker Panel that let the user add/remove marker using mouse clicks.
    This could be used for bookmarks, breakpoints,...
    """
    def __init__(self, icon=":/icons/rc/bookmark.png", parent=None):
        MarkersPanel.__init__(self, "User markers", False, parent)
        self.addMarkerRequested.connect(self.__addUserMarker)
        #: marker icon
        self._icon = icon

    def __addUserMarker(self, panel, lineNbr):
        """
        Add a user marker automatically on click

        :param panel: panel instance (self)
        :param lineNbr: where to put the marker
        """
        panel.addMarker(Marker(lineNbr, QIcon(self._icon), None))


class CheckersMarkerPanel(MarkersPanel):
    """ A marker panel dedicated to the checkers modes. It allow to add several messages on the same
    marker.

    """
    def __init__(self, parent=None):
        MarkersPanel.__init__(self, "Checkers marker panel", True, parent)
        self.icons = {0: ":/icons/rc/marker_warning.png",
                      1: ":/icons/rc/marker_error.png"}

    def addCheckerMarker(self, error_type, line, message):
        """
        Add a checker marker to the panel

        :param error_type: error type

        :param line: marker line

        :param message: marker message
        """
        for marker in self.markers:
            # combine messages
            if marker.position == line:
                # change icon/message to show the highest priority icon/message
                if marker.error_type < error_type:
                    marker.tooltip = "{0}\n{1}".format(message, marker.tooltip)
                    marker.icon = QIcon(self.icons[error_type])
                # just append message
                else:
                    marker.tooltip += "\n %s" % message
                return marker
        marker = Marker(line, icon=QIcon(self.icons[error_type]), tooltip=message)
        marker.error_type = error_type
        self.addMarker(marker)
        return marker

