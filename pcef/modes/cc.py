#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from collections import deque
from PySide.QtCore import Qt, Slot, QThread, Signal, QObject, QRunnable, QThreadPool, QMutex, QTimer
from PySide.QtGui import QStandardItemModel, QStandardItem, QCompleter, \
    QTextCursor, QIcon, QToolTip
import time

from pcef.core import Mode


class Suggestion(object):
    """
    Represent a suggestion in the completion list. A suggestion is made up of
    the following elements:
        - display: suggestion text (display role)
        - decoration: an optional decoration icon (decoration role)
    """
    def __init__(self, txt, icon=None, description=None):
        #: Displayed text.
        self.display = txt
        #: QIcon used for the decoration role.
        self.decoration = icon
        # optional description
        self.description = description


class CompletionModel(object):
    """
    Base class for representing a completion model.

    A completion model is a single list of suggestions associated with a priority.

    This base class can be used directly with a static list of words.
    """
    @property
    def suggestions(self):
        ret_val = self._suggestions
        return ret_val

    def __init__(self, words=None, priority=0):
        """
        Creates a basic completion model based

        :param words: A static list of words from which we build the suggestions list.

        :param priority: Model priority (default is 0)
        """
        #: Model priority
        self.priority = priority
        #: List of suggestions (accessible through the suggestions property).
        self._suggestions = []
        if words is not None:
            for word in words:
                suggestion = Suggestion(word)
                self._suggestions.append(suggestion)

    def update(self, source_code, line, col, filename, encoding):
        """
        Non-static completion model should overrides this method to update their
        suggestion list.

        This method is called by the completion mode whenever the completion prefix changed.
        """
        pass


class DocumentWordsCompletionModel(CompletionModel):
    """
    Provides suggestions based on the current document words.
    """

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
        for sep in seps[1:]:  # we skip seps[0] because that's the default separator
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
        return set(words)

    def update(self, source_code, line, col, filename, encoding):
        """
        Updates the suggestion list.

        :param source_code: document text

        :param line: current line number (starting at 1)

        :param col: current column number (starting at 0)

        :param filename: the document filename if any

        :param encoding: the document encoding if any
        """
        words = self.split(
            source_code, ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                          '+', '{', '}', '|', ':', '"', "'", "<", ">", "?", ",",
                          ".", "/", ";", '[', ']', '\\', '\n', '\t', '-', '=',
                          ' '])
        self._suggestions[:] = []
        for w in words:
            self._suggestions.append(
                Suggestion(w, ":/icons/rc/text-generic.png"))

    def __init__(self):
        super(DocumentWordsCompletionModel, self).__init__(priority=0)


class CompletionRequest(object):
    """
    Holds data need for a code completion request.
    """
    def __init__(self, source_code="", line=0, col=1, filename="", encoding="",
                 completionPrefix="", onlyAdapt=False):
        self.source_code = source_code
        self.line = line
        self.col = col
        self.filename = filename
        self.encoding = encoding
        self.completionPrefix = completionPrefix
        self.onlyAdapt = onlyAdapt


class CompletionEvent(QObject):
    signal = Signal(CompletionRequest)


class RunnableCompleter(QRunnable):

    def __init__(self, models, request):
        super(RunnableCompleter, self).__init__()
        self.event = CompletionEvent()
        self._models = models
        self._request = request

    def connect(self, handler):
        self.event.signal.connect(handler)

    def disconnect(self, handler):
        self.event.signal.disconnect(handler)

    def run(self, *args, **kwargs):
        if not self._request.onlyAdapt:
            for model in self._models:
                try:
                    # update the current model
                    model.update(
                        self._request.source_code, self._request.line,
                        self._request.col, self._request.filename,
                        self._request.encoding)
                except :
                    pass
        self.event.signal.emit(self._request)


