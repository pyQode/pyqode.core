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
from PySide.QtCore import Qt, QRunnable, Signal, QObject, QThreadPool, Slot
from PySide.QtGui import QStandardItemModel, QStandardItem, QCompleter, QTextCursor, QIcon

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
            self._suggestions.append(Suggestion(w, QIcon(":/icons/rc/text-generic.png")))

    def __init__(self):
        super(DocumentWordsCompletionModel, self).__init__(priority=0)


class CodeCompletionMode(Mode):
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

    def __init__(self):
        super(CodeCompletionMode, self).__init__(self.IDENTIFIER, self.DESCRIPTION)
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
        self.__caseSensitivity = Qt.CaseSensitive

        #: The internal QCompleter
        self.__completer = QCompleter()
        # self.__completer.activated.connect(self._insertCompletion)
        self.__completer.highlighted.connect(self._onHighlighted)
        self.__preventUpdate = False

        #: List of completion models
        self._models = [DocumentWordsCompletionModel()]

    def addModel(self, model):
        self._models.append(model)

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
        if state is True:
            self.editor.codeEdit.keyPressed.connect(self._onKeyPressed)
            self.editor.codeEdit.postKeyPressed.connect(self._onKeyReleased)
            self.editor.codeEdit.textChanged.connect(self._onTextChanged)
            self.editor.codeEdit.focusedIn.connect(self._onFocusIn)
        else:
            self.editor.codeEdit.keyPressed.disconnect(self._onKeyPressed)
            self.editor.codeEdit.postKeyPressed.disconnect(self._onKeyReleased)
            self.editor.codeEdit.textChanged.disconnect(self._onTextChanged)
            self.editor.codeEdit.focusedIn.disconnect(self._onFocusIn)

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
        eow = "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-= "
        # hide popup if completion prefix len < 3 or end of word
        containsEow = self.containsAny(completionPrefix, eow)
        tooShort = len(completionPrefix) < self.nbTriggerChars
        if not self.__completer.popup().isVisible() and (tooShort or containsEow):
            self.__completer.popup().hide()
            return
        if completionPrefix != self.__completer.completionPrefix() and self.__preventUpdate is False:
            if self.autoTrigger is True:
                self._updateModels(completionPrefix)
                self.__completer.setCompletionPrefix(completionPrefix)
                self.__completer.popup().setCurrentIndex(self.__completer.completionModel().index(0, 0))
                c = self.__completer
                cr = self.editor.codeEdit.cursorRect()
                charWidth = self.editor.codeEdit.fm.width('A')
                cr.setX(cr.x() - len(completionPrefix) * charWidth)
                cr.setWidth(400)
                c.complete(cr)
            else:
                self.__completer.setCompletionPrefix(completionPrefix)
                self.__completer.popup().setCurrentIndex(self.__completer.completionModel().index(0, 0))

    def _onKeyReleased(self, event):
        word = self._textUnderCursor()
        isShortcut = (event.modifiers() & Qt.ControlModifier > 0) and event.key() == self.triggerKey
        if isShortcut is False and event.modifiers() == 0 and (word.isspace() or word == ""):
            self.__completer.popup().hide()
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete or event.modifiers() != 0:
            self.__preventUpdate = False

    def _onKeyPressed(self, event):
        """
        Trigger the completion with ctrl+triggerKey and handle completion events ourselves (insert completion and hide
        completer)

        :param event: QKeyEvent
        """
        isShortcut = (event.modifiers() & Qt.ControlModifier > 0) and event.key() == self.triggerKey
        completionPrefix = self._textUnderCursor()
        if self.__completer.popup().isVisible():
            # complete
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self._insertCompletion(self.currentCompletion)
                self.__completer.popup().hide()
                event.setAccepted(True)
            # hide
            elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_Backtab:
                self.__completer.popup().hide()
                event.setAccepted(True)
        elif isShortcut is True:
            self.__preventUpdate = False
            self._updateModels(completionPrefix)
            c = self.__completer
            c.setCompletionPrefix(completionPrefix)
            c.popup().setCurrentIndex(self.__completer.completionModel().index(0, 0))
            cr = self.editor.codeEdit.cursorRect()
            charWidth = self.editor.codeEdit.fm.width('A')
            cr.setX(cr.x() - len(completionPrefix) * charWidth)
            cr.setWidth(400)
            c.complete(cr)  # popup it up!
        # prevent updating models when deleting text
        elif ((not completionPrefix.isspace() and completionPrefix != "") and
              (event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete or event.modifiers() != 0)):
            self.__preventUpdate = True

    def _textUnderCursor(self):
        """
        Return the word under the cursor
        """
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        tokens = tc.selectedText().split('.')
        return tokens[len(tokens) - 1]

    def _updateModels(self, completionPrefix):
        """
        Update the completion models while there is not enough suggestions and build the standard item model
        used for the final completion model.

        :param completionPrefix: The current completion prefix.
        """
        # use models from the highest to lowest priority
        sorted_models = sorted(self._models, key=lambda mdl: mdl.priority, reverse=True)
        # get completion data needed by most code completion library (source, line, column, filename, encoding)
        tc = self.editor.codeEdit.textCursor()
        line = tc.blockNumber() + 1
        col = tc.columnNumber()
        fn = self.editor.codeEdit.tagFilename
        encoding = self.editor.codeEdit.tagEncoding
        source = self.editor.codeEdit.toPlainText()
        # build the completion model
        cc_model = QStandardItemModel()
        cc_model.clear()
        cptSuggestion = 0
        for model in sorted_models:
            # update the current model
            model.update(source, line, col, fn, encoding)
            # add suggestion as an standard item to the final completion model
            for s in model.suggestions:
                # skip redundant completion
                if s.display != completionPrefix:
                    items = []
                    item = QStandardItem()
                    items.append(item)
                    item.setData(s.display, Qt.DisplayRole)
                    if s.description is not None:
                        item_desc = QStandardItem()
                        item_desc.setData(s.description, Qt.DisplayRole)
                        items.append(item_desc)
                    if s.decoration is not None:
                        item.setData(s.decoration, Qt.DecorationRole)
                    # print len(items)
                    cc_model.appendRow(items)
                    cptSuggestion += 1
            # do we need to use more completion model?
            if cptSuggestion >= self.minSuggestions:
                break  # enough suggestions
        self.__completer.setModel(cc_model)

    def _insertCompletion(self, completion):
        """
        Insert the completion (replace the word under cursor)

        :param completion: the completion text to insert
        """
        tc = self.editor.codeEdit.textCursor()
        tc.setPosition(tc.position() - 1)
        tc.select(QTextCursor.WordUnderCursor)
        print tc.selectedText()
        tc.insertText(completion)
        self.editor.codeEdit.setTextCursor(tc)
