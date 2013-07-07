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
import pcef
from pcef.qt import QtGui
from pcef.core.mode import Mode


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
        pcef.core.mode.Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        self.__scrollable = False
        #: The background brush (automatically updated when panelBackground
        #: change)
        self.backgroundBrush = None
        #: The foreground pen (automatically updated when panelForeground
        #: changed)
        self.foregroundPen = None

    def install(self, editor):
        """
        Extends the Mode.install method to set the editor instance
        as the parent widget.

        Also adds the panelBackground and panel foreground.

        :param editor: QCodeEdit instance
        """
        Mode.install(self, editor)
        self.setParent(editor)
        self.editor.refreshPanels()
        self.backgroundBrush = QtGui.QBrush(QtGui.QColor(
            self.editor.style.value("panelBackground")))
        self.foregroundPen = QtGui.QPen(QtGui.QColor(
            self.editor.style.value("panelForeground")))

    def onStateChanged(self, state):
        """ Shows/Hides the Panel

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if state is True:
            self.show()
        else:
            self.hide()
        self.editor.refreshPanels()

    def onStyleChanged(self, section, key, value):
        """
        Repaints widget if the panel background color changed.

        :param section:
        :param key:
        :param value:
        """
        if key == "panelBackground":
            self.backgroundBrush = QtGui.QBrush(QtGui.QColor(value))
            self.editor.repaint()
        elif key == "panelForeground":
            self.foregroundPen = QtGui.QPen(QtGui.QColor(value))
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