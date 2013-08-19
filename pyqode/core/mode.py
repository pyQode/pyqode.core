#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
This module contains the definition of the Mode class
"""
import weakref
from pyqode.qt import QtCore


class Mode(object):
    """
    Base class for editor extension/mode. An extension is a "thing" that can be
    installed on the QCodeEdit to add new behaviours.

    An extension is added to a QCodeEdit by using the addMode or addPanel
    methods.

    Subclasses must/should override the following methods:
        - _onStateChanged: to connect/disconnect to/from the code edit signals
        - _onStyleChanged: to refresh ui colors (mainly used by panels)
        - _onSettingsChanged: to refresh some settings value.
    """
    #: The mode identifier, must redefined for every subclasses
    IDENTIFIER = ""
    #: The mode description, must redefined for every subclasses
    DESCRIPTION = ""

    @property
    def editor(self):
        """
        Provides easy access to the CodeEditorWidget weakref

        :rtype: pyqode.core.QCodeEdit
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Enabled flag
        """
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled flag

        :param enabled: New enable flag value
        """
        if enabled != self.__enabled:
            self.__enabled = enabled
            self._onStateChanged(enabled)

    def __init__(self):
        """
        Creates the extension. Uses self.IDENTIFIER and self.DESCRIPTION to
        setup sefl.name and self.description (you can override them after
        calling this constructor if you need it).
        """
        #: Mode name
        self.name = self.IDENTIFIER
        #: Mode description
        self.description = self.DESCRIPTION
        #: Mode enables state (subclasses must implement onStateChanged to
        #  disconnect their slots to disable any actions)
        self.__enabled = False
        #: Editor instance
        self._editor = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def _onInstall(self, editor):
        """
        Installs the extension on the editor.

        .. warning::
            For internal use only.

        .. warning::
            Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pyqode.QCodeEdit
        """
        self._editor = weakref.ref(editor)
        self.enabled = True
        editor.style.valueChanged.connect(self._onStyleChanged)
        editor.settings.valueChanged.connect(self._onSettingsChanged)

    def _onUninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self._editor = None

    def _onStateChanged(self, state):
        """
        Called when the enable state changed.

        .. warning: Raises NotImplementedError. Subclasses must override this
                    method to disconnect their slots.

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        raise NotImplementedError()

    def _onStyleChanged(self, section, key):
        """
        Automatically called when a style property changed.

        .. note: If the editor style changed globally, key will be set to "".
        """
        pass

    def _onSettingsChanged(self, section, key):
        """
        Automatically called when a settings property changed

        .. note: If the editor style changed globally, key will be set to "".
        """
        pass
