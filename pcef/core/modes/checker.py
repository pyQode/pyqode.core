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
This module contains the checker mode, a base class for code checker modes.
"""
import logging
from pcef.core.mode import Mode
from pcef.core.system import DelayJobRunner
from pcef.core.panels.marker import Marker
from pcef.core.decoration import TextDecoration
from pcef.qt import QtCore, QtGui


#: Status value for an information message
MSG_STATUS_INFO = 0
#: Status value for a warning message
MSG_STATUS_WARNING = 1
#: Status value for an error message
MSG_STATUS_ERROR = 2

#: Check is triggered when text has changed
CHECK_TRIGGER_TXT_CHANGED = 0
#: Check is triggered when text has been saved.
CHECK_TRIGGER_TXT_SAVED = 1


class CheckerMessage(object):
    """
    A message associates a description with a status and few other information
    such as line and column number, custom icon (to override the status icon).

    A message will be displayed in the editor's marker panel and/or as a
    TextDecoration (if status is error or warning).
    """
    ICONS = {MSG_STATUS_INFO: ("marker-info",
                               ":/pcef-icons/rc/dialog-info.png"),
             MSG_STATUS_WARNING: ("marker-warning",
                                  ":/pcef-icons/rc/dialog-warning.png"),
             MSG_STATUS_ERROR: ("marker-error",
                                ":/pcef-icons/rc/dialog-error.png")}

    COLORS = {MSG_STATUS_INFO: "#4040DD",
              MSG_STATUS_WARNING: "#DDDD40",
              MSG_STATUS_ERROR: "#DD4040"}

    def __init__(self, description, status, line, col=None, icon=None,
                 color=None):
        """
        :param description: The message description (used as a tooltip)
        :param status:
        :param line:
        :param col:
        :param icon:
        :param color:
        """
        # QtCore.QObject.__init__(self)
        assert 0 <= status <= 2
        self.description = description
        self.status = status
        self.line = line
        self.col = col
        self.color = color
        if self.color is None:
            self.color = self.COLORS[status]
        self.icon = icon
        if self.icon is None:
            self.icon = self.ICONS[status]
        self._marker = None
        self._decoration = None


class CheckerMode(Mode, QtCore.QObject):
    """
    This mode is an abstract base class for code checker modes.

    The checker will run an analysis job (in a background thread when the
    editor's text changed and will take care of displaying messages emitted by
    the addMessageRequested.

    To create a concrete checker you must override the run method and use the
    addMessageRequested signal to add messages to the ui from the background
    thread.

    The run method will receive a clone of the editor's text document and the
    current file path.
    """

    addMessagesRequested = QtCore.Signal(object, bool)
    clearMessagesRequested = QtCore.Signal()

    def __init__(self, clearOnRequest=True, trigger=CHECK_TRIGGER_TXT_CHANGED,
                 showEditorTooltip=False):
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=1500)
        self.__messages = []
        self.__trigger = trigger
        self.__mutex = QtCore.QMutex()
        self.__clearOnRequest = clearOnRequest
        self.__showTooltip = showEditorTooltip

    def addMessage(self, messages, clear=False):
        """
        Adds a message.

        .. warning: Do not use this method from the run method, use
                    addMessageRequested signal instead.

        :param messages: A list of messages or a single message
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
                if hasattr(self.editor, "markerPanel"):
                    message._marker = Marker(message.line, message.icon,
                                             message.description)
                    self.editor.markerPanel.addMarker(message._marker)
                tooltip = None
                if self.__showTooltip:
                    tooltip = message.description
                message._decoration = TextDecoration(self.editor.textCursor(),
                                                     startLine=message.line,
                                                     tooltip=tooltip,
                                                     draw_order=3)
                message._decoration.setFullWidth(True)
                message._decoration.setError(color=QtGui.QColor(message.color))
                self.editor.addDecoration(message._decoration)

    def removeMessage(self, message):
        """
        Remove the message

        :param message: Message to remove
        """
        self.__messages.remove(message)
        if message._marker:
            self.editor.markerPanel.removeMarker(message._marker)
        if message._decoration:
            self.editor.removeDecoration(message._decoration)

    def clearMessages(self):
        """
        Clears all messages.

        .. warning: Do not use this method from the run method, use
                    clearMessagesRequested signal instead.
        """
        while len(self.__messages):
            self.removeMessage(self.__messages[0])

    def _onStateChanged(self, state):
        if state:
            if self.__trigger == CHECK_TRIGGER_TXT_CHANGED:
                self.editor.textChanged.connect(self.requestAnalysis)
            elif self.__trigger == CHECK_TRIGGER_TXT_SAVED:
                self.editor.textSaved.connect(self.requestAnalysis)
            self.addMessagesRequested.connect(self.addMessage)
            self.clearMessagesRequested.connect(self.clearMessages)
        else:
            if self.__trigger == CHECK_TRIGGER_TXT_CHANGED:
                self.editor.textChanged.disconnect(self.requestAnalysis)
            elif self.__trigger == CHECK_TRIGGER_TXT_SAVED:
                self.editor.textSaved.disconnect(self.requestAnalysis)
            self.addMessagesRequested.disconnect(self.addMessage)
            self.clearMessagesRequested.disconnect(self.clearMessages)

    def run(self, code, filePath):
        """
        Abstract method that is ran from a background thread. Override this
        method to implement a concrete checker.

        :param document: Clone of the QTextDocument (thread safe)

        :param filePath: The current file path.
        """
        raise NotImplementedError()

    def requestAnalysis(self):
        """ Request an analysis job. """
        if self.__clearOnRequest:
            self.clearMessages()
        self.__jobRunner.requestJob(self.run, True,
                                    self.editor.toPlainText(),
                                    self.editor.filePath)


if __name__ == "__main__":
    import sys
    import random
    from pcef.core import QGenericCodeEdit, MarkerPanel

    try:
        import faulthandler
        faulthandler.enable()
    except ImportError:
        pass

    class FancyChecker(CheckerMode):
        """
        Example checker. Clear messages and add a message of each status on a
        randome line.
        """
        IDENTIFIER = "fancyChecker"
        DESCRIPTION = "An example checker, does not actually do anything " \
                      "usefull"

        def run(self, document, filePath):
            self.clearMessagesRequested.emit()
            msg = CheckerMessage(
                "A fancy info message", MSG_STATUS_INFO,
                random.randint(1, self.editor.lineCount()))
            self.addMessagesRequested.emit(msg)
            msg = CheckerMessage(
                "A fancy warning message", MSG_STATUS_WARNING,
                random.randint(1, self.editor.lineCount()))
            self.addMessagesRequested.emit(msg)
            msg = CheckerMessage(
                "A fancy error message", MSG_STATUS_ERROR,
                random.randint(1, self.editor.lineCount()))
            self.addMessagesRequested.emit(msg)

    def main():
        app = QtGui.QApplication(sys.argv)
        win = QtGui.QMainWindow()
        edit = QGenericCodeEdit()
        win.setCentralWidget(edit)
        edit.installMode(FancyChecker(trigger=CHECK_TRIGGER_TXT_CHANGED))
        edit.installPanel(MarkerPanel())
        edit.openFile(__file__)
        win.show()
        app.exec_()

    sys.exit(main())