class CodeCompletionMode(Mode):
    """
    This mode provides code completion to the CodeEdit widget.

    The list of suggestion is supplied by a CodeCompletionModel.

    Code completion may use more than one completion model. The suggestions
    list is then filled model per model by beginning by the highest priority as
    long as the number of suggestions is lower than
    :attr:`pcef.modes.code_completion.CodeCompletion.minSuggestions`.

    For example, a python editor will use a smart completion model with a high
    priority and use the DocumentWordsCompletion model as a fallback system
    when the smart model fails to provide enough suggestions.

    The mode uses a QCompleter to provides display the list of suggestions.

    Code completion is triggered using ctrl+space or when there is at least
    three characters in the word being typed.
    """
    #: Mode identifier
    IDENTIFIER = "Code completion"

    #: Mode description
    DESCRIPTION = "Provides code completion though completion models"

    def __init__(self):
        super(CodeCompletionMode, self).__init__(
            self.IDENTIFIER, self.DESCRIPTION)
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.__cached_request = None
        self.__active_thread_count = 0
        self.__updating_models = False
        self.__timer = QTimer()

        #: Defines the min number of suggestions. This is used to know we should
        #  avoid using lower priority models.
        #  If there is at least minSuggestions in the suggestions list, we won't
        #  use other completion model.
        self.minSuggestions = 50

        #: Trigger key (automatically associated with the control modifier)
        self.triggerKey = Qt.Key_Space

        #: Number of chars needed to trigger the code completion
        self.nbTriggerChars = 1

        #: Tells if the completion should be triggered automatically (when
        #  len(wordUnderCursor) > nbTriggerChars )
        #  Default is True. Turning this option off might enhance performances
        #  and usability
        self.autoTrigger = True

        #: Show/Hide current suggestion tooltip
        self.displayTooltips = True

        self.__caseSensitivity = Qt.CaseSensitive
        #: The internal QCompleter
        self.__completer = QCompleter()
        # self.__completer.activated.connect(self._insertCompletion)
        self.__completer.highlighted.connect(self._onHighlighted)
        self.__completer.activated.connect(self._insertCompletion)
        self.__prev_txt_len = 0
        #: List of completion models
        self._models = [DocumentWordsCompletionModel()]
        self.__tooltips = {}

    def __del__(self):
        self.__completer.setWidget(None)
        self.__completer = None

    def addModel(self, model):
        """
        Adds a completion model to the completion models list.

        :param model: CompletionModel to add
        """
        self._models.append(model)
        self._models = sorted(self._models, key=lambda mdl: mdl.priority,
                              reverse=True)

    def install(self, editor):
        """
        Setup the completer with the CodeEdit.

        :param editor: CodeEditorWidget instance
        """
        super(CodeCompletionMode, self).install(editor)
        self.__completer.setWidget(editor.codeEdit)
        self.__completer.setCaseSensitivity(self.__caseSensitivity)
        self.__completer.setCompletionMode(QCompleter.PopupCompletion)

    def __set_case(self, case):
        if case != self.__caseSensitivity:
            self.__caseSensitivity = case
            self.__completer.setCaseSensitivity(case)

    def __get_case(self):
        return self.__caseSensitivity

    #: The completion case sensitivity
    caseSensitivity = property(__get_case, __set_case)

    def _onStateChanged(self, state):
        """
        Enables/Disables code completion.

        :param state: True to enable, False to disable
        """
        if state:
            self.editor.codeEdit.keyPressed.connect(self._onKeyPressed)
            self.editor.codeEdit.postKeyPressed.connect(self._onKeyReleased)
            self.editor.codeEdit.focusedIn.connect(self._onFocusIn)
            self.__completer.highlighted.connect(
                self._displayHighlightedTooltip)
        else:
            self.editor.codeEdit.keyPressed.disconnect(self._onKeyPressed)
            self.editor.codeEdit.postKeyPressed.disconnect(self._onKeyReleased)
            self.editor.codeEdit.focusedIn.disconnect(self._onFocusIn)
            self.__completer.highlighted.disconnect(
                self._displayHighlightedTooltip)

    def _onFocusIn(self, event):
        """
        Resets completer widget

        :param event: QFocusEvent
        """
        self.__completer.setWidget(self.editor.codeEdit)

    def _onHighlighted(self, completion):
        """
        Remembers the current completion when the hilighted signal is emitted.

        :param completion: Current completion
        """
        self.currentCompletion = completion

    def _onKeyReleased(self, event):
        """
        Handles the key released event to adapt completer prefix, run the cc
        library if necessary or prevent completer popup when removing text.

        :param event:

        :return:
        """
        word = self._textUnderCursor()
        isShortcut = self._isShortcut(event) or event.key() == Qt.Key_Period
        tooShort = len(word) < self.nbTriggerChars
        # closes popup if completion prefix is empty and we are not removing
        # some text
        if (not self.__completer.popup().isVisible() and
                event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete) or\
                (not isShortcut and event.modifiers() == 0 and (
                word.isspace() or word == "")):
            self._hideCompletions()
            return
        # . is an auto-trigger
        if event.key() == Qt.Key_Period and self.autoTrigger:
            self._requestCompletion(completionPrefix=word, onlyAdapt=False)
            return
        # adapt completion prefix
        if self.__completer.popup().isVisible():
            self._requestCompletion(completionPrefix=word, onlyAdapt=True)
        # run cc if word is long enough and auto trigger is on
        elif not tooShort and self.autoTrigger and event.text() != "" \
                and event.modifiers() == 0:
            self._requestCompletion(completionPrefix=word, onlyAdapt=False)

    def _isShortcut(self, event):
        """
        Checks if the event's key and modifiers make the completion shortcut.

        :param event: QKeyEvent

        :return: bool
        """
        return ((event.modifiers() & Qt.ControlModifier > 0) and
                event.key() == self.triggerKey)

    def _onKeyPressed(self, event):
        """
        Trigger the completion with ctrl+triggerKey and handle completion events
        ourselves (insert completion and hide completer)

        :param event: QKeyEvent
        """
        isShortcut = self._isShortcut(event)
        completionPrefix = self._textUnderCursor()
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            # complete
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self._insertCompletion(self.currentCompletion)
                self.__completer.popup().hide()
                event.setAccepted(True)
                return
            # hide
            elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_Backtab:
                self.__completer.popup().hide()
                event.setAccepted(True)
                return
        # user completion request: update models and show completions
        if isShortcut:
            self._requestCompletion(completionPrefix, onlyAdapt=False)
            if event.key() == self.triggerKey:
                event.setAccepted(True)

    def _textUnderCursor(self):
        """
        Returns the word under the cursor
        """
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        selectedText = tc.selectedText()
        tokens = selectedText.split('.')
        wuc = tokens[len(tokens) - 1]
        if selectedText == ".":
            wuc = '.'
        return wuc

    def _lastCharOfLine(self):
        """
        Returns the last char of the active line.

        :return: unicode
        """
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
        return tc.selectedText()

    def _getCCRequest(self, completionPrefix):
        """
        Creates a CompletionRequest from context (line nbr, ...)

        :param completionPrefix: the completion request prefix
        """
        tc = self.editor.codeEdit.textCursor()
        line = tc.blockNumber() + 1
        col = tc.columnNumber()
        fn = self.editor.codeEdit.tagFilename
        encoding = self.editor.codeEdit.tagEncoding
        source = self.editor.codeEdit.toPlainText()
        return CompletionRequest(
            col=col, encoding=encoding, filename=fn, line=line,
            source_code=source, completionPrefix=completionPrefix)

    def _execRequest(self, request):
        """
        Executes a cc request and emit __completionResultsAvailable when the
        execution is done.

        :param request: The CodeCompletionRequest to execute.
        """
        pass

    def _createCompleterModel(self, completionPrefix):
        """
        Creates a QStandardModel that holds the suggestion from the completion
        models for the QCompleter

        :param completionPrefix:
        """
        # build the completion model
        cc_model = QStandardItemModel()
        cptSuggestion = 0
        displayedTexts = []
        self.__tooltips.clear()
        for model in self._models:
            for s in model.suggestions:
                # skip redundant completion
                if s.display != completionPrefix and \
                        not s.display in displayedTexts:
                    displayedTexts.append(s.display)
                    items = []
                    item = QStandardItem()
                    items.append(item)
                    item.setData(s.display, Qt.DisplayRole)
                    if s.description is not None:
                        self.__tooltips[s.display] = s.description
                    if s.decoration is not None:
                        item.setData(QIcon(s.decoration), Qt.DecorationRole)
                    cc_model.appendRow(items)
                    cptSuggestion += 1
            # do we need to use more completion model?
            if cptSuggestion >= self.minSuggestions:
                break  # enough suggestions
        return cc_model, cptSuggestion

    def _showCompletions(self, completionPrefix):
        """
        Shows the completion popup

        :param completionPrefix: completion prefix use to set the popup pos
        """
        c = self.__completer
        c.setCompletionPrefix(completionPrefix)
        c.popup().setCurrentIndex(
            self.__completer.completionModel().index(0, 0))
        cr = self.editor.codeEdit.cursorRect()
        charWidth = self.editor.codeEdit.fm.width('A')
        cr.setX(cr.x() - len(completionPrefix) * charWidth)
        cr.setWidth(400)
        c.complete(cr)  # popup it up!
        self._displayHighlightedTooltip(c.currentCompletion())

    def _hideCompletions(self):
        """
        Hides the completion popup
        """
        self.__completer.popup().hide()
        QToolTip.hideText()

    def _requestCompletion(self, completionPrefix, onlyAdapt=False):
        """
        Requests a code completion. The request will be transmitted to the
        background thread and treated by the __applyRequestResults slot when
        __completionResultsAvailable is emitted.

        :param completionPrefix:
        :param onlyAdapt:
        :return:
        """
        self.__preventUpdate = False
        # cancel prev running request
        if not onlyAdapt:
            request = self._getCCRequest(completionPrefix)
        else:
            request = CompletionRequest(completionPrefix=completionPrefix,
                                        onlyAdapt=True)
        # only one at a time
        if self.__active_thread_count == 0:
            if self.__cached_request:
                self.__cached_request, request = request, self.__cached_request
            self.__active_thread_count += 1
            runnable = RunnableCompleter(self._models, request)
            runnable.connect(self._applyRequestResults)
            self.thread_pool.start(runnable)
        # cache last request
        else:
            self.__cached_request = request

    def _applyRequestResults(self, request):
        """
        Updates the completer model and show the popup
        """
        self.__active_thread_count -= 1
        if self.__preventUpdate:
            return
        if not request.onlyAdapt:
            cc_model, cptSuggestion = self._createCompleterModel(
                request.completionPrefix)
            if cptSuggestion > 1:
                self.__completer.setModel(cc_model)
                self._showCompletions(request.completionPrefix)
            else:
                self._hideCompletions()
        else:
            self.__completer.setCompletionPrefix(request.completionPrefix)
            self.__completer.popup().updateGeometries()
            self.__completer.popup().setCurrentIndex(
                self.__completer.completionModel().index(0, 0))
            if self.__completer.currentCompletion() == "" or \
                    self.__completer.currentCompletion() == \
                    request.completionPrefix:
                self._hideCompletions()
        # relaunch last cached request
        if self.__cached_request and self.__active_thread_count == 0:
            self.__timer.singleShot(0.1, self.__apply_cached_request)

    def __apply_cached_request(self):
        request = self.__cached_request
        self.__active_thread_count += 1
        runnable = RunnableCompleter(self._models, request)
        runnable.connect(self._applyRequestResults)
        self.__cached_request = None
        self.thread_pool.start(runnable)

    @Slot(unicode)
    def _displayHighlightedTooltip(self, txt):
        """
        Shows/hides current suggestion tooltip next to the completer popup
        :param txt:
        :return:
        """
        if not self.displayTooltips or not txt in self.__tooltips:
            QToolTip.hideText()
            return
        tooltip = self.__tooltips[txt]
        charWidth = self.editor.codeEdit.fm.width('A')
        # show tooltip
        pos = self.__completer.popup().pos()
        pos.setX(pos.x() + 400)
        pos.setY(pos.y() - 15)
        QToolTip.showText(pos, tooltip, self.editor.codeEdit)

    def _insertCompletion(self, completion):
        """
        Inserts the completion (replace the word under cursor)

        :param completion: the completion text to insert
        """
        offset = 0
        if len(self._textUnderCursor()) > 1:
            offset = 1
        tc = self.editor.codeEdit.textCursor()
        tc.setPosition(tc.position() - offset)
        tc.select(QTextCursor.WordUnderCursor)
        tc.insertText(completion)
        self.editor.codeEdit.setTextCursor(tc)
