# -*- coding: utf-8 -*-
"""
This module contains the marker panel
"""
import logging
from PyQt4 import QtCore, QtGui

from pyqode.core.frontend import Panel
from pyqode.core import frontend
from pyqode.core.frontend.utils import DelayJobRunner, memoized


def _logger():
    return logging.getLogger(__name__)


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
        return self._position

    @property
    def icon(self):
        """
        Gets the icon file name. Read-only.
        """
        return self._icon

    @property
    def description(self):
        """ Gets the marker description. """
        return self._description

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
        self._position = position
        self._icon = icon
        self._description = description


class MarkerPanel(Panel):
    """
    This panels takes care of drawing icons at a specific line number.

    Use addMarker, removeMarker and clearMarkers to manage the collection of
    displayed makers.

    You can create a user editable panel (e.g. a breakpoints panel) by using
    the following signals:

        - :attr:`pyqode.core.MarkerPanel.add_marker_requested`
        - :attr:`pyqode.core.MarkerPanel.remove_marker_requested`
    """
    #: Signal emitted when the user clicked in a place where there is no
    #: marker.
    add_marker_requested = QtCore.pyqtSignal(int)
    #: Signal emitted when the user clicked on an existing marker.
    remove_marker_requested = QtCore.pyqtSignal(int)

    def __init__(self):
        Panel.__init__(self)
        self._markers = []
        self._icons = {}
        self._previous_line = -1
        self.scrollable = True
        self._job_runner = DelayJobRunner(self, nb_threads_max=1, delay=100)
        self.setMouseTracking(True)
        self._to_remove = []

    def add_marker(self, marker):
        """
        Adds the marker to the panel.

        :param marker: Marker to add
        :type marker: pyqode.core.Marker
        """
        key, val = self.make_marker_icon(marker.icon)
        if key and val:
            self._icons[key] = val
        self._markers.append(marker)
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
        self._markers.remove(marker)
        self._to_remove.append(marker)
        self.repaint()

    def clear_markers(self):
        """ Clears the markers list """
        while len(self._markers):
            self.remove_marker(self._markers[0])

    def marker_for_line(self, line):
        """
        Returns the marker that is displayed at the specified line number if
        any.

        :param line: The marker line.

        :return: Marker of None
        :rtype: pyqode.core.Marker
        """
        for marker in self._markers:
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
                if marker in self._to_remove:
                    user_data.marker = None
                    self._to_remove.remove(marker)
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
                    self._icons[key].paint(painter, r)

    def mousePressEvent(self, event):
        line = frontend.line_nbr_from_position(self.editor, event.pos().y())
        if self.marker_for_line(line):
            _logger().debug("remove marker requested")
            self.remove_marker_requested.emit(line)
        else:
            _logger().debug("add marker requested")
            self.add_marker_requested.emit(line)

    def mouseMoveEvent(self, event):
        line = frontend.line_nbr_from_position(self.editor, event.pos().y())
        marker = self.marker_for_line(line)
        if marker and marker.description:
            if self._previous_line != line:
                self._job_runner.request_job(self._display_tooltip, False,
                                             marker.description,
                                             frontend.line_pos_from_number(
                                                 self.editor,
                                                 marker.position - 2))
        else:
            self._job_runner.cancel_requests()
        self._previous_line = line

    def leaveEvent(self, *args, **kwargs):
        QtGui.QToolTip.hideText()
        self._previous_line = -1

    def _display_tooltip(self, tooltip, top):
        QtGui.QToolTip.showText(self.mapToGlobal(QtCore.QPoint(
            self.sizeHint().width(), top)), tooltip, self)
