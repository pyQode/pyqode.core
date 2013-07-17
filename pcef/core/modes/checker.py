"""
This module contains the checker mode, a base class for code checker modes.
"""
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


class Message(object):
    """
    A message associates a description with a status and few other information
    such as line and column number, custom icon (to override the status icon).

    A message will be displayed in the editor's marker panel and/or as a
    TextDecoration (if status is error or warning).
    """
    ICONS = {MSG_STATUS_INFO: ("dialog-info",
                               ":/pcef-icons/rc/dialog-info.png"),
             MSG_STATUS_WARNING: ("dialog-warning",
                                  ":/pcef-icons/rc/dialog-warning.png"),
             MSG_STATUS_ERROR: ("dialog-error",
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


class Checker(Mode):
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

    addMessageRequested = QtCore.Signal(Message)
    clearMessagesRequested = QtCore.Signal()

    def __init__(self, clearOnRequest=True):
        Mode.__init__(self)
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=2, delay=1200)
        self.__messages = []
        self.__mutex = QtCore.QMutex()
        self.__clearOnRequest = clearOnRequest

    def addMessage(self, message):
        """
        Adds a message.

        .. warning: Do not use this method from the run method, use
                    addMessageRequested signal instead.

        :param message: Message to add
        """
        self.__messages.append(message)
        if message.line:
            message._marker = Marker(message.line, message.icon,
                                     message.description)
            self.editor.markerPanel.addMarker(message._marker)
            message._decoration = TextDecoration(self.editor.textCursor(),
                                                 startLine=message.line,
                                                 tooltip=message.description,
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

    def onStateChanged(self, state):
        if state:
            self.editor.textChanged.connect(self.requestAnalysis)
            self.addMessageRequested.connect(self.addMessage)
            self.clearMessagesRequested.connect(self.clearMessages)
        else:
            self.editor.textChanged.disconnect(self.requestAnalysis)
            self.addMessageRequested.disconnect(self.addMessage)
            self.clearMessagesRequested.disconnect(self.clearMessages)

    def run(self, document, filePath):
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
                                    self.editor.document().clone(),
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

    class FancyChecker(Checker):
        """
        Example checker. Clear messages and add a message of each status on a
        randome line.
        """
        IDENTIFIER = "fancyChecker"
        DESCRIPTION = "An example checker, does not actually do anything usefull"

        def run(self, document, filePath):
            self.clearMessagesRequested.emit()
            msg = Message("A fancy info message", MSG_STATUS_INFO,
                          random.randint(1, self.editor.lineCount()))
            self.addMessageRequested.emit(msg)
            msg = Message("A fancy warning message", MSG_STATUS_WARNING,
                          random.randint(1, self.editor.lineCount()))
            self.addMessageRequested.emit(msg)
            msg = Message("A fancy error message", MSG_STATUS_ERROR,
                          random.randint(1, self.editor.lineCount()))
            self.addMessageRequested.emit(msg)

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