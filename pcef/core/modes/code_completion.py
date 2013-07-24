"""
This module contains the code completion mode and the related classes.
"""
from pcef.core.mode import Mode
from pcef.qt import QtGui, QtCore


class CodeCompletionMode(Mode):
    IDENTIFIER = "codeCompletionMode"
    DESCRIPTION = "Provides a code completion/suggestion system"

    def __init__(self):
        Mode.__init__(self)
        self.__currentCompletion = ""
        self.__triggerKey = None

    def requestCompletion(self):
        self.showPopup()

    def _onInstall(self, editor):
        Mode._onInstall(self, editor)
        self.__triggerKey = self.editor.settings.addProperty(
            "codeCompletionTriggerKey", QtCore.Qt.Key_Space)
        self.__completer = QtGui.QCompleter(["titi", "tata", "toto",
                                             "qzdd", "ijqzoijd", "k,qdkl,dqz",
                                             "k,qzdkld,z", "lqkzdmlzd"], editor)
        self.__completer .setCompletionMode(self.__completer.PopupCompletion)
        self.__completer.activated.connect(self.insertCompletion)
        self.__completer.highlighted.connect(self.__onCompletionChanged)

    def _onUninstall(self):
        self.__completer = None

    def _onStateChanged(self, state):
        if state:
            self.editor.focusedIn.connect(self._onFocusIn)
            self.editor.keyPressed.connect(self.__onKeyPressed)
            self.editor.postKeyPressed.connect(self.__onKeyReleased)
        else:
            self.editor.focusedIn.disconnect(self._onFocusIn)
            self.editor.keyPressed.disconnect(self.__onKeyPressed)
            self.editor.postKeyPressed.disconnect(self.__onKeyReleased)

    def __isShortcut(self, event):
        """
        Checks if the event's key and modifiers make the completion shortcut
        (Ctrl+M)

        :param event: QKeyEvent

        :return: bool
        """
        val = int(event.modifiers() & QtCore.Qt.ControlModifier)
        return val and event.key() == self.__triggerKey

    def __handleCompleterEvents(self, event):
        # complete
        if (event.key() == QtCore.Qt.Key_Enter or
                event.key() == QtCore.Qt.Key_Return):
            self.insertCompletion(self.__currentCompletion)
            self.__completer.popup().hide()
            event.accept()
            return True
        # hide
        elif (event.key() == QtCore.Qt.Key_Escape or
                event.key() == QtCore.Qt.Key_Backtab):
            self.__completer.popup().hide()
            event.accept()
            return True
        return False

    def _onFocusIn(self, event):
        """
        Resets completer widget

        :param event: QFocusEvents
        """
        self.__completer.setWidget(self.editor)

    def __onKeyPressed(self, event):
        isShortcut = self.__isShortcut(event)
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            self.__handleCompleterEvents(event)
        elif isShortcut:
            self.requestCompletion()
            event.accept()

    def __onKeyReleased(self, event):
        isPrintable = self.__isPrintableKeyEvent(event)
        isShortcut = self.__isShortcut(event)
        if event.key() == QtCore.Qt.Key_Delete:
            print("Del")
        if self.__completer.popup().isVisible():
            # Update completion prefix
            self.__completer.setCompletionPrefix(self.completionPrefix)
            cnt = self.__completer.completionCount()
            if not cnt or not self.completionPrefix:
                self.__completer.popup().hide()
            else:
                self.__completer.popup().setCurrentIndex(
                    self.__completer.completionModel().index(0, 0))
        elif isPrintable:
            # try to detect auto trigger:
            #  1: symbols such as ".", "->"
            #  2: word lenght
            print("detect auto triggers")
            pass

    def __isPrintableKeyEvent(self, event):
        try:
            ch = chr(event.key())
        except ValueError:
            return False
        else:
            return True

    def __onCompletionChanged(self, completion):
        self.__currentCompletion = completion

    @property
    def completionPrefix(self):
        prefix = self.editor.selectWordUnderCursor().selectedText()
        if prefix == "":
            prefix = self.editor.selectWordUnderCursor(
                selectWholeWord=True).selectedText()
        return prefix

    def showPopup(self):
        cr = self.editor.cursorRect()
        cr.setWidth(400)
        charWidth = self.editor.fontMetrics().width('A')
        prefixLen = (len(self.editor.selectWordUnderCursor().selectedText()) *
                     charWidth)
        cr.setX(cr.x() + self.editor.marginSize() - prefixLen)
        print(cr)
        self.__completer.complete(cr)  # popup it up!

    def insertCompletion(self, completion):
        print("completion")
        tc = self.editor.selectWordUnderCursor(selectWholeWord=True)
        tc.insertText(completion)
        self.editor.setTextCursor(tc)
