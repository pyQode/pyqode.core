#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyQode - Python/Qt Code Editor widget
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the marker panel
"""
from pyqode.qt import QtCore, QtGui
from pyqode.core.panel import Panel
from pyqode.core.system import DelayJobRunner, memoized


class Marker(QtCore.QObject):
    """
    Defines a marker: a line number (position), an icon (string) and an
    optional description string used as a tool tip.

    The position of the marker can be changed dynamically.
    """

    @property
    def icon(self):
        """
        Returns the icon file name. Read-only.
        """
        return self.__icon

    @property
    def description(self):
        """ Returns the marker description. """
        return self.__description

    def __init__(self, position, icon="", description="", parent=None):
        """
        :param position: The marker position/line number.

        :param icon: the icon filename.

        :param parent: The optional parent object.
        """
        QtCore.QObject.__init__(self, parent)
        #: The position of the marker.
        self.position = position
        self.__icon = icon
        self.__description = description


class MarkerPanel(Panel):
    """
    This panels takes care of drawing icons at a specific line position.

    Use addMarker, removeMarker and clearMarkers to manage the collection if
    displayed makers.

    This panel exposes to signal:
      - addMarkerRequest: when the user click the panel where there is no
                          marker
      - removeMarkerRequest: when the user click on a marker on the panel
    """
    DESCRIPTION = "Draw icons in a side panel"
    IDENTIFIER = "markerPanel"

    addMarkerRequest = QtCore.Signal(int)
    removeMarkerRequest = QtCore.Signal(int)

    def __init__(self):
        Panel.__init__(self)
        self.__markers = []
        self.__icons = {}
        self.__previousLine = -1
        self.scrollable = True
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=100)
        self.setMouseTracking(True)
        self.__toRemove = []

    def addMarker(self, marker):
        """
        Adds the marker to the panel.

        :param marker: Marker to add
        """
        key, val = self.makeMarkerIcon(marker.icon)
        if key and val:
            self.__icons[key] = val
        self.__markers.append(marker)
        doc = self.editor.document()
        assert isinstance(doc, QtGui.QTextDocument)
        block = doc.findBlockByLineNumber(marker.position - 1)
        usrData = block.userData()
        if hasattr(usrData, "marker"):
            usrData.marker = marker

    @memoized
    def makeMarkerIcon(self, icon):
        if isinstance(icon, tuple):
            return icon[0], QtGui.QIcon.fromTheme(
                icon[0], QtGui.QIcon(icon[1]))
        elif isinstance(icon, str):
            return icon, QtGui.QIcon(icon)
        else:
            return None, None

    def removeMarker(self, marker):
        """
        Removes the marker from the panel

        :param marker: Marker to remove
        """
        self.__markers.remove(marker)
        self.__toRemove.append(marker)

    def clearMarkers(self):
        """ Clears the markers list """
        self.__markers[:] = []

    def getMarkerForLine(self, line):
        """
        Returns the marker positioned at line or None.

        :param line: The marker line.

        :return: Marker of None
        """
        for marker in self.__markers:
            if line == marker.position:
                return marker

    def sizeHint(self):
        """ Returns the widget size hint (based on the editor font size) """
        fm = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(fm.height(), fm.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for top, blockNumber, block in self.editor.visibleBlocks:
            usrData = block.userData()
            if hasattr(usrData, "marker"):
                marker = usrData.marker
                if marker in self.__toRemove:
                    usrData.marker = None
                    self.__toRemove.remove(marker)
                    continue
                if marker and marker.icon:
                    r = QtCore.QRect()
                    r.setX(0)
                    r.setY(top)
                    r.setWidth(self.sizeHint().width())
                    r.setHeight(self.sizeHint().height())
                    if isinstance(marker.icon, tuple):
                        key = marker.icon[0]
                    else:
                        key = marker.icon
                    self.__icons[key].paint(painter, r)

    def mousePressEvent(self, event):
        line = self.editor.lineNumber(event.pos().y())
        if self.getMarkerForLine(line):
            self.removeMarkerRequest.emit(line)
        else:
            self.addMarkerRequest.emit(line)

    def mouseMoveEvent(self, event):
        line = self.editor.lineNumber(event.pos().y())
        marker = self.getMarkerForLine(line)
        if marker and marker.description:
            if self.__previousLine != line:
                self.__jobRunner.requestJob(self.__displayTooltip, False,
                                            marker.description,
                                            self.editor.linePos(
                                                marker.position - 2))
        else:
            self.__jobRunner.cancelRequests()
        self.__previousLine = line

    def leaveEvent(self, *args, **kwargs):
        QtGui.QToolTip.hideText()
        self.__previousLine = -1

    def __displayTooltip(self, tooltip, top):
        QtGui.QToolTip.showText(self.mapToGlobal(QtCore.QPoint(
            self.sizeHint().width(), top)), tooltip, self)


if __name__ == '__main__':
    from pyqode.core import QGenericCodeEdit, constants

    class Example(QGenericCodeEdit):

        def __init__(self):
            QGenericCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.installPanel(MarkerPanel())
            marker = Marker(5, icon=constants.ACTION_GOTO_LINE[0],
                            description="First marker")
            self.markerPanel.addMarker(marker)
            # add another action in 5s
            QtCore.QTimer.singleShot(5000, self.addOtherMarker)

        def addOtherMarker(self):
            m = self.markerPanel.getMarkerForLine(5)
            m.position = 7
            marker = Marker(15, icon=constants.ACTION_PASTE[0],
                            description="Second marker")
            self.markerPanel.addMarker(marker)
            # clear all in 15s
            QtCore.QTimer.singleShot(15000, self.markerPanel.clearMarkers)

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
