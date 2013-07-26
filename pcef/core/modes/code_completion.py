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
        self.text = text.strip()
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

    def run(self, code, line, column, completionPrefix,
            filePath, fileEncoding):
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
        self.__tooltips = {}
        self.__cursorLine = -1

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

    def requestCompletion(self, immediate=False):
        code = self.editor.toPlainText()
        useThreads = self.editor.settings.value(
            "useThreads", section="codeCompletion")
        if not immediate:
            self.__jobRunner.requestJob(
                self.__collectCompletions, useThreads, code,
                self.editor.cursorPosition[0], self.editor.cursorPosition[1],
                self.completionPrefix, self.editor.filePath,
                self.editor.fileEncoding)
        else:
            self.__jobRunner.cancelRequests()
            if useThreads:
                self.__jobRunner.startJob(
                    self.__collectCompletions, False, code,
                    self.editor.cursorPosition[0],
                    self.editor.cursorPosition[1], self.completionPrefix,
                    self.editor.filePath, self.editor.fileEncoding)
            else:
                self.__collectCompletions(
                    code, self.editor.cursorPosition[0],
                    self.editor.cursorPosition[1], self.completionPrefix,
                    self.editor.filePath, self.editor.fileEncoding)

    def __collectCompletions(self, code, l, c, prefix, filePath, fileEncoding):
        print("Run", l, c)
        completions = []
        for completionProvider in self.__providers:
            completions += completionProvider.run(code, l, c, prefix,
                                                  filePath, fileEncoding)
        self.completionsReady.emit(completions)
        print("Finished", l, c)

    def _onInstall(self, editor):
        self.__completer = QtGui.QCompleter([""], editor)
        self.__completer.setCompletionMode(self.__completer.PopupCompletion)
        self.__completer.activated.connect(self.__insertCompletion)
        self.__completer.highlighted.connect(self.__onCompletionChanged)
        Mode._onInstall(self, editor)
        self.editor.settings.addProperty(
            "triggerKey", QtCore.Qt.Key_Space, section="codeCompletion")
        self.__triggerLength = self.editor.settings.addProperty(
            "triggerLength", 1, section="codeCompletion")
        self.editor.settings.addProperty(
            "triggerSymbols", ["."], section="codeCompletion")
        self.editor.settings.addProperty("showTooltips", True,
                                         section="codeCompletion")
        self.editor.settings.addProperty("caseSensitive", True,
                                         section="codeCompletion")
        self.editor.settings.addProperty("useThreads", True,
                                         section="codeCompletion")

    def _onUninstall(self):
        self.__completer = None

    def _onStateChanged(self, state):
        if state:
            self.editor.focusedIn.connect(self._onFocusIn)
            self.editor.keyPressed.connect(self.__onKeyPressed)
            self.editor.postKeyPressed.connect(self.__onKeyReleased)
            self.completionsReady.connect(self.__applyResults)
            self.__completer.highlighted.connect(
                self.__displayCompletionTooltip)
            self.editor.cursorPositionChanged.connect(
                self.__onCursorPositionChanged)
        else:
            self.editor.focusedIn.disconnect(self._onFocusIn)
            self.editor.keyPressed.disconnect(self.__onKeyPressed)
            self.editor.postKeyPressed.disconnect(self.__onKeyReleased)
            self.completionsReady.disconnect(self.__applyResults)
            self.__completer.highlighted.disconnect(
                self.__displayCompletionTooltip)
            self.editor.cursorPositionChanged.disconnect(
                self.__onCursorPositionChanged)

    def _onFocusIn(self, event):
        """
        Resets completer widget

        :param event: QFocusEvents
        """
        self.__completer.setWidget(self.editor)

    def __onKeyPressed(self, event):
        QtGui.QToolTip.hideText()
        isShortcut = self.__isShortcut(event)
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            self.__handleCompleterEvents(event)
        if isShortcut:
            self.requestCompletion(immediate=True)
            event.accept()

    def __onKeyReleased(self, event):
        # print("KR", self.editor.toPlainText())
        isPrintable = self.__isPrintableKeyEvent(event)
        isShortcut = self.__isShortcut(event)
        if self.__completer.popup().isVisible():
            # Update completion prefix
            self.__completer.setCompletionPrefix(self.completionPrefix)
            cnt = self.__completer.completionCount()
            if (not cnt or (int(event.modifiers()) and
                            event.key() == QtCore.Qt.Key_Backspace) or
                self.completionPrefix == "" and
                    (event.key() == QtCore.Qt.Key_Backspace or
                     event.key() == QtCore.Qt.Key_Delete or
                     event.key() == QtCore.Qt.Key_Left or
                     event.key() == QtCore.Qt.Key_Right or
                     event.key() == QtCore.Qt.Key_Space or
                     event.key() == QtCore.Qt.Key_End or
                     event.key() == QtCore.Qt.Key_Home)):
                self.__hidePopup()
            else:
                self.__showPopup()
        elif (isPrintable or event.key() == QtCore.Qt.Key_Delete or
              event.key() == QtCore.Qt.Key_Backspace) and not isShortcut:
            if (self.completionPrefix == "" and
                (event.key() == QtCore.Qt.Key_Backspace or
                 event.key() == QtCore.Qt.Key_Delete or
                 event.key() == QtCore.Qt.Key_Left or
                 event.key() == QtCore.Qt.Key_Right or
                 event.key() == QtCore.Qt.Key_Space or
                 event.key() == QtCore.Qt.Key_End or
                 event.key() == QtCore.Qt.Key_Home)):
                self.__hidePopup()
            else:
                prefixLen = len(self.completionPrefix)
                # detect auto trigger symbols symbols such as ".", "->"
                tc = self.editor.selectWordUnderCursor()
                tc.setPosition(tc.position())
                tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
                textToCursor = tc.selectedText()
                symbols = self.editor.settings.value(
                    "triggerSymbols", section="codeCompletion")
                for symbol in symbols:
                    if textToCursor.endswith(symbol):
                        self.requestCompletion(immediate=True)
                        return
                if prefixLen >= self.editor.settings.value(
                        "triggerLength", section="codeCompletion"):
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
        self.__completer.setModel(self.__createCompleterModel(completions))
        self.__showPopup()

    def __isShortcut(self, event):
        """
        Checks if the event's key and modifiers make the completion shortcut
        (Ctrl+M)

        :param event: QKeyEvent

        :return: bool
        """
        val = int(event.modifiers() & QtCore.Qt.ControlModifier)
        return val and event.key() == self.editor.settings.value(
            "triggerKey", section="codeCompletion")

    def __hidePopup(self):
        self.__completer.popup().hide()
        self.__jobRunner.cancelRequests()
        self.__jobRunner.stopJob()
        QtGui.QToolTip.hideText()

    def __handleCompleterEvents(self, event):
        # complete
        if (event.key() == QtCore.Qt.Key_Enter or
                event.key() == QtCore.Qt.Key_Return):
            self.__insertCompletion(self.__currentCompletion)
            self.__hidePopup()
            event.accept()
            return True
        # hide
        elif (event.key() == QtCore.Qt.Key_Escape or
                event.key() == QtCore.Qt.Key_Backtab):
            self.__hidePopup()
            event.accept()
            return True
        return False

    def __showPopup(self):
        if self.editor.settings.value("caseSensitive",
                                      section="codeCompletion"):
            self.__completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        else:
            self.__completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # set prefix
        self.__completer.setCompletionPrefix(self.completionPrefix)
        # compute size and pos
        cr = self.editor.cursorRect()
        cr.setWidth(400)
        charWidth = self.editor.fontMetrics().width('A')
        prefixLen = (len(self.completionPrefix) * charWidth)
        cr.setX(cr.x() + self.editor.marginSize() - prefixLen)
        cr.setWidth(
            self.__completer.popup().sizeHintForColumn(0) +
            self.__completer.popup().verticalScrollBar().sizeHint().width())
        # show the completion list
        self.__completer.complete(cr)
        self.__completer.popup().setCurrentIndex(
            self.__completer.completionModel().index(0, 0))

    def __insertCompletion(self, completion):
        tc = self.editor.selectWordUnderCursor(selectWholeWord=True)
        tc.insertText(completion)
        self.editor.setTextCursor(tc)

    def __createCompleterModel(self, completions):
        """
        Creates a QStandardModel that holds the suggestion from the completion
        models for the QCompleter

        :param completionPrefix:
        """
        # build the completion model
        cc_model = QtGui.QStandardItemModel()
        displayedTexts = []
        self.__tooltips.clear()
        for completion in completions:
            # skip redundant completion
            if completion.text != self.completionPrefix and \
                    not completion.text in displayedTexts:
                displayedTexts.append(completion.text)
                item = QtGui.QStandardItem()
                item.setData(completion.text, QtCore.Qt.DisplayRole)
                if completion.tooltip is not None:
                    self.__tooltips[completion.text] = completion.tooltip
                if completion.icon is not None:
                    item.setData(
                        QtGui.QIcon(completion.icon), QtCore.Qt.DecorationRole)
                cc_model.appendRow(item)
        return cc_model

    def __displayCompletionTooltip(self, completion):
        if not self.editor.settings.value("showTooltips",
                                          section="codeCompletion"):
            return
        if not completion in self.__tooltips:
            QtGui.QToolTip.hideText()
            return
        tooltip = self.__tooltips[completion]
        pos = self.__completer.popup().pos()
        pos.setX(pos.x() + self.__completer.popup().size().width())
        pos.setY(pos.y() - 15)
        QtGui.QToolTip.showText(pos, tooltip, self.editor)

    def __onCursorPositionChanged(self):
        cl = self.editor.cursorPosition[0]
        if cl != self.__cursorLine:
            self.__cursorLine = cl
            self.__hidePopup()
            self.__jobRunner.cancelRequests()
            self.__jobRunner.stopJob()


class DocumentWordCompletionProvider(CompletionProvider):
    """
    Provides code completions using the document words.
    """

    def __init__(self, editor):
        CompletionProvider.__init__(self)
        assert isinstance(editor, QCodeEdit)
        self.settings = weakref.ref(editor.settings)

    @staticmethod
    def split(txt, seps):
        """
        Splits a text in a meaningful list of words.

        :param txt: Text to split

        :param seps: List of words separators

        :return: A set of words found in the document (excluding punctuations,
        numbers, ...)
        """
        default_sep = seps[0]
        for sep in seps[1:]:
            if sep:
                txt = txt.replace(sep, default_sep)
        words = txt.split(default_sep)
        for w in words:
            w = w.strip()
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

    def run(self, code, line, column, completionPrefix,
            filePath, fileEncoding):
        retVal = []
        settings = self.settings()
        separators = constants.WORD_SEPARATORS
        if settings:
            separators = settings.value("wordSeparators")
        words = self.split(code, separators)
        for w in words:
            retVal.append(Completion(w))
        return retVal


if __name__ == '__main__':

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
    sys.exit(app.exec_())
