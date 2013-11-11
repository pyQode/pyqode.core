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
This module contains the checker mode, a base class for code checker modes.
"""
import os
import multiprocessing
from pyqode.core import logger
from pyqode.core.mode import Mode
from pyqode.core.system import DelayJobRunner
from pyqode.core.panels.marker import Marker
from pyqode.core.decoration import TextDecoration
from pyqode.qt import QtCore, QtGui


#: Status value for an information message.
MSG_STATUS_INFO = 0
#: Status value for a warning message.
MSG_STATUS_WARNING = 1
#: Status value for an error message.
MSG_STATUS_ERROR = 2

#: Check is triggered when text has changed.
CHECK_TRIGGER_TXT_CHANGED = 0
#: Check is triggered when text has been saved.
CHECK_TRIGGER_TXT_SAVED = 1


class CheckerMessage(object):
    """
    Holds data for a message displayed by the :class:`pyqode.core.CheckerMode`.
    """
    #: Default set of icons foreach message status
    ICONS = {MSG_STATUS_INFO: ("marker-info",
                               ":/pyqode-icons/rc/dialog-info.png"),
             MSG_STATUS_WARNING: ("marker-warning",
                                  ":/pyqode-icons/rc/dialog-warning.png"),
             MSG_STATUS_ERROR: ("marker-error",
                                ":/pyqode-icons/rc/dialog-error.png")}

    #: Default colors foreach message status
    COLORS = {MSG_STATUS_INFO: "#4040DD",
              MSG_STATUS_WARNING: "#DDDD40",
              MSG_STATUS_ERROR: "#DD4040"}

    @classmethod
    def statusToString(cls, status):
        """
        Converts a message status to a string.
        :param status: Status to convert (pyqode.core.MSG_STATUS_XXX)

        :return: The status string.
        :rtype: str
        """
        strings = {MSG_STATUS_INFO: "Info", MSG_STATUS_WARNING: "Warning",
                   MSG_STATUS_ERROR: "Error"}
        return strings[status]

    @property
    def statusString(self):
        """
        Returns the message status as a string.

        :return: The status string.
        """
        return self.statusToString(self.status)

    def __init__(self, description, status, line, col=None, icon=None,
                 color=None, filename=None):
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
        #: The color used for the text decoration. If None, the default color is
        #: used (:const:`pyqode.core.CheckerMessage.COLORS`)
        self.color = color
        if self.color is None:
            self.color = self.COLORS[status]
        #: The icon used for the marker panel. If None, the default icon is used
        #: (:const:`pyqode.core.CheckerMessage.ICONS`)
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

        def analysisProcess(queue: multiprocessing.Queue, code: str, path: str, encoding: str):

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
    #: Internal signal used to add a checker message from a background thread.
    addMessagesRequested = QtCore.Signal(object, bool)
    #: Internal signal used to clear the checker messages.
    clearMessagesRequested = QtCore.Signal()

    def __init__(self, process_func,
                 delay=500,
                 markerPanelId="markerPanel",
                 clearOnRequest=True, trigger=CHECK_TRIGGER_TXT_CHANGED,
                 showEditorTooltip=False):
        """
        :param process_func: The process function that performs the code
                             analysis.
        :param delay: The delay used before running the analysis process when
                      trigger is set to
                      :const:pyqode.core.CHECK_TRIGGER_TXT_CHANGED`
        :param markerPanelId: Identifier of the marker panel to use to add
                              checker messages markers.
        :param clearOnRequest: Clear all markers on request. If set to False,
                            the marker will be cleared only when the analysis
                            jobs finished. Default is True
        :param trigger: The kind of trigger. (see
                        :const:`pyqode.core.CHECK_TRIGGER_TXT_CHANGED` or
                        :const:`pyqode.core.CHECK_TRIGGER_TXT_SAVED`)
        :param showEditorTooltip: Specify if a tooltip must be display when the
                                  mouse is over a checker message decoration.
        """
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=delay)
        self.__messages = []
        self.__process_func = process_func
        self.__trigger = trigger
        self.__mutex = QtCore.QMutex()
        self.__clearOnRequest = clearOnRequest
        self.__showTooltip = showEditorTooltip
        self.__markerPanelId = markerPanelId

    def addMessages(self, messages, clear=True):
        """
        Adds one message or a list of message.

        :param messages: A list of messages or a single message
        :param clear: Clear messages before displaying the new ones.
                      Default is True.

        .. warning:: This function will be renamed to **addMessages** for the
                     next release (this is planned for 1.1).
        """
        if clear:
            self.clearMessages()
        if isinstance(messages, CheckerMessage):
            messages = [messages]
        nbMsg = len(messages)
        if nbMsg > 20:
            nbMsg = 20
        for message in messages[0:nbMsg]:
            self.__messages.append(message)
            if message.line:
                if hasattr(self.editor, self.__markerPanelId):
                    message.marker = Marker(message.line, message.icon,
                                             message.description)
                    self.editor.markerPanel.addMarker(message.marker)
                tooltip = None
                if self.__showTooltip:
                    tooltip = message.description
                message.decoration = TextDecoration(self.editor.textCursor(),
                                                     startLine=message.line,
                                                     tooltip=tooltip,
                                                     draw_order=3)
                message.decoration.setFullWidth(True)
                message.decoration.setError(color=QtGui.QColor(message.color))
                self.editor.addDecoration(message.decoration)
        if hasattr(self.editor, "markerPanel"):
            self.editor.markerPanel.repaint()

    def removeMessage(self, message):
        """
        Removes a message.

        :param message: Message to remove
        """
        self.__messages.remove(message)
        if message.marker:
            self.editor.markerPanel.removeMarker(message.marker)
        if message.decoration:
            self.editor.removeDecoration(message.decoration)

    def clearMessages(self):
        """
        Clears all messages.
        """
        while len(self.__messages):
            self.removeMessage(self.__messages[0])
        if hasattr(self.editor, "markerPanel"):
            self.editor.markerPanel.repaint()

    def _onStateChanged(self, state):
        if state:
            if self.__trigger == CHECK_TRIGGER_TXT_CHANGED:
                self.editor.textChanged.connect(self.requestAnalysis)
            elif self.__trigger == CHECK_TRIGGER_TXT_SAVED:
                self.editor.textSaved.connect(self.requestAnalysis)
                self.editor.newTextSet.connect(self.requestAnalysis)
            self.addMessagesRequested.connect(self.addMessages)
            self.clearMessagesRequested.connect(self.clearMessages)
        else:
            if self.__trigger == CHECK_TRIGGER_TXT_CHANGED:
                self.editor.textChanged.disconnect(self.requestAnalysis)
            elif self.__trigger == CHECK_TRIGGER_TXT_SAVED:
                self.editor.textSaved.disconnect(self.requestAnalysis)
                self.editor.newTextSet.disconnect(self.requestAnalysis)
            self.addMessagesRequested.disconnect(self.addMessages)
            self.clearMessagesRequested.disconnect(self.clearMessages)

    def __runAnalysis(self, code, filePath, fileEncoding):
        """
        Creates a subprocess. The subprocess receives a queue for storing
        results, the code string, the file path and the file encoding as
        input parameters.

        The subprocess must fill the queue with a list of
        :class:`pyqode.core.CheckerMessage`.
        """
        if "PYQODE_NO_COMPLETION_SERVER" in os.environ:
            return
        try:
            q = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=self.__process_func, name="%s process" % self.name,
                args=(q, code, filePath, fileEncoding))
            p.start()
            try:
                self.addMessagesRequested.emit(q.get(), True)
            except IOError as e:
                logger.warning("Failed to add messages: %s" % e)
            p.join()
        except OSError as e:
            logger.error("%s: failed to run analysis, %s" % (self.name, e))

    def requestAnalysis(self):
        """ Requests an analysis job. """
        if self.__clearOnRequest:
            self.clearMessages()
        self.__jobRunner.requestJob(self.__runAnalysis, True,
                                    self.editor.toPlainText(),
                                    self.editor.filePath,
                                    self.editor.fileEncoding)


if __name__ == "__main__":
    import sys
    import random
    from pyqode.core import QGenericCodeEdit, MarkerPanel

    def run(queue, code, document, filePath):
        queue.put([CheckerMessage("A fancy info message",
                                  MSG_STATUS_INFO, random.randint(1, 15)),
                   CheckerMessage("A fancy warning message",
                                  MSG_STATUS_WARNING, random.randint(1, 15)),
                   CheckerMessage("A fancy error message", MSG_STATUS_ERROR,
                                  random.randint(1, 15))])

    class FancyChecker(CheckerMode):
        """
        Example checker. Clear messages and add a message of each status on a
        randome line.
        """
        IDENTIFIER = "fancyChecker"
        DESCRIPTION = "An example checker"

        def __init__(self):
            super(FancyChecker, self).__init__(run)

    def main():
        app = QtGui.QApplication(sys.argv)
        win = QtGui.QMainWindow()
        edit = QGenericCodeEdit()
        win.setCentralWidget(edit)
        edit.installMode(FancyChecker())
        edit.installPanel(MarkerPanel())
        edit.openFile(__file__)
        win.show()
        app.exec_()

    sys.exit(main())
