#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the definition of a panel mode
"""
from pcef.core.mode import Mode
from pcef.qt import QtGui


class Panel(QtGui.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a widget.

    Panels are drawn in the QCodeEdit viewport margins.
    """

    @property
    def scrollable(self):
        """
        A scrollable panel will follow the editor's scrollbars. Left and right
        panels follow the vertical scrollbar. Top and bottom panels follow the
        horizontal scrollbar.
        """
        return self.__scrollable

    @scrollable.setter
    def scrollable(self, value):
        """ Sets the scrollable flag. """
        self.__scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        #: Panel order into the zone it is installed. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.zoneOrder = -1
        self.__scrollable = False
        #: The background brush (automatically updated when panelBackground
        #: change)
        self.backgroundBrush = None
        #: The foreground pen (automatically updated when panelForeground
        #: changed)
        self.foregroundPen = None

    def _onInstall(self, editor):
        """
        Extends the Mode.install method to set the editor instance
        as the parent widget.

        Also adds the panelBackground and panel foreground.

        :param editor: QCodeEdit instance
        """
        Mode._onInstall(self, editor)
        self.setParent(editor)
        self.editor.refreshPanels()
        self.backgroundBrush = QtGui.QBrush(QtGui.QColor(
            self.editor.style.value("panelBackground")))
        self.foregroundPen = QtGui.QPen(QtGui.QColor(
            self.editor.style.value("panelForeground")))

    def _onStateChanged(self, state):
        """ Shows/Hides the Panel

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if not self.editor.isVisible():
            return
        if state is True:
            self.show()
        else:
            self.hide()

    def _onStyleChanged(self, section, key):
        """
        Repaints widget if the panel background color changed.

        :param section:
        :param key:
        :param value:
        """
        if key == "panelBackground" or not key:
            self.backgroundBrush = QtGui.QBrush(
                self.editor.style.value("panelBackground"))
            self.editor.repaint()
        if key == "panelForeground" or not key:
            self.foregroundPen = QtGui.QPen(
                self.editor.style.value("panelForeground"))
            self.editor.repaint()

    def paintEvent(self, event):
        if self.isVisible():
            # fill background
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self.backgroundBrush)

    def showEvent(self, *args, **kwargs):
        self.editor.refreshPanels()

    def show(self):
        self.adjustSize()
        QtGui.QWidget.show(self)
        self.editor.refreshPanels()

    def hide(self):
        self.adjustSize()
        QtGui.QWidget.hide(self)
        self.editor.refreshPanels()
