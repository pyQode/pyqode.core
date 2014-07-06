# -*- coding: utf-8 -*-
"""
This module contains the checker mode, a base class for code checker modes.
"""
import logging
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.mode import Mode
from pyqode.core.backend import NotConnected
from pyqode.core.managers.backend import BackendManager
from pyqode.core.api.utils import DelayJobRunner
from pyqode.core.panels import Marker, MarkerPanel
from pyqode.core.qt import QtCore, QtGui
# pylint: disable=too-many-arguments, maybe-no-member


class CheckerMessages:
    """
    Enumerates the possible checker message types.
    """
    # pylint: disable=no-init, too-few-public-methods
    #: Status value for an information message.
    INFO = 0
    #: Status value for a warning message.
    WARNING = 1
    #: Status value for an error message.
    ERROR = 2


class CheckerMessage(object):
    """
    Holds data for a message displayed by the
    :class:`pyqode.core.modes.CheckerMode`.
    """
    # pylint: disable= too-many-instance-attributes
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

        :param status: Status to convert (p yqode.core.modes.CheckerMessages)
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
        #:    * :const:`pyqode.core.modes.CheckerMessages.INFO`
        #:    * :const:`pyqode.core.modes.CheckerMessages.WARNING`
        #:    * :const:`pyqode.core.modes.CheckerMessages.ERROR`
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


def _logger(klass):
    return logging.getLogger('%s [%s]' % (__name__, klass.__name__))


class CheckerMode(Mode, QtCore.QObject):
    """
    Performs a user defined code analysis job using the backend and
    display the results on the editor instance.

    The user defined code analysis job is a simple **function** with the
    following signature:

    .. code-block:: python

        def analysisProcess(data)

    where data is the request data:

    .. code-block:: python

        request_data = {
                'code': self.editor.toPlainText(),
                'path': self.editor.file.path,
                'encoding': self.editor.file.encoding
            }

    and the return value is a tuple made up of the following elements:

        (description, status, line, [col], [icon], [color], [path])

    The background process is ran when the text changed and the ide is an idle
    state for a few seconds.

    You can also request an analysis manually using
    :meth:`pyqode.core.modes.CheckerMode.request_analysis`

    Messages are displayed as text decorations on the editor and optional
    markers can be added to a :class:`pyqode.core.panels.MarkerPanel`
    """
    def __init__(self, worker,
                 delay=500,
                 marker_panel_id="markerPanel",
                 clear_on_request=True, show_tooltip=False):
        """
        :param worker: The process function or class to call remotely.
        :param delay: The delay used before running the analysis process when
                      trigger is set to
                      :class:pyqode.core.modes.CheckerTriggers`
        :param marker_panel_id: Identifier of the marker panel to use to add
                              checker messages markers.
        :param clear_on_request: Clear all markers on request. If set to False,
                            the marker will be cleared only when the analysis
                            jobs finished. Default is True
        :param trigger: The kind of trigger. (see
                        :class:pyqode.core.modes.CheckerTriggers)
        :param show_tooltip: Specify if a tooltip must be displayed when the
                             mouse is over a checker message decoration.
        """
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        # max number of messages
        self.limit = 50
        self._job_runner = DelayJobRunner(delay=delay)
        self._messages = []
        self._worker = worker
        self._mutex = QtCore.QMutex()
        self._clear_on_request = clear_on_request
        self._show_tooltip = show_tooltip
        self._marker_panel_id = marker_panel_id

    def add_messages(self, messages, clear=True):
        """
        Adds a message or a list of message.

        :param messages: A list of messages or a single message
        :param clear: Clear messages before displaying the new ones.
                      Default is True.
        """
        if clear:
            self.clear_messages()
        self._pending_msg = messages
        # limit number of messages
        if len(self._pending_msg) > self.limit:
            _logger(self.__class__).debug(
                'too much messages (%s), keeping error messages only' %
                len(messages))
            for msg in reversed(self._pending_msg):
                if msg.status != CheckerMessages.ERROR and \
                        len(self._pending_msg) > self.limit:
                    self._pending_msg.remove(msg)
            if len(self._pending_msg) > self.limit:
                _logger(self.__class__).info(
                    'still too much messages (%s), limiting to the 50 first '
                    'messages' % len(messages))
                self._pending_msg = self._pending_msg[:self.limit]
        QtCore.QTimer.singleShot(1, self._add_batch)

    def _add_batch(self):
        marker_panel = None
        try:
            marker_panel = self.editor.panels.get(MarkerPanel)
        except KeyError:
            pass
        for i in range(10):
            if not len(self._pending_msg):
                return
            message = self._pending_msg.pop(0)
            if message.line:
                self._messages.append(message)
                if marker_panel:
                    message.marker = Marker(message.line, message.icon,
                                            message.description)
                    marker_panel.add_marker(message.marker)
                tooltip = None
                if self._show_tooltip:
                    tooltip = message.description
                message.decoration = TextDecoration(
                    self.editor.textCursor(), start_line=message.line,
                    tooltip=tooltip, draw_order=3)
                message.decoration.set_full_width(True)
                message.decoration.set_as_error(color=QtGui.QColor(
                    message.color))
                self.editor.decorations.append(message.decoration)
        QtCore.QTimer.singleShot(1, self._add_batch)

    def remove_message(self, message):
        """
        Removes a message.

        :param message: Message to remove
        """
        self._messages.remove(message)
        if message.marker:
            try:
               pnl = self.editor.panels.get(MarkerPanel)
            except KeyError:
                pass
            else:
                pnl.remove_marker(message.marker)
        if message.decoration:
            self.editor.decorations.remove(message.decoration)

    def clear_messages(self):
        """
        Clears all messages.
        """
        while len(self._messages):
            self.remove_message(self._messages[0])
        try:
            pnl = self.editor.panels.get(MarkerPanel)
        except KeyError:
            pass
        else:
            pnl.repaint()

    def on_state_changed(self, state):
        if state:
            self.editor.textChanged.connect(self.request_analysis)
        else:
            self.editor.textChanged.disconnect(self.request_analysis)

    def _on_work_finished(self, status, messages):
        """
        Display results.

        :param status: Response status
        :param messages: Response data, messages.
        """
        # pylint: disable=star-args
        if status:
            messages = [CheckerMessage(*msg) for msg in messages]
            self.add_messages(messages)
        else:
            self.clear_messages()

    def request_analysis(self):
        """
        Requests an analysis.
        """
        self._job_runner.request_job(self._request)

    def _request(self):
        """ Requests a checking of the editor content. """
        if not self.editor:
            return
        if self._clear_on_request:
            self.clear_messages()
        request_data = {
            'code': self.editor.toPlainText(),
            'path': self.editor.file.path,
            'encoding': self.editor.file.encoding
        }
        try:
            self.editor.backend.send_request(
                self._worker, request_data, on_receive=self._on_work_finished)
        except NotConnected:
            QtCore.QTimer.singleShot(100, self._request)
