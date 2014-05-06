# -*- coding: utf-8 -*-
"""
This module contains the checker mode, a base class for code checker modes.
"""
from PyQt4 import QtCore, QtGui
from pyqode.core import frontend
from pyqode.core.frontend.utils import DelayJobRunner
from pyqode.core.frontend.panels.marker import Marker, MarkerPanel


class CheckerMessages:
    #: Status value for an information message.
    INFO = 0
    #: Status value for a warning message.
    WARNING = 1
    #: Status value for an error message.
    ERROR = 2


class CheckerMessage(object):
    """
    Holds data for a message displayed by the
    :class:`pyqode.core.frontend.modes.CheckerMode`.
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
                 color=None, path=None):
        """
        :param description: The message description (used as a tooltip)
        :param status: The status associated with the message.
        :param line: The message line number
        :param col: The message start column (at the moment the message ends at
                    the end of the line).
        :param icon: Icon used for the marker panel
        :param color: Text decoration color
        :param path: file path. Optional
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
        self.path = path

    def __repr__(self):
        return "{0} {1}".format(self.description, self.line)


class CheckerMode(frontend.Mode, QtCore.QObject):
    """
    Performs a user defined code analysis job in a background process and
    display the results on the editor instance.

    The user defined code analysis job is a simple **function** with the
    following signature:

    .. code-block:: python

        def analysisProcess(queue: multiprocessing.Queue, code: str, path:
        str, encoding: str):

    You use the queue to put the list of
    :class:`pyqode.core.frontend.modes.CheckerMessage` that you want to be
    displayed.

    The background process is ran when the text changed and the user is idle
    for a specific delay or when the text is saved depending on the trigger
    (see :const:`pyqode.core.frontend.modes.CheckMessages`).

    You can also request an analysis manually using
    :meth:`pyqode.core.frontend.modes.CheckerMode.request_analysis`

    The messages are displayed as text decorations on the editor and optional
    markers can be added to a :class:`pyqode.core.frontend.panels.MarkerPanel`
    """
    def __init__(self, worker,
                 delay=500,
                 marker_panel_id="markerPanel",
                 clear_on_request=True, show_tooltip=False):
        """
        :param worker: The process function or class to call remotely.
        :param delay: The delay used before running the analysis process when
                      trigger is set to
                      :class:pyqode.core.frontend.modes.CheckerTriggers`
        :param marker_panel_id: Identifier of the marker panel to use to add
                              checker messages markers.
        :param clear_on_request: Clear all markers on request. If set to False,
                            the marker will be cleared only when the analysis
                            jobs finished. Default is True
        :param trigger: The kind of trigger. (see
                        :class:pyqode.core.frontend.modes.CheckerTriggers)
        :param show_tooltip: Specify if a tooltip must be displayed when the
                             mouse is over a checker message decoration.
        """
        frontend.Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self._job_runner = DelayJobRunner(self, nb_threads_max=1, delay=delay)
        self._messages = []
        self._worker = worker
        self._mutex = QtCore.QMutex()
        self._clear_on_request = clear_on_request
        self._show_tooltip = show_tooltip
        self._marker_panel_id = marker_panel_id

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
        marker_panel = None
        nb_msg = len(messages)
        if nb_msg > 20:
            nb_msg = 20
        for message in messages[0:nb_msg]:
            self._messages.append(message)
            if message.line:
                try:
                    marker_panel = frontend.get_panel(self.editor,
                                                      MarkerPanel)
                except KeyError:
                    pass
                else:
                    message.marker = Marker(message.line, message.icon,
                                            message.description)
                    marker_panel.add_marker(message.marker)
                tooltip = None
                if self._show_tooltip:
                    tooltip = message.description
                message.decoration = frontend.TextDecoration(
                    self.editor.textCursor(), start_line=message.line,
                    tooltip=tooltip, draw_order=3)
                message.decoration.set_full_width(True)
                message.decoration.set_as_error(color=QtGui.QColor(
                    message.color))
                frontend.add_decoration(self.editor, message.decoration)
        if marker_panel:
            marker_panel.repaint()

    def remove_message(self, message):
        """
        Removes a message.

        :param message: Message to remove
        """
        self._messages.remove(message)
        if message.marker:
            try:
                pnl = frontend.get_panel(self.editor, MarkerPanel)
            except KeyError:
                pass
            else:
                pnl.remove_marker(message.marker)
        if message.decoration:
            frontend.remove_decoration(self.editor, message.decoration)

    def clear_messages(self):
        """
        Clears all messages.
        """
        while len(self._messages):
            self.remove_message(self._messages[0])
        try:
            m = frontend.get_panel(self.editor, MarkerPanel)
        except KeyError:
            pass
        else:
            m.repaint()

    def _on_state_changed(self, state):
        if state:
            self.editor.textChanged.connect(self.request_analysis)
        else:
            self.editor.textChanged.disconnect(self.request_analysis)

    def _on_work_finished(self, status, messages):
        if status:
            messages = [CheckerMessage(*msg) for msg in messages]
            self.add_messages(messages)
        else:
            self.clear_messages()

    def request_analysis(self):
        self._job_runner.request_job(self._request, False)

    def _request(self):
        """ Requests a checking of the editor content. """
        if self._clear_on_request:
            self.clear_messages()
        request_data = {
            'code': self.editor.toPlainText(),
            'path': self.editor.file_path,
            'encoding': self.editor.file_encoding
        }
        try:
            frontend.request_work(self.editor, self._worker, request_data,
                                  on_receive=self._on_work_finished)
        except frontend.NotConnectedError:
            QtCore.QTimer.singleShot(100, self._request)
