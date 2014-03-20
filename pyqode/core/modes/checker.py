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
This module contains the checker mode, a base class for code checker modes.
"""
from PyQt4 import QtCore, QtGui
from pyqode.core.api import client

from pyqode.core.editor import Mode
from pyqode.core.api.system import DelayJobRunner
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.constants import CheckerMessages
from pyqode.core.api.constants import CheckerTriggers
from pyqode.core.panels.marker import Marker


class CheckerMessage(object):
    """
    Holds data for a message displayed by the :class:`pyqode.core.CheckerMode`.
    """
    #: Default set of icons foreach message status
    ICONS = {CheckerMessages.INFO: ("marker-info",
                                    ":/pyqode-icons/rc/dialog-info.png"),
             CheckerMessages.WARNING: ("marker-warning",
                                       ":/pyqode-icons/rc/dialog-warning.png"),
             CheckerMessages.ERROR: ("marker-error",
                                     ":/pyqode-icons/rc/dialog-error.png")}

    #: Default colors foreach message status
    COLORS = {CheckerMessages.INFO: "#4040DD",
              CheckerMessages.WARNING: "#DDDD40",
              CheckerMessages.ERROR: "#DD4040"}

    @classmethod
    def status_to_string(cls, status):
        """
        Converts a message status to a string.
        :param status: Status to convert (pyqode.core.MSG_STATUS_XXX)

        :return: The status string.
        :rtype: str
        """
        strings = {CheckerMessages.INFO: "Info",
                   CheckerMessages.WARNING: "Warning",
                   CheckerMessages.ERROR: "Error"}
        return strings[status]

    @property
    def status_string(self):
        """
        Returns the message status as a string.

        :return: The status string.
        """
        return self.status_to_string(self.status)

    def __init__(self, description, status, line, col=None, icon=None,
                 color=None):
        """
        :param description: The message description (used as a tooltip)
        :param status: The status associated with the message.
        :param line: The message line number
        :param col: The message start column (at the moment the message ends at
                    the end of the line).
        :param icon: Icon used for the marker panel
        :param color: Text decoration color
        """
        assert 0 <= status <= 2
        #: The description of the message, used as a tooltip.
        self.description = description
        #: The status associated with the message. One of:
        #:    * :const:`pyqode.core.MSG_STATUS_INFO`
        #:    * :const:`pyqode.core.MSG_STATUS_WARNING`
        #:    * :const:`pyqode.core.MSG_STATUS_ERROR`
        self.status = status
        #: The line of the message
        self.line = line
        #: The start column (used for the text decoration). If the col is None,
        #: the whole line is highlighted.
        self.col = col
        #: The color used for the text decoration. If None, the default color
        #: is used (:const:`pyqode.core.CheckerMessage.COLORS`)
        self.color = color
        if self.color is None:
            self.color = self.COLORS[status]
        #: The icon used for the marker panel. If None, the default icon is
        #: used (:const:`pyqode.core.CheckerMessage.ICONS`)
        self.icon = icon
        if self.icon is None:
            self.icon = self.ICONS[status]
        self.marker = None
        self.decoration = None

    def __repr__(self):
        return "{0} {1}".format(self.description, self.line)


class CheckerMode(Mode, QtCore.QObject):
    """
    Performs a user defined code analysis job in a background process and
    display the results on the editor instance.

    The user defined code analysis job is a simple **function** with the
    following signature:

    .. code-block:: python

        def analysisProcess(queue: multiprocessing.Queue, code: str, path:
        str, encoding: str):

    You use the queue to put the list of :class:`pyqode.core.CheckerMessage`
    that you want to be displayed.

    The background process is ran when the text changed and the user is idle
    for a specific delay or when the text is saved depending on the trigger
    (see :const:`pyqode.core.CHECK_TRIGGER_TXT_CHANGED` or
    :const:`pyqode.core.CHECK_TRIGGER_TXT_SAVED`). You can also request an
    analysis manually using :meth:`pyqode.core.CheckerMode.requestAnalysis`

    The messages are displayed as text decorations on the editor and optional
    markers can be added to a :class:`pyqode.core.MarkerPanel`
    """
    def __init__(self, worker,
                 delay=500,
                 marker_panel_id="markerPanel",
                 clear_on_request=True, trigger=CheckerTriggers.TXT_CHANGED,
                 show_tooltip=False):
        """
        :param worker: The process function or class to call remotely.
        :param delay: The delay used before running the analysis process when
                      trigger is set to
                      :const:pyqode.core.CHECK_TRIGGER_TXT_CHANGED`
        :param marker_panel_id: Identifier of the marker panel to use to add
                              checker messages markers.
        :param clear_on_request: Clear all markers on request. If set to False,
                            the marker will be cleared only when the analysis
                            jobs finished. Default is True
        :param trigger: The kind of trigger. (see
                        :const:`pyqode.core.CHECK_TRIGGER_TXT_CHANGED` or
                        :const:`pyqode.core.CHECK_TRIGGER_TXT_SAVED`)
        :param show_tooltip: Specify if a tooltip must be displayed when the
                             mouse is over a checker message decoration.
        """
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__jobRunner = DelayJobRunner(self, nb_threads_max=1, delay=delay)
        self.__messages = []
        self._worker = worker
        self.__trigger = trigger
        self.__mutex = QtCore.QMutex()
        self.__clearOnRequest = clear_on_request
        self.__showTooltip = show_tooltip
        self.__markerPanelId = marker_panel_id

    def add_messages(self, messages, clear=True):
        """
        Adds one message or a list of message.

        :param messages: A list of messages or a single message
        :param clear: Clear messages before displaying the new ones.
                      Default is True.

        .. warning:: This function will be renamed to **addMessages** for the
                     next release (this is planned for 1.1).
        """
        if clear:
            self.clear_messages()
        if isinstance(messages, CheckerMessage):
            messages = [messages]
        nb_msg = len(messages)
        if nb_msg > 20:
            nb_msg = 20
        for message in messages[0:nb_msg]:
            self.__messages.append(message)
            if message.line:
                if hasattr(self.editor, self.__markerPanelId):
                    message.marker = Marker(message.line, message.icon,
                                            message.description)
                    self.editor.markerPanel.add_marker(message.marker)
                tooltip = None
                if self.__showTooltip:
                    tooltip = message.description
                message.decoration = TextDecoration(self.editor.textCursor(),
                                                    start_line=message.line,
                                                    tooltip=tooltip,
                                                    draw_order=3)
                message.decoration.set_full_width(True)
                message.decoration.set_as_error(color=QtGui.QColor(
                    message.color))
                self.editor.add_decoration(message.decoration)
        if hasattr(self.editor, "markerPanel"):
            self.editor.markerPanel.repaint()

    def remove_message(self, message):
        """
        Removes a message.

        :param message: Message to remove
        """
        self.__messages.remove(message)
        if message.marker:
            self.editor.markerPanel.remove_marker(message.marker)
        if message.decoration:
            self.editor.remove_decoration(message.decoration)

    def clear_messages(self):
        """
        Clears all messages.
        """
        while len(self.__messages):
            self.remove_message(self.__messages[0])
        if hasattr(self.editor, "markerPanel"):
            self.editor.markerPanel.repaint()

    def _on_state_changed(self, state):
        if state:
            if self.__trigger == CheckerTriggers.TXT_CHANGED:
                self.editor.textChanged.connect(self.request_checking)
            elif self.__trigger == CheckerTriggers.TXT_SAVED:
                self.editor.text_saved.connect(self.request_checking)
                self.editor.new_text_set.connect(self.request_checking)
        else:
            if self.__trigger == CheckerTriggers.TXT_CHANGED:
                self.editor.textChanged.disconnect(self.request_checking)
            elif self.__trigger == CheckerTriggers.TXT_SAVED:
                self.editor.text_saved.disconnect(self.request_checking)
                self.editor.new_text_set.disconnect(self.request_checking)

    def _on_work_finished(self, status, messages):
        if status:
            messages = [CheckerMessage(*msg) for msg in messages]
            self.add_messages(messages)

    def request_checking(self):
        """ Requests a checking of the editor content. """
        if self.__clearOnRequest:
            self.clear_messages()
        request_data = {
            'code': self.editor.toPlainText(),
            'path': self.editor.file_path,
            'encoding': self.editor.file_encoding
        }
        try:
            self.editor.request_work(self._worker, request_data,
                                     on_receive=self._on_work_finished)
        except client.NotConnectedError:
            QtCore.QTimer.singleShot(2000, self.request_checking)
