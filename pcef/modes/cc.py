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
from PySide.QtCore import Qt, Slot, QThread, Signal, QMutex, QModelIndex
from PySide.QtGui import QStandardItemModel, QStandardItem, QCompleter, QTextCursor, QIcon, QToolTip

from pcef.core import Mode


class Suggestion(object):
    """
    Represent a suggestion in the completion list. A suggestion is made up of the following elements:
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
        return self._suggestions

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
        Non-static completion model should overrides this method to update their suggestion list.

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

        :return: A set of words found in the document (excluding punctuations, numbers, ...)
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
            source_code, ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{', '}', '|', ':', '"',
                          "'", "<", ">", "?", ",", ".", "/", ";", '[', ']', '\\', '\n', '\t', '-', '=', ' '])
        self._suggestions[:] = []
        for w in words:
            self._suggestions.append(Suggestion(w, ":/icons/rc/text-generic.png"))

    def __init__(self):
        super(DocumentWordsCompletionModel, self).__init__(priority=0)


class CompletionRequest(object):
    def __init__(self, source_code="", line=0, col=1, filename="", encoding="", completionPrefix="", onlyAdapt=False):
        self.source_code = source_code
        self.line = line
        self.col = col
        self.filename = filename
        self.encoding = encoding
        self.completionPrefix = completionPrefix
        self.onlyAdapt = onlyAdapt


class CodeCompletionMode(Mode, QThread):
    """
    This mode provides code completion to the CodeEdit widget.

    The list of suggestion is supplied by a CodeCompletionModel.

    Code completion may use more than one completion model. The suggestions list is then filled model per model by
    beginning by the highest priority as long as the number of suggestions is lower than
    :attr:`pcef.modes.code_completion.CodeCompletion.minSuggestions`. For example, a python editor will use a smart
    completion model with a high priority and use the DocumentWordsCompletion model as a fallback system when the
    smart model fails to provide enough suggestions.

    The mode uses a QCompleter to provides display the list of suggestions.

    Code completion is triggered using ctrl+space or when there is at least three
    characters in the word being typed.
    """
    #: Mode identifier
    IDENTIFIER = "Code completion"

    #: Mode description
    DESCRIPTION = "Provides code completion though completion models"

    __completionResultsAvailable = Signal(CompletionRequest)

    def __init__(self):
        super(CodeCompletionMode, self).__init__(self.IDENTIFIER, self.DESCRIPTION)
        QThread.__init__(self)
        self.__cc_request_queue = deque()
        # self.mutex = QMutex()
        #: Defines the min number of suggestions. This is used to know we should avoid using lower priority models.
        #  If there is at least minSuggestions in the suggestions list, we won't use other completion model.
        self.minSuggestions = 50
        #: Trigger key (automatically associated with the control modifier)
        self.triggerKey = Qt.Key_Space
        #: Number of chars needed to trigger the code completion
        self.nbTriggerChars = 1
        #: Tells if the completion should be triggered automatically (when len(wordUnderCursor) > nbTriggerChars )
        #  Default is True. Turning this option off might enhance performances and usability
        self.autoTrigger = True
        #: Show/Hide current suggestion tooltip
        self.displayTooltips = True
        self.__caseSensitivity = Qt.CaseSensitive
        #: The internal QCompleter
        self.__completer = QCompleter()
        # self.__completer.activated.connect(self._insertCompletion)
        self.__completer.highlighted.connect(self._onHighlighted)
        self.__completer.activated.connect(self._insertCompletion)
        self.__preventUpdate = False
        #: List of completion models
        self._models = [DocumentWordsCompletionModel()]
        self.__tooltips = {}

    def run(self, *args, **kwargs):
        self.is_running = True
        while self.is_running:
            if len(self.__cc_request_queue):
                request = self.__cc_request_queue.pop()
                if not request.onlyAdapt:
                    self.__exec_request(request)
                self.__completionResultsAvailable.emit(request)
            self.msleep(1)

    def addModel(self, model):
        self._models.append(model)
        self._models = sorted(self._models, key=lambda mdl: mdl.priority, reverse=True)

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
            self.editor.codeEdit.textChanged.connect(self._onTextChanged)
            self.editor.codeEdit.focusedIn.connect(self._onFocusIn)
            self.__completer.highlighted.connect(self.__displayHilightedTooltip)
            self.__completionResultsAvailable.connect(self._updateModel)
            self.start()
        else:
            self.editor.codeEdit.keyPressed.disconnect(self._onKeyPressed)
            self.editor.codeEdit.postKeyPressed.disconnect(self._onKeyReleased)
            self.editor.codeEdit.textChanged.disconnect(self._onTextChanged)
            self.editor.codeEdit.focusedIn.disconnect(self._onFocusIn)
            self.is_running = False
            self.wait()

    @staticmethod
    def containsAny(txt, charsSet):
        """Check whether 'txt' contains ANY of the chars in 'charsSet'"""
        return 1 in [c in txt for c in charsSet]

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

    @Slot()
    def _onTextChanged(self):
        """
        Update completion prefix if the word's len is > self.nbTriggerChars
        """
        completionPrefix = self._textUnderCursor()
        eow = "~!@#$%^&*()+{}|:\"<>?,/;'[]\\-= "
        # hide popup if completion prefix len < 3 or end of word
        prefixLen = len(completionPrefix)
        prevPrefixLen = len(self.__completer.completionPrefix())
        containsEow = self.containsAny(completionPrefix, eow)
        tooShort = len(completionPrefix) < self.nbTriggerChars and not "." in completionPrefix
        shortcut = self.lastCharOfLine() == "." or (prefixLen == self.nbTriggerChars and
                                                    prevPrefixLen == self.nbTriggerChars - 1)
        # close popup if not enough characters or on an end of word
        if not self.__completer.popup().isVisible() and (tooShort or containsEow) and not shortcut:
            self.__hideCompletions()
            return

        # emptyPrefix = self.__completer.completionPrefix() == "" or completionPrefix == ""
        # prevPrefix = self.__completer.completionPrefix()
        # alreadySearched = not emptyPrefix and (prevPrefix in completionPrefix or completionPrefix in prevPrefix)
        if not shortcut:
            if self.__completer.popup().isVisible():
                self.__request_completion(completionPrefix, onlyAdapt=True)
        else:
            if not self.__completer.popup().isVisible():
                self.__request_completion(completionPrefix, onlyAdapt=False)

    def _onKeyReleased(self, event):
        # closes popup if word under cursor is space or empty
        word = self._textUnderCursor()
        isShortcut = self.isShortcut(event)
        if isShortcut is False and event.modifiers() == 0 and (word.isspace() or word == ""):
            self.__hideCompletions()

    def isShortcut(self, event):
        isShortcut = ((event.modifiers() & Qt.ControlModifier > 0) and event.key() == self.triggerKey) or \
                     (event.key() == Qt.Key_Period and self.autoTrigger and self.nbTriggerChars >= 1)
        return isShortcut

    def _onKeyPressed(self, event):
        """
        Trigger the completion with ctrl+triggerKey and handle completion events ourselves (insert completion and hide
        completer)

        :param event: QKeyEvent
        """
        isShortcut = self.isShortcut(event)
        completionPrefix = self._textUnderCursor()
        # handle completer popup events ourselves
        if self.__completer.popup().isVisible():
            # complete
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self._insertCompletion(self.currentCompletion)
                self.__completer.popup().hide()
                self.__completer.setCompletionPrefix("")
                event.setAccepted(True)
            # hide
            elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_Backtab:
                self.__completer.popup().hide()
                self.__completer.setCompletionPrefix("")
                event.setAccepted(True)
        # user completion request: update models and show completions
        elif isShortcut:
            self.__request_completion(completionPrefix)

    def _textUnderCursor(self):
        """
        Return the word under the cursor
        """
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        selectedText = tc.selectedText()
        tokens = selectedText.split('.')
        wuc = tokens[len(tokens) - 1]
        if selectedText == ".":
            wuc = '.'
        return wuc

    def lastCharOfLine(self):
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
        return tc.selectedText()

    def __get_cc_infos(self, completionPrefix):
        tc = self.editor.codeEdit.textCursor()
        line = tc.blockNumber() + 1
        col = tc.columnNumber()
        fn = self.editor.codeEdit.tagFilename
        encoding = self.editor.codeEdit.tagEncoding
        source = self.editor.codeEdit.toPlainText()
        return CompletionRequest(col=col, encoding=encoding, filename=fn, line=line, source_code=source,
                                 completionPrefix=completionPrefix)

    def __exec_request(self, request):
        # self.mutex.lock()
        # try:
        for model in self._models:
            try:
                # update the current model
                model.update(request.source_code, request.line, request.col, request.filename, request.encoding)
            except :
                pass
        # except
        # finally:
        #     self.mutex.unlock()

    def __createCompleterModel(self, completionPrefix):
        # build the completion model
        cc_model = QStandardItemModel()
        cptSuggestion = 0
        displayedTexts = []
        self.__tooltips.clear()
        for model in self._models:
            for s in model.suggestions:
                if s.display != completionPrefix and not s.display in displayedTexts:  # skip redundant completion
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
            if cptSuggestion >= self.minSuggestions:  # do we need to use more completion model?
                break  # enough suggestions
        return cc_model, cptSuggestion

    def __showCompletions(self, completionPrefix):
        c = self.__completer
        c.setCompletionPrefix(completionPrefix)
        c.popup().setCurrentIndex(self.__completer.completionModel().index(0, 0))
        cr = self.editor.codeEdit.cursorRect()
        charWidth = self.editor.codeEdit.fm.width('A')
        cr.setX(cr.x() - len(completionPrefix) * charWidth)
        cr.setWidth(400)
        c.complete(cr)  # popup it up!
        self.__displayHilightedTooltip(c.currentCompletion())

    def __hideCompletions(self):
        self.__preventUpdate = True
        self.__completer.popup().hide()
        self.__completer.setCompletionPrefix("")
        QToolTip.hideText()

    def __request_completion(self, completionPrefix, onlyAdapt=False):
        self.__preventUpdate = False
        # cancel prev running request
        if not onlyAdapt:
            self.__cc_request_queue.append(self.__get_cc_infos(completionPrefix))
        else:
            self.__cc_request_queue.append(CompletionRequest(completionPrefix=completionPrefix, onlyAdapt=True))

    def _updateModel(self, request):
        """
        Updates the completer model and show the popup
        """
        if self.__preventUpdate:
            return
        if not request.onlyAdapt:
            # self.mutex.lock()
            cc_model, cptSuggestion = self.__createCompleterModel(request.completionPrefix)
            # self.mutex.unlock()
            if cptSuggestion > 1:
                self.__completer.setModel(cc_model)
                self.__showCompletions(request.completionPrefix)
            else:
                self.__hideCompletions()
        else:
            self.__completer.setCompletionPrefix(request.completionPrefix)
            self.__completer.popup().updateGeometries()
            self.__completer.popup().setCurrentIndex(self.__completer.completionModel().index(0, 0))
            if self.__completer.currentCompletion() == "" or self.__completer.currentCompletion() == \
                    request.completionPrefix:
                self.__hideCompletions()

    @Slot(unicode)
    def __displayHilightedTooltip(self, txt):
        if not self.displayTooltips:
            return
        if txt in self.__tooltips:
            tooltip = self.__tooltips[txt]
            charWidth = self.editor.codeEdit.fm.width('A')
            # show tooltip
            pos = self.__completer.popup().pos()
            pos.setX(pos.x() + 400)
            pos.setY(pos.y() - 15)
            QToolTip.showText(pos, tooltip, self.editor.codeEdit)

    def _insertCompletion(self, completion):
        """
        Insert the completion (replace the word under cursor)

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
