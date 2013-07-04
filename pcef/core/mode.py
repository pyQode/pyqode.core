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
This module contains the definition of the Mode class
"""
import weakref


class Mode(object):
    """
    Base class for editor extension/mode. An extension is a "thing" that can be
    installed on the QCodeEdit to add new behaviours.

    An extension is added to a QCodeEdit by using the addMode or addPanel
    methods.

    Subclasses must/should override the following methods:
        - onStateChanged: to connect/disconnect to/from the code edit signals
        - onStyleChanged: to refresh ui colors (mainly used by panels)
    """
    IDENTIFIER = ""
    DESCRIPTION = ""

    @property
    def editor(self):
        """
        Provides easy access to the CodeEditorWidget weakref

        :rtype: pcef.QCodeEdit
        """
        if self.__editor is not None:
            return self.__editor()
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
            self.onStateChanged(enabled)

    def __init__(self):
        """
        Creates the extension.

        :param name: Mode name (used as an identifier)

        :param description: A description of the extension
        """
        #: Mode name
        self.name = self.IDENTIFIER
        #: Mode description
        self.description = self.DESCRIPTION
        #: Mode enables state (subclasses must implement onStateChanged to
        #  disconnect their slots to disable any actions)
        self.__enabled = False
        #: Editor instance
        self.__editor = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def install(self, editor):
        """
        Installs the extension on the editor.

        .. warning::
            For internal use only.

        .. warning::
            Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pcef.QCodeEdit
        """
        self.__editor = weakref.ref(editor)
        self.enabled = True
        editor.style.valueChanged.connect(self.onStyleChanged)

    def uninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self.__editor = None

    def onStateChanged(self, state):
        """
        Called when the enable state changed.

        .. warning: Raises NotImplementedError. Subclasses must override this
                    method to disconnect their slots.

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        raise NotImplementedError()

    def onStyleChanged(self, section, key, value):
        """
        Automatically called when a style property changed
        """
        pass