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
This modules provides a series of services for the user to customize editor
style and settings.

The name service is used here to denote the global aspect of the functionality
provided.

The main purpose of this module is to provide a coherent and homogeneous style
and settings for all PCEF instances. It provides way to change the global
style and global settings for the code editor.

"""
from pcef.config.styles import DefaultWhiteStyle
from pcef.config.styles import DefaultDarkStyle


class StyleChangedSignal(object):
    """
    Style changed signal
    """

    def __init__(self):
        self.slots = set()

    def connect(self, slot):
        """Connect a slot to the wrapped qt signal
        :param slot: the slot to connect (method or function)
        """
        self.slots.add(slot)

    def disconnect(self, slot):
        """ Disconnects a slot from the wrapped qt signal """
        self.slots.remove(slot)

    def emit(self, *args):
        """ Emits the wrapped qt signal """
        for slot in self.slots:
            slot.__call__(*args)

    def clear(self):
        self.slots.clear()


#: Signal emitted when the style is changed by the changeGlobalStyle function
__styleChanged = StyleChangedSignal()


#: Global style variable
__globalStyle = DefaultWhiteStyle()


def connectToStyleChanged(slot):
    """
    Connect a slot to the __styleChanged signal.
    :param slot: Slot to connect to the signal
    """
    global __styleChanged
    __styleChanged.connect(slot)


def changeGlobalStyle(style):
    """
    Changes the global style and emit the __styleChanged signal.

    :param style: The new style instance that will be shared by all
    editor/panel/modes instances who have the inheritGlobalStyle set to True.
    """
    global __globalStyle, __styleChanged
    __globalStyle = style
    __styleChanged.emit()


def getGlobalStyle():
    """
    Returns the current style instance
    :return: Style
    """
    return __globalStyle


class StyledObject(object):
    """Provides styling functionality:
        - define a style property
        - define an abstract method to warn subclasses when the style changed
          and to force them to update themselves
        - automatically connects to the global style changed signal
        - provides a way to use a custom style instead.
    """

    def __init__(self):
        global __styleChanged
        self._style = getGlobalStyle()
        self._inheritsGlobalStyle = True
        connectToStyleChanged(self.onStyleChanged)

    def setCustomStyle(self, useCustom,  style=None):
        """
        Shortcut for settings a custom style or resetting the global style.
        :param useCustom: True to set a custom style. False to reset the global
        style
        :param style: Custom style to set.
        """
        if not useCustom:
            self.currentStyle = getGlobalStyle()
        else:
            assert style is not None, "Custom style cannot be None"
            self.currentStyle= style
        self._inheritsGlobalStyle = not useCustom

    def __get_style(self):
        return self._style

    def __set_style(self, style):
        self._style = style
        self.updateStyling()

    #: Current style instance
    currentStyle = property(__get_style, __set_style)

    def __get_inheritsGlobalStyle(self):
        return self._inheritsGlobalStyle

    def __set_inheritsGlobalStyle(self, inherits):
        self._inheritsGlobalStyle = inherits

    #: Set this property to False to setup a custom style.
    inheritsGlobalStyle = property(__get_inheritsGlobalStyle,
                                   __set_inheritsGlobalStyle)

    def onStyleChanged(self):
        if self.inheritsGlobalStyle:
            self.currentStyle = getGlobalStyle()

    def updateStyling(self):
        """
        Raises not ImplementError.
        Subclasses must overrides this method to update themselves whenever the
        style changed
        :return:
        """
        raise NotImplementedError
