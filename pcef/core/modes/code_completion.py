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
This module contains the code completion mode and the related classes.
"""
import logging
from pcef.core import constants
from pcef.core.editor import QCodeEdit
from pcef.core.mode import Mode
from pcef.core.system import DelayJobRunner, SubprocessServer, memoized
from pcef.qt import QtGui, QtCore


class PreLoadWorker(object):
    """
    A worker object that will run the preload method on all completion provider
    in the child process.
    """

    def __init__(self, providers, previous_results, *args):
        """
        :param providers: The list of completion providers

        :param previous_results: The list of previous results foreach provider

        :param args: The preload method arguments
        """
        self.__providers = providers
        self.__old_res = previous_results
        self.__args = args

    def __call__(self):
        """
        Do the work (this will be called in the child process by the
        SubprocessServer).
        """
        results = []
        for prov in self.__providers:
            r = prov.preload(*self.__args)
            results.append(r)
        return results


class CompletionWorker(object):
    """
    A worker object that will run the complete method of
    """
    def __init__(self, providers, old_res, *args):
        self.__providers = providers
        self.__old_res = old_res
        self.__args = args

    def __call__(self, *args, **kwargs):
        """
        Do the work (this will be called in the child process by the
        SubprocessServer).
        """
        completions = []
        if self.__old_res:
            for prov, old_results in zip(self.__providers, self.__old_res):
                if len(old_results) > 1:
                    prov.previousResults = old_results
                results = prov.complete(*self.__args)
                completions.append(results)
                if len(results) > 20:
                    break
        else:
            for prov in self.__providers:
                completions.append(prov.complete(*self.__args))
        return completions


class Completion(object):
    """
    Defines a code completion. A code suggestion is made up of the following
    elements:
        - the suggestion text
        - the suggestion icon. Optional.
        - the suggestion tooltip. Optional.
    """

    def __init__(self, text, icon=None, tooltip=None):
        #: Displayed text.
        self.text = text.strip()
        #: filename/resource name of the icon used for the decoration role
        self.icon = icon
        # optional description
        self.tooltip = tooltip

    def isNull(self):
        return self.text == ""

    def __repr__(self):
        return self.text


class CompletionProvider(object):
    """
    Base class for code completion providers, objects that scan some code and
    return a list of Completion objects.

    There are two methods to override:
        - preload: preload the list of Completions when a new text is set on the
                   editor. Optional.
        - complete: complete the current text. All subclasses needs to implement
                    this method. Provides that use preload can just return
                    self.previousResults
    """
    PRIORITY = 0

    def __init__(self):
        self.previousResults = None

    def preload(self, code, fileEncoding, filePath):
        return [Completion("")]

    def complete(self, code, line, column, completionPrefix, filePath, fileEncoding):
        """
        Provides a list of possible code completions.

        :param document: QTextDocument
        :param filePath: Document file path
        :param fileEncoding: Document file encoding.

        :return: A list of Completion
        """
        raise NotImplementedError()


class CodeCompletionMode(Mode, QtCore.QObject):
    IDENTIFIER = "codeCompletionMode"
    DESCRIPTION = "Provides a code completion/suggestion system"

    SERVER = None

    completionsReady = QtCore.Signal(object)
    waitCursorRequested = QtCore.Signal()

    preLoadStarted = QtCore.Signal()
    preLoadCompleted = QtCore.Signal()

    @property
    def completionPrefix(self):
        prefix = self.editor.selectWordUnderCursor().selectedText()
        if prefix == "":
            try:
                prefix = self.editor.selectWordUnderCursor(
                    selectWholeWord=True).selectedText()[0]
            except IndexError:
                pass
        return prefix

    def __init__(self):
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__currentCompletion = ""
        self.__triggerKey = None
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=500)
        self.__providers = []
        self.__tooltips = {}
        self.__cursorLine = -1
        self.__cancelNext = False
        self.__previous_results = None
        self.__preloadFinished = False
        self.waitCursorRequested.connect(self.__setWaitCursor)

    def addCompletionProvider(self, provider):
        self.__providers.append(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.PRIORITY,
            reverse=True)

    def removeCompletionProvider(self, provider):
        self.__providers.remove(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.PRIORITY,
            reverse=True)

    def requestCompletion(self, immediate=False):
        if not self.__preloadFinished:
            return
        print("request")
        code = self.editor.toPlainText()
        if not immediate:
            self.__jobRunner.requestJob(
                self.__collectCompletions, False, self.__previous_results,
                code, self.editor.cursorPosition[0], self.editor.cursorPosition[1],
                self.completionPrefix, self.editor.filePath,
                self.editor.fileEncoding)
        else:
            self.__jobRunner.cancelRequests()
            self.__collectCompletions(self.__previous_results,
                code, self.editor.cursorPosition[0],
                self.editor.cursorPosition[1], self.completionPrefix,
                self.editor.filePath, self.editor.fileEncoding)

    def requestPreload(self):
        self.__preloadFinished = False
        code = self.editor.toPlainText()
        self.__jobRunner.requestJob(
            self.__preload, False, self.__previous_results,
            code, self.editor.filePath, self.editor.fileEncoding)

    def _onInstall(self, editor):
        if CodeCompletionMode.SERVER is None:
            s = SubprocessServer()
            s.start()
            CodeCompletionMode.SERVER = s
        s.signals.workCompleted.connect(self.__onWorkFinished)
        self.__completer = QtGui.QCompleter([""], editor)
        self.__completer.setCompletionMode(self.__completer.PopupCompletion)
        self.__completer.activated.connect(self.__insertCompletion)
        self.__completer.highlighted.connect(self.__onCompletionChanged)
        Mode._onInstall(self, editor)
        self.editor.settings.addProperty(
            "triggerKey", int(QtCore.Qt.Key_Space), section="codeCompletion")
        self.__triggerLength = self.editor.settings.addProperty(
            "triggerLength", 1, section="codeCompletion")
        self.editor.settings.addProperty(
            "triggerSymbols", ["."], section="codeCompletion")
        self.editor.settings.addProperty("showTooltips", True,
                                         section="codeCompletion")
        self.editor.settings.addProperty("caseSensitive", False,
                                         section="codeCompletion")
        self.editor.settings.addProperty("useThreads", True,
                                         section="codeCompletion")

    def _onUninstall(self):
        self.__completer = None

    def _onStateChanged(self, state):
        if state:
            self.editor.focusedIn.connect(self.__onFocusIn)
            self.editor.keyPressed.connect(self.__onKeyPressed)
            self.editor.postKeyPressed.connect(self.__onKeyReleased)
            self.completionsReady.connect(self.__showCompletions)
            self.__completer.highlighted.connect(
                self.__displayCompletionTooltip)
            self.editor.cursorPositionChanged.connect(
                self.__onCursorPositionChanged)
            self.editor.newTextSet.connect(self.requestPreload)
        else:
            self.editor.focusedIn.disconnect(self.__onFocusIn)
            self.editor.keyPressed.disconnect(self.__onKeyPressed)
            self.editor.postKeyPressed.disconnect(self.__onKeyReleased)
            self.completionsReady.disconnect(self.__showCompletions)
            self.__completer.highlighted.disconnect(
                self.__displayCompletionTooltip)
            self.editor.cursorPositionChanged.disconnect(
                self.__onCursorPositionChanged)
            self.editor.newTextSet.disconnect(self.requestPreload)

    def __onFocusIn(self, event):
        """
        Resets completer widget

        :param event: QFocusEvents
        """
        self.__completer.setWidget(self.editor)

    def __onWorkFinished(self, caller_id, worker, results):
        if caller_id == id(self) and isinstance(worker, CompletionWorker):
            all = []
            for res in results:
                all += res
            self.completionsReady.emit(all)
            self.__previous_results = results
        elif caller_id == id(self) and isinstance(worker, PreLoadWorker):
            self.__previous_results = results
            self.__preloadFinished = True
            self.preLoadCompleted.emit()

    def __onKeyPressed(self, event):
        QtGui.QToolTip.hideText()
        isShortcut = self.__isShortcut(event)
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            self.__handleCompleterEvents(event)
        elif isShortcut:
            self.requestCompletion(immediate=True)
            event.accept()

    def __onKeyReleased(self, event):
        if self.__isShortcut(event):
            return
        isPrintable = self.__isPrintableKeyEvent(event)
        navigationKey = (event.key() == QtCore.Qt.Key_Backspace or
                         event.key() == QtCore.Qt.Key_Back or
                         event.key() == QtCore.Qt.Key_Delete or
                         event.key() == QtCore.Qt.Key_Left or
                         event.key() == QtCore.Qt.Key_Right or
                         event.key() == QtCore.Qt.Key_Up or
                         event.key() == QtCore.Qt.Key_Down or
                         event.key() == QtCore.Qt.Key_Space or
                         event.key() == QtCore.Qt.Key_End or
                         event.key() == QtCore.Qt.Key_Home)
        symbols = self.editor.settings.value(
            "triggerSymbols", section="codeCompletion")
        isEndOfWordChar = False
        if isPrintable:
            k = str(chr(event.key()))
            seps = self.editor.settings.value("wordSeparators")
            isEndOfWordChar = (k in seps and
                               not str(chr(event.key())) in symbols)
        if self.__completer.popup().isVisible():
            # Update completion prefix
            self.__completer.setCompletionPrefix(self.completionPrefix)
            cnt = self.__completer.completionCount()
            if (not cnt or
                    (self.completionPrefix == "" and navigationKey) or
                    isEndOfWordChar or
                    (int(event.modifiers()) and
                     event.key() == QtCore.Qt.Key_Backspace)):
                self.__hidePopup()
            else:
                self.__showPopup()
        else:
            if not navigationKey and int(event.modifiers()) == 0:
                # detect auto trigger symbols symbols such as ".", "->"
                tc = self.editor.selectWordUnderCursor()
                tc.setPosition(tc.position())
                tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
                textToCursor = tc.selectedText()
                for symbol in symbols:
                    if textToCursor.endswith(symbol):
                        logging.getLogger("pcef-cc").debug("Symbols trigger")
                        self.requestCompletion(immediate=False)
                        return
            if isPrintable:
                prefixLen = len(self.completionPrefix)
                if prefixLen >= self.editor.settings.value(
                        "triggerLength", section="codeCompletion"):
                    logging.getLogger("pcef-cc").debug("Len trigger")
                    self.requestCompletion()

    def __onCompletionChanged(self, completion):
        self.__currentCompletion = completion

    def __onCursorPositionChanged(self):
        cl = self.editor.cursorPosition[0]
        if cl != self.__cursorLine:
            self.__cursorLine = cl
            self.__hidePopup()
            self.__jobRunner.cancelRequests()
            self.__jobRunner.stopJob()

    @QtCore.Slot()
    def __setWaitCursor(self):
        self.editor.viewport().setCursor(QtCore.Qt.WaitCursor)

    def __isLastCharEndOfWord(self):
        try:
            tc = self.editor.selectWordUnderCursor()
            tc.setPosition(tc.position())
            tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
            l = tc.selectedText()
            lastChar = l[len(l) - 1]
            if lastChar != ' ':
                symbols = self.editor.settings.value(
                    "triggerSymbols", section="codeCompletion")
                seps = self.editor.settings.value("wordSeparators")
                return lastChar in seps and not lastChar in symbols
            return False
        except IndexError:
            return False

    def __showCompletions(self, completions):
        # user typed too fast: end of word char has been inserted
        if self.__isLastCharEndOfWord():
            return
        # user typed too fast: the user already typed the only suggestion we
        # have
        elif (len(completions) == 1 and
              completions[0].text == self.completionPrefix):
            return
        # a request cancel has been set
        if self.__cancelNext:
            self.__cancelNext = False
            return
        # we can show the completer
        self.__completer.setModel(self.__createCompleterModel(completions))
        self.__showPopup()
        self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)

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

    def __hidePopup(self):
        self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)
        self.__completer.popup().hide()
        self.__jobRunner.cancelRequests()
        if self.__jobRunner.jobRunning:
            self.__cancelNext = True
        QtGui.QToolTip.hideText()

    def __showPopup(self):
        cnt = self.__completer.completionCount()
        fullPrefix = self.editor.selectWordUnderCursor(
            selectWholeWord=True).selectedText()
        if (fullPrefix == self.__currentCompletion) and cnt == 1:
            self.__hidePopup()
        else:
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

    def __isShortcut(self, event):
        """
        Checks if the event's key and modifiers make the completion shortcut
        (Ctrl+M)

        :param event: QKeyEvent

        :return: bool
        """
        val = int(event.modifiers() & QtCore.Qt.ControlModifier)
        triggerKey = int(self.editor.settings.value(
            "triggerKey", section="codeCompletion"))
        return val and event.key() == triggerKey

    def __isPrintableKeyEvent(self, event):
        try:
            ch = chr(event.key())
        except ValueError:
            return False
        else:
            return int(event.modifiers()) == 0

    @memoized
    def __makeIcon(self, icon):
        return QtGui.QIcon(icon)

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
            if completion.isNull():
                continue
            # skip redundant completion
            if completion.text != self.completionPrefix and \
                    not completion.text in displayedTexts:
                displayedTexts.append(completion.text)
                item = QtGui.QStandardItem()
                item.setData(completion.text, QtCore.Qt.DisplayRole)
                if completion.tooltip is not None:
                    self.__tooltips[completion.text] = completion.tooltip
                if completion.icon is not None:
                    item.setData(self.__makeIcon(completion.icon),
                                 QtCore.Qt.DecorationRole)
                cc_model.appendRow(item)
        return cc_model

    def __displayCompletionTooltip(self, completion):
        if not self.editor.settings.value("showTooltips",
                                          section="codeCompletion"):
            return
        if not completion in self.__tooltips:
            QtGui.QToolTip.hideText()
            return
        tooltip = self.__tooltips[completion].strip()
        if tooltip:
            pos = self.__completer.popup().pos()
            pos.setX(pos.x() + self.__completer.popup().size().width())
            pos.setY(pos.y() - 15)
            QtGui.QToolTip.showText(pos, tooltip, self.editor)
        else:
            QtGui.QToolTip.hideText()

    def __collectCompletions(self, previous_results, *args):
        worker = CompletionWorker(self.__providers, previous_results, *args)
        CodeCompletionMode.SERVER.requestWork(self, worker)
        # completions will be displayed when the finished signal is triggered

    def __preload(self, previous_results, *args):
        self.preLoadStarted.emit()
        worker = PreLoadWorker(self.__providers, previous_results, *args)
        CodeCompletionMode.SERVER.requestWork(self, worker)


class DocumentWordCompletionProvider(CompletionProvider):
    """
    Provides code completions using the document words.
    """

    def __init__(self):
        CompletionProvider.__init__(self)

    def preload(self, code, fileEncoding, filePath):
        return self.parse(code)

    def parse(self, code, wordSeparators=constants.WORD_SEPARATORS):
        completions = []
        for w in self.split(code, wordSeparators):
            completions.append(Completion(w))
        return completions

    @staticmethod
    def split(txt, seps):
        """
        Splits a text in a meaningful list of words.

        :param txt: Text to split

        :param seps: List of words separators

        :return: A set of words found in the document (excluding punctuations,
        numbers, ...)
        """
        # replace all possible separators with a default sep
        default_sep = seps[0]
        for sep in seps[1:]:
            if sep:
                txt = txt.replace(sep, default_sep)
        # now we can split using the default_sep
        raw_words = txt.split(default_sep)
        words = set()
        for w in raw_words:
            # w = w.strip()
            if w.isalpha():
                words.add(w)
        return sorted(words)

    def complete(self, code, line, column, completionPrefix,
                 filePath, fileEncoding):
        if not self.previousResults:
            return self.parse(code)
        else:
            return self.previousResults


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
