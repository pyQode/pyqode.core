#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
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
