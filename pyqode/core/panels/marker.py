#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the marker panel
"""
from pyqode.core import logger
from PyQt4 import QtCore, QtGui
from pyqode.core.editor import Panel
from pyqode.core.api.system import DelayJobRunner, memoized


class Marker(QtCore.QObject):
    """
    A marker is an icon draw on a marker panel at a specific line position and
    with a possible tooltip.
    """

    @property
    def position(self):
        """
        Gets the marker position (line number)
        :type: int
        """
        return self.__position

    @property
    def icon(self):
        """
        Gets the icon file name. Read-only.
        """
        return self.__icon

    @property
    def description(self):
        """ Gets the marker description. """
        return self.__description

    def __init__(self, position, icon="", description="", parent=None):
        """
        :param position: The marker position/line number.
        :type position: int

        :param icon: the icon filename.
        :type icon: str

        :param parent: The optional parent object.
        :type parent: QtCore.QObject or None
        """
        QtCore.QObject.__init__(self, parent)
        #: The position of the marker (line number)
        self.__position = position
        self.__icon = icon
        self.__description = description


class MarkerPanel(Panel):
    """
    This panels takes care of drawing icons at a specific line number.

    Use addMarker, removeMarker and clearMarkers to manage the collection of
    displayed makers.

    You can create a user editable panel (e.g. a breakpoints panel) by using
    the following signals:

        - :attr:`pyqode.core.MarkerPanel.addMarkerRequested`
        - :attr:`pyqode.core.MarkerPanel.removeMarkerRequested`
    """
    #: The panel identifier
    DESCRIPTION = "Draw icons in a side panel"
    #: The panel description
    IDENTIFIER = "markerPanel"

    #: Signal emitted when the user clicked in a place where there is no
    #: marker.
    addMarkerRequested = QtCore.pyqtSignal(int)

    #: Signal emitted when the user clicked on an existing marker.
    removeMarkerRequested = QtCore.pyqtSignal(int)

    def __init__(self):
        Panel.__init__(self)
        self.__markers = []
        self.__icons = {}
        self.__previousLine = -1
        self.scrollable = True
        self.__jobRunner = DelayJobRunner(self, nb_threads_max=1, delay=100)
        self.setMouseTracking(True)
        self.__toRemove = []

    def add_marker(self, marker):
        """
        Adds the marker to the panel.

        :param marker: Marker to add
        :type marker: pyqode.core.Marker
        """
        key, val = self.make_marker_icon(marker.icon)
        if key and val:
            self.__icons[key] = val
        self.__markers.append(marker)
        doc = self.editor.document()
        assert isinstance(doc, QtGui.QTextDocument)
        block = doc.findBlockByLineNumber(marker.position - 1)
        user_data = block.userData()
        if hasattr(user_data, "marker"):
            user_data.marker = marker
        self.repaint()

    @staticmethod
    @memoized
    def make_marker_icon(icon):
        if isinstance(icon, tuple):
            return icon[0], QtGui.QIcon.fromTheme(
                icon[0], QtGui.QIcon(icon[1]))
        elif isinstance(icon, str):
            return icon, QtGui.QIcon(icon)
        else:
            return None, None

    def remove_marker(self, marker):
        """
        Removes a marker from the panel

        :param marker: Marker to remove
        :type marker: pyqode.core.Marker
        """
        self.__markers.remove(marker)
        self.__toRemove.append(marker)
        self.repaint()

    def clear_markers(self):
        """ Clears the markers list """
        while len(self.__markers):
            self.remove_marker(self.__markers[0])

    def marker_for_line(self, line):
        """
        Returns the marker that is displayed at the specified line number if
        any.

        :param line: The marker line.

        :return: Marker of None
        :rtype: pyqode.core.Marker
        """
        for marker in self.__markers:
            if line == marker.position:
                return marker

    def sizeHint(self):
        fm = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(fm.height(), fm.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for top, blockNumber, block in self.editor.visible_blocks:
            user_data = block.userData()
            if hasattr(user_data, "marker"):
                marker = user_data.marker
                if marker in self.__toRemove:
                    user_data.marker = None
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
        line = self.editor.line_nbr_from_position(event.pos().y())
        if self.marker_for_line(line):
            logger.debug("Remove marker requested")
            self.removeMarkerRequested.emit(line)
        else:
            logger.debug("Add marker requested")
            self.addMarkerRequested.emit(line)

    def mouseMoveEvent(self, event):
        line = self.editor.line_nbr_from_position(event.pos().y())
        marker = self.marker_for_line(line)
        if marker and marker.description:
            if self.__previousLine != line:
                self.__jobRunner.request_job(self._display_tooltip, False,
                                             marker.description,
                                             self.editor.line_pos_from_number(
                                                 marker.position - 2))
        else:
            self.__jobRunner.cancel_requests()
        self.__previousLine = line

    def leaveEvent(self, *args, **kwargs):
        QtGui.QToolTip.hideText()
        self.__previousLine = -1

    def _display_tooltip(self, tooltip, top):
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
            self.markerPanel.add_marker(marker)
            # add another action in 5s
            QtCore.QTimer.singleShot(1000, self.add_marker)

        def add_marker(self):
            m = self.markerPanel.marker_for_line(5)
            m.position = 7
            marker = Marker(15, icon=constants.ACTION_PASTE[0],
                            description="Second marker")
            self.markerPanel.add_marker(marker)
            # clear all in 2s
            QtCore.QTimer.singleShot(2000, self.markerPanel.clear_markers)

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
