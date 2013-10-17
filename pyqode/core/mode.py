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
    Base class for editor extensions. An extension is a "thing" that can be
    installed on the QCodeEdit to add new behaviours or to modify the
    appearance.

    An extension is added to a QCodeEdit by using the
    :meth:`pyqode.core.QCodeEdit.installMode` or
    :meth:`pyqode.core.QCodeEdit.installPanel` methods.

    Subclasses must/should override the following methods:
        - :meth:`pyqode.core.Mode._onStateChanged`
        - :meth:`pyqode.core.Mode._onStyleChanged`
        - :meth:`pyqode.core.Mode._onSettingsChanged`

    Uses :attr:`pyqode.core.Mode.IDENTIFIER` and
    :attr:`pyqode.core.Mode.DESCRIPTION` to setup the mode name and
    description:

    .. code-block:: python

        class MyMode(Mode):
            IDENTIFIER = "myMode"
            DESCRIPTION = "Describes your mode here"

        m = MyMode()
        print(m.name, m.description)

        >>> ("myMode", "Describes your mode here" )
    """
    #: The mode identifier, must redefined for every subclasses
    IDENTIFIER = ""
    #: The mode description, must redefined for every subclasses
    DESCRIPTION = ""

    @property
    def editor(self):
        """
        Provides easy access to the CodeEditorWidget weakref. **READ ONLY**

        :type: pyqode.core.QCodeEdit
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Tell if the mode is enabled, :meth:`pyqode.core.Mode._onStateChanged` is
        called when the value changed.

        :type: bool
        """
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled != self.__enabled:
            self.__enabled = enabled
            self._onStateChanged(enabled)

    def __init__(self):
        #: Mode name/identifier. :class:`pyqode.core.QCodeEdit` use it as the
        #: attribute key when you install a mode.
        self.name = self.IDENTIFIER
        #: Mode description
        self.description = self.DESCRIPTION
        self.__enabled = False
        self._editor = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def _onInstall(self, editor):
        """
        Installs the extension on the editor. Subclasses might want to override
        this method to add new style/settings properties to the editor.

        .. note:: This method is called by QCodeEdit when you install a Mode.
                  You should never call it yourself, even in a subclass.

        .. warning:: Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pyqode.core.QCodeEdit
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

        This method does not do anything, you may override it if you need
        to connect/disconnect to the editor's signals (connect when state is
        true and disconnect when it is false).

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        pass

    def _onStyleChanged(self, section, key):
        """
        Automatically called when a style property changed.

        .. note: If the editor style changed globally, key will be set to an
                 empty string.

        :param section: The section which contains the property that has changed
        :type section: str

        :param key: The property key
        :type key: str
        """
        pass

    def _onSettingsChanged(self, section, key):
        """
        Automatically called when a settings property changed

        .. note: If the editor style changed globally, key will be set to an
                 empty string.

        :param section: The section which contains the property that has changed
        :type section: str

        :param key: The property key
        :type key: str
        """
        pass
