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
This module contains the code completion mode and the related classes.
"""
import re
import sys
import os
from pyqode.core import constants
from pyqode.core.editor import QCodeEdit
from pyqode.core.mode import Mode
from pyqode.core.system import DelayJobRunner, SubprocessServer, memoized
from pyqode.qt import QtGui, QtCore
from pyqode.core import logger


class PreLoadWorker(object):
    """
    A worker object that will run the preload method on all completion provider
    in the child process.
    """

    def __init__(self, providers, *args):
        """
        :param providers: The list of completion providers

        :param args: The preload method arguments
        """
        self.__providers = providers
        self.__args = args

    def __call__(self, *args, **kwargs):
        """
        Do the work (this will be called in the child process by the
        SubprocessServer).
        """
        results = []
        for prov in self.__providers:
            # pass the process dict to every providers
            setattr(prov, "processDict", self.processDict)
            r = prov.preload(*self.__args)
            if r:
                results.append(r)
        return results


class CompletionWorker(object):
    """
    A worker object that will run the complete method of every providers
    """
    def __init__(self, providers, *args):
        self.__providers = providers
        self.__args = args

    def __call__(self, *args, **kwargs):
        """
        Do the work (this will be called in the child process by the
        SubprocessServer).
        """
        completions = []
        for prov in self.__providers:
            # pass the process dict to every providers
            setattr(prov, "processDict", self.processDict)
            completions.append(prov.complete(*self.__args))
            if len(completions) > 20:
                break
        return completions


class Completion(object):
    """
    Defines a code completion item.

    A completion is made up of the following elements:
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
                    this method.

    .. note: As the provider is executed in a child process, your class instance
             will loose its data every time its run. To store persistent data
             (such as the preload results), you may use the 'processDict'
             attribute. Care must be taken from the key, we suggest a
             combination of the file path and type(self).__name__.

    """
    PRIORITY = 0

    def preload(self, code, fileEncoding, filePath):
        return None

    def complete(self, code, line, column, completionPrefix,
                 filePath, encodign):
        """
        :param code: code string
        :param line: line number (1 based)
        :param column: colum number (0 based)
        :param completionPrefix: The prefix to complete
        :param filePath: file path of the code to complete
        :param fileEncoding: encoding of the code to complete
        """
        raise NotImplementedError()


class CodeCompletionMode(Mode, QtCore.QObject):
    """
    This mode provides code completion system wich is extensible. It takes care
    of running the completion request in a background process using one or more
    completion provider(s).

    To implement a code completion for a specific language, you only need to
    implement new :class:`pyqode.core.CompletionProvider`

    The completion pop is shown the user press **ctrl+space** or automatically
    while the user is typing some code (this can be configured using a series
    of properties described in the below table).

    The code completion mode adds the following properties to
    :attr:`pyqode.core.QCodeEdit.settings`

    ====================== ====================== ======= ====================== ================
    Key                    Section                Type    Default value          Description
    ====================== ====================== ======= ====================== ================
    triggerKey             Code completion        int     QtCore.Qt.Key_Space    The key that triggers the code completion requests(ctrl + **space**)
    triggerLength          Code completion        int     1                      The number of character needed to trigger automatic completion requests.
    triggerSymbols         Code completion        list    ["."]                  The list of symbols that trigger code completion requests(".", "->", ...)
    showTooltips           Code completion        bool    True                   Show completion tooltip (e.g. to display the underlying type)
    caseSensitive          Code completion        bool    False                  Case sensitivity (True is case sensitive)
    ====================== ====================== ======= ====================== ================

    .. note:: The code completion mode automatically starts a unique subprocess
              (:attr:`pyqode.core.CodeCompletionMode.SERVER`)
              to run code completion tasks. This process is automatically closed
              when the application is about to quit. You can use this process
              to run custom task on the completion process (e.g. setting up some :py:attr:`sys.modules`).
    """
    #: Mode identifier
    IDENTIFIER = "codeCompletionMode"
    #: Mode description
    DESCRIPTION = "Provides a code completion/suggestion system"

    #: Code completion server running in a background process and shared among
    #: all instances. Automatically started the first time a completion mode is
    #: installed on an editor widget and stopped when the app is about to quit.
    SERVER = None

    completionsReady = QtCore.Signal(object)
    waitCursorRequested = QtCore.Signal()

    #: Signal emitted when the preload operation has started.
    preLoadStarted = QtCore.Signal()
    #: Signal emitted when the preload operation has completed.
    preLoadCompleted = QtCore.Signal()

    @property
    def triggerKey(self):
        return self.editor.style.value("triggerKey", section="Code completion")

    @triggerKey.setter
    def triggerKey(self, value):
        self.editor.style.setValue("triggerKey", value, section="Code Completion")

    @property
    def triggerLength(self):
        return self.editor.style.value("triggerLength", section="Code completion")

    @triggerLength.setter
    def triggerLength(self, value):
        self.editor.style.setValue("triggerLength", value, section="Code completion")

    @property
    def triggerSymbols(self):
        return self.editor.style.value("triggerSymbols", section="Code completion")

    @triggerSymbols.setter
    def triggerSymbols(self, value):
        self.editor.style.setValue("triggerSymbols", value, section="Code completion")

    @property
    def showTooltips(self):
        return self.editor.style.value("showTooltips", section="Code completion")

    @showTooltips.setter
    def showTooltips(self, value):
        self.editor.style.setValue("showTooltips", value, section="Code completion")

    @property
    def caseSensitive(self):
        return self.editor.style.value("caseSensitive", section="Code completion")

    @caseSensitive.setter
    def caseSensitive(self, value):
        self.editor.style.setValue("caseSensitive", value, section="Code completion")

    @property
    def completionPrefix(self):
        """
        Returns the current completion prefix
        """
        prefix = self.editor.selectWordUnderCursor().selectedText()
        if prefix == "":
            try:
                prefix = self.editor.selectWordUnderCursor(
                    selectWholeWord=True).selectedText()[0]
            except IndexError:
                pass
        return prefix.strip()

    def __init__(self, server_port=5000):
        """
        :param server_port: Local TCP/IP port to use to start the code
                            completion server process
        """
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.__currentCompletion = ""
        self.__triggerKey = None
        # use to display a waiting cursor if completion provider takes too much
        # time
        self.__jobRunner = DelayJobRunner(self, nbThreadsMax=1, delay=1000)
        self.__providers = []
        self.__tooltips = {}
        self.__cursorLine = -1
        self.__cancelNext = False
        self.__preloadFinished = False
        self.__requestCnt = 0
        self.__lastCompletionPrefix = ""
        self._server_port = server_port
        self.waitCursorRequested.connect(self.__setWaitCursor)

    def addCompletionProvider(self, provider):
        """
        Adds a completion provider to the list of providers used to provide
        code completion to the user.

        Note that the provider instance will be pickled to be sent to the
        subprocess, this means that you cannot store data to keep results from
        run to run. Instead you may use
        :attr:`pyqode.core.CompletionProvider.processDict` which is a regular
        dict attribute that is set on every provider object when run in the
        subprocess.

        :param provider: The completion provider instance to add.
        """
        self.__providers.append(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.PRIORITY,
            reverse=True)

    def removeCompletionProvider(self, provider):
        """
        Removes a completion provider.

        :param provider: Provider instance to remove
        :return:
        """
        self.__providers.remove(provider)
        self.__providers = sorted(
            self.__providers, key=lambda provider: provider.PRIORITY,
            reverse=True)

    def requestCompletion(self):
        """
        Requests a code completion at the current cursor position.
        """
        if not self.__preloadFinished or self.__requestCnt:
            return
        # only check first byte
        state = self.editor.textCursor().block().userState()
        if state > 0:
            state &= 0x0F
        if state >= 1:
            return
        self.__requestCnt += 1
        self.__collectCompletions(
            self.editor.toPlainText(), self.editor.cursorPosition[0],
            self.editor.cursorPosition[1], self.completionPrefix,
            self.editor.filePath, self.editor.fileEncoding)

    def requestPreload(self):
        """
        Requests a preload of the document.
        """
        self.__preloadFinished = False
        code = self.editor.toPlainText()
        self.__preload(code, self.editor.filePath, self.editor.fileEncoding)

    @classmethod
    def startCompletionServer(cls, port=5000):
        """
        Starts the code completion server. This is automatically called the
        first time a code completion mode is isntalled on a QCodeEdit instance
        but you can call it manually before if you need it.

        :return The code completion server if created.
        :rtype pyqode.core.SubprocessServer or None
        """
        if not "PYQODE_NO_COMPLETION_SERVER" in os.environ:
            if CodeCompletionMode.SERVER is None:
                s = SubprocessServer()
                if s.start(port):
                    cls.SERVER = s
                    return s
        return None

    def _onInstall(self, editor):
        CodeCompletionMode.startCompletionServer(self._server_port)
        if CodeCompletionMode.SERVER:
            CodeCompletionMode.SERVER.signals.workCompleted.connect(
                self.__onWorkFinished)
        self.__completer = QtGui.QCompleter([""], editor)
        self.__completer.setCompletionMode(self.__completer.PopupCompletion)
        self.__completer.activated.connect(self.__insertCompletion)
        self.__completer.highlighted.connect(self.__onCompletionChanged)
        self.__completer.setModel(QtGui.QStandardItemModel())
        Mode._onInstall(self, editor)
        self.editor.settings.addProperty(
            "triggerKey", int(QtCore.Qt.Key_Space), section="Code completion")
        self.__triggerLength = self.editor.settings.addProperty(
            "triggerLength", 1, section="Code completion")
        self.editor.settings.addProperty(
            "triggerSymbols", ["."], section="Code completion")
        # todo to removed, replaced by trigger symbols
        self.editor.settings.addProperty(
            "triggerKeys", [int(QtCore.Qt.Key_Period)],
            section="Code completion")
        self.editor.settings.addProperty("showTooltips", True,
                                         section="Code completion")
        self.editor.settings.addProperty("caseSensitive", False,
                                         section="Code completion")

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
            logger.debug("Completion request finished")
            self.editor.setCursor(QtCore.Qt.IBeamCursor)
            all_results = []
            for res in results:
                all_results += res
            self.__requestCnt -= 1
            self.__showCompletions(all_results)
        elif caller_id == id(self) and isinstance(worker, PreLoadWorker):
            logger.debug("Preload request finished")
            self.__preloadFinished = True
            self.preLoadCompleted.emit()

    def __onKeyPressed(self, event):
        QtGui.QToolTip.hideText()
        isShortcut = self.__isShortcut(event)
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            self.__handleCompleterEvents(event)
            if isShortcut:
                event.accept()
        if isShortcut:
            self.requestCompletion()
            event.accept()

    def __isNavigationKey(self, event):
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
        return navigationKey

    def __isEndOfWordChar(self, event, isPrintable, symbols):
        isEndOfWordChar = False
        if isPrintable and symbols:
            k = event.text()
            seps = constants.WORD_SEPARATORS
            isEndOfWordChar = (k in seps and not k in symbols)
        return isEndOfWordChar

    def __onKeyReleased(self, event):
        if self.__isShortcut(event):
            return
        isPrintable = self.__isPrintableKeyEvent(event)
        navigationKey = self.__isNavigationKey(event)
        symbols = self.editor.settings.value(
            "triggerSymbols", section="Code completion")
        isEndOfWordChar = self.__isEndOfWordChar(event, isPrintable, symbols)
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
        # text triggers
        if isPrintable:
            if event.text() == " ":
                self.__cancelNext = bool(self.__requestCnt)
            else:
                # trigger symbols
                if symbols:
                    tc = self.editor.selectWordUnderCursor()
                    tc.setPosition(tc.position())
                    tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
                    textToCursor = tc.selectedText()
                    for symbol in symbols:
                        if textToCursor.endswith(symbol):
                            logger.debug("CC: Symbols trigger")
                            self.__hidePopup()
                            self.requestCompletion()
                            return
                # trigger length
                if not self.__completer.popup().isVisible():
                    prefixLen = len(self.completionPrefix)
                    if prefixLen == self.editor.settings.value(
                            "triggerLength", section="Code completion"):
                        logger.debug("CC: Len trigger")
                        self.requestCompletion()
                        return
            if self.completionPrefix == "":
                return self.__hidePopup()

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
        self.editor.setCursor(QtCore.Qt.WaitCursor)

    def __isLastCharEndOfWord(self):
        try:
            tc = self.editor.selectWordUnderCursor()
            tc.setPosition(tc.position())
            tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
            l = tc.selectedText()
            lastChar = l[len(l) - 1]
            if lastChar != ' ':
                symbols = self.editor.settings.value(
                    "triggerSymbols", section="Code completion")
                seps = constants.WORD_SEPARATORS
                return lastChar in seps and not lastChar in symbols
            return False
        except IndexError:
            return False
        except TypeError:
            return False  # no symbols

    def __showCompletions(self, completions):
        self.__jobRunner.cancelRequests()
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
        self._updateCompletionModel(completions,
                                    self.__completer.model())
        self.__showPopup()
        # self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)

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
        # self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)
        self.__completer.popup().hide()
        self.__jobRunner.cancelRequests()
        QtGui.QToolTip.hideText()

    def __showPopup(self):
        cnt = self.__completer.completionCount()
        fullPrefix = self.editor.selectWordUnderCursor(
            selectWholeWord=True).selectedText()
        if (fullPrefix == self.__currentCompletion) and cnt == 1:
            self.__hidePopup()
        else:
            if self.editor.settings.value("caseSensitive",
                                          section="Code completion"):
                self.__completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
            else:
                self.__completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            # set prefix
            self.__completer.setCompletionPrefix(self.completionPrefix)
            # compute size and pos
            cr = self.editor.cursorRect()
            charWidth = self.editor.fontMetrics().width('A')
            prefixLen = (len(self.completionPrefix) * charWidth)
            cr.translate(self.editor.marginSize() - prefixLen,
                         self.editor.marginSize(0))
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
            "triggerKey", section="Code completion"))
        return val and event.key() == triggerKey

    @staticmethod
    def strip_control_characters(input):
        if input:
            # unicode invalid characters
            if sys.version_info[0] == 2:
                try:
                    RE_ILLEGAL = eval("""u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                                 u'|' + \
                                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                                 (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))""")
                except SyntaxError:
                    pass # This is horrible, I know but this is the only way I found to fool this damn python 3.2 interpreter wich hates u"..."
            else:
                RE_ILLEGAL = '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                             '|' + \
                             '([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                             (chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                              chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                              chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff))
            input = re.sub(RE_ILLEGAL, "", input)
            # ascii control characters
            input = re.sub(r"[\x01-\x1F\x7F]", "", input)
        return input

    @staticmethod
    def __isPrintableKeyEvent(event):
        return len(CodeCompletionMode.strip_control_characters(
            event.text())) == 1

    @staticmethod
    @memoized
    def __makeIcon(icon):
        return QtGui.QIcon(icon)

    def _updateCompletionModel(self, completions, cc_model):
        """
        Creates a QStandardModel that holds the suggestion from the completion
        models for the QCompleter

        :param completionPrefix:
        """
        # build the completion model
        cc_model.clear()
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
                                          section="Code completion"):
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

    def __collectCompletions(self, *args):
        logger.debug("Completion requested")
        self.__jobRunner.requestJob(self.__setWaitCursor, False)
        worker = CompletionWorker(self.__providers, *args)
        CodeCompletionMode.SERVER.requestWork(self, worker)

    def __preload(self, *args):
        self.preLoadStarted.emit()
        worker = PreLoadWorker(self.__providers, *args)
        CodeCompletionMode.SERVER.requestWork(self, worker)


class DocumentWordCompletionProvider(CompletionProvider):
    """
    Provides code completions using the document words.
    """

    def __init__(self):
        CompletionProvider.__init__(self)

    def preload(self, code, filePath, fileEncoding):
        return self.parse(code, filePath=filePath)

    def parse(self, code, wordSeparators=constants.WORD_SEPARATORS,
              filePath=""):
        """
        Returns a list of completions based on the code passed as a parameter.

        :param code: The code to parse/tokenize
        :param wordSeparators: The list of words separators.
        :param filePath:
        :return: A list of :class:`pyqode.core.Completion`
        :rtype: list
        """
        completions = []
        for w in self.split(code, wordSeparators):
            completions.append(Completion(w))
        # store results in the subprocess dict for later use
        self.processDict["docWords%s-%s" %
                         (filePath, type(self).__name__)] = completions
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
        # get previous result from the server process dict
        try:
            words = self.processDict["docWords%s-%s"
                                     % (filePath, type(self).__name__)]
        except KeyError:
            words = None
        if not words or not len(words):
            return self.parse(code, filePath=filePath)
        return words


if __name__ == '__main__':

    class Example(QCodeEdit):

        def __init__(self):
            QCodeEdit.__init__(self, parent=None)
            self.resize(QtCore.QSize(1000, 600))
            self.installMode(CodeCompletionMode())
            self.codeCompletionMode.addCompletionProvider(
                DocumentWordCompletionProvider())
            self.openFile(__file__)

    import sys
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    e = Example()
    e.show()
    sys.exit(app.exec_())
