"""
This module contains the code completion mode and the related classes.
"""
import weakref
from pcef.core import constants
from pcef.core.editor import QCodeEdit
from pcef.core.mode import Mode
from pcef.core.system import DelayJobRunner
from pcef.qt import QtGui, QtCore


class Completion(QtCore.QObject):
    """
    Defines a code completion. A code suggestion is made up of the following
    elements:
        - the suggestion text
        - the suggestion icon. Optional.
        - the suggestion tooltip. Optional.
    """

    def __init__(self, text, icon=None, tooltip=None):
        QtCore.QObject.__init__(self)
        #: Displayed text.
        self.text = text
        #: QIcon used for the decoration role.
        self.icon = icon
        # optional description
        self.tooltip = tooltip

    def __repr__(self):
        return self.text


class CompletionProvider(object):
    """
    Base class for code completion providers.

    Subclasses must implement the run method to return a list of completions.
    """

    def __init__(self, priority=0):
        self.priority = priority

    def run(self, document, filePath, fileEncoding):
        """
        Provides a list of possible code completions. Must be implemented by
        subclasses

        :param document: QTextDocument
        :param filePath: Document file path
        :param fileEncoding: Document file encoding.

        :return: A list of Completion
        """
        raise NotImplementedError()


class CodeCompletionMode(Mode, QtCore.QObject):
    IDENTIFIER = "codeCompletionMode"
    DESCRIPTION = "Provides a code completion/suggestion system"

    completionsReady = QtCore.Signal(object)

    @property
    def completionPrefix(self):
        prefix = self.editor.selectWordUnderCursor().selectedText()
        if prefix == "":
            prefix = self.editor.selectWordUnderCursor(
                selectWholeWord=True).selectedText()
        return prefix

    def __init__(self):
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__currentCompletion = ""
        self.__triggerKey = None
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=700)
        self.__providers = []

    def addCompletionProvider(self, provider):
        self.__providers.append(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.priority,
            reverse=True)

    def removeCompletionProvider(self, provider):
        self.__providers.remove(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.priority,
            reverse=True)

    def requestCompletion(self):
        self.__jobRunner.requestJob(self.__collectCompletions, True,
                                    self.editor.document().clone(),
                                    self.editor.filePath,
                                    self.editor.fileEncoding)

    def __collectCompletions(self, doc, filePath, fileEncoding):
        completions = []
        for completionProvider in self.__providers:
            completions += completionProvider.run(doc, filePath, fileEncoding)
        self.completionsReady.emit(completions)

    def _onInstall(self, editor):
        Mode._onInstall(self, editor)
        self.__triggerKey = self.editor.settings.addProperty(
            "codeCompletionTriggerKey", QtCore.Qt.Key_Space)
        self.__triggerLength = self.editor.settings.addProperty(
            "codeCompletionTriggerLength", 1)
        self.__completer = QtGui.QCompleter(["titi", "tata", "toto",
                                             "qzdd", "ijqzoijd", "k,qdkl,dqz",
                                             "k,qzdkld,z", "lqkzdmlzd"], editor)
        self.__completer.setCompletionMode(self.__completer.PopupCompletion)
        self.__completer.activated.connect(self.__insertCompletion)
        self.__completer.highlighted.connect(self.__onCompletionChanged)

    def _onUninstall(self):
        self.__completer = None

    def _onStateChanged(self, state):
        if state:
            self.editor.focusedIn.connect(self._onFocusIn)
            self.editor.keyPressed.connect(self.__onKeyPressed)
            self.editor.postKeyPressed.connect(self.__onKeyReleased)
            self.completionsReady.connect(self.__applyResults)
        else:
            self.editor.focusedIn.disconnect(self._onFocusIn)
            self.editor.keyPressed.disconnect(self.__onKeyPressed)
            self.editor.postKeyPressed.disconnect(self.__onKeyReleased)
            self.completionsReady.disconnect(self.__applyResults)

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
            prefixLen = len(self.completionPrefix)
            if prefixLen >= self.__triggerLength:
                self.requestCompletion()

    def __isPrintableKeyEvent(self, event):
        try:
            ch = chr(event.key())
        except ValueError:
            return False
        else:
            return True

    def __onCompletionChanged(self, completion):
        self.__currentCompletion = completion

    def __applyResults(self, completions):
        pass

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
            self.__insertCompletion(self.__currentCompletion)
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

    def __showPopup(self):
        # set prefix
        self.__completer.setCompletionPrefix(self.completionPrefix)
        # compute size and pos
        cr = self.editor.cursorRect()
        cr.setWidth(400)
        charWidth = self.editor.fontMetrics().width('A')
        prefixLen = (len(self.completionPrefix) * charWidth)
        cr.setX(cr.x() + self.editor.marginSize() - prefixLen)
        # show the completion list
        self.__completer.complete(cr)

    def __insertCompletion(self, completion):
        print("completion")
        tc = self.editor.selectWordUnderCursor(selectWholeWord=True)
        tc.insertText(completion)
        self.editor.setTextCursor(tc)


class DocumentWordCompletionProvider(CompletionProvider):
    """
    Provides code completions using the document words.
    """

    def __init__(self, editor):
        CompletionProvider.__init__(self)
        assert isinstance(editor, QCodeEdit)
        self.settings = weakref.ref(editor.settings)

    @staticmethod
    def split(doc, seps):
        """
        Splits a text in a meaningful list of words.

        :param txt: Text to split

        :param seps: List of words separators

        :return: A set of words found in the document (excluding punctuations,
        numbers, ...)
        """
        print(sorted(seps))
        default_sep = seps[0]
        txt = doc.toPlainText()
        for sep in seps[1:]:
            if sep:
                txt = txt.replace(sep, default_sep)
        words = txt.split(default_sep)
        for w in words:
            w.strip()
            if w == '':
                words.remove(w)
            if len(w) == 1:
                words.remove(w)
            try:
                int(w)
                words.remove(w)
            except ValueError:
                pass
        words = set(words)
        try:
            words.remove("")
        except KeyError:
            pass
        return sorted(words)

    def run(self, document, filePath, fileEncoding):
        retVal = []
        assert isinstance(document, QtGui.QTextDocument)
        settings = self.settings()
        separators = constants.WORD_SEPARATORS
        if settings:
            separators = settings.value("wordSeparators")
        # print(document.toPlainText())
        words = self.split(document, separators)
        for w in words:
            retVal.append(Completion(w))
        return retVal


if __name__ == '__main__':
    from pcef.core import QCodeEdit, constants

    class Example(QCodeEdit):

        def __init__(self):
            QCodeEdit.__init__(self, parent=None)
            self.openFile(__file__)
            self.resize(QtCore.QSize(1000, 600))
            self.installMode(CodeCompletionMode())
            self.codeCompletionMode.addCompletionProvider(
                DocumentWordCompletionProvider(self))

    import sys
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    print(DocumentWordCompletionProvider.split(e.document(),
                                               constants.WORD_SEPARATORS))
    sys.exit(app.exec_())
