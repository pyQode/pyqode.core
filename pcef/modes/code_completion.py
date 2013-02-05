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
import os

from PySide.QtCore import Qt
from PySide.QtGui import QStandardItemModel, QStandardItem, QCompleter, QTextCursor, QPlainTextEdit, QIcon

from pcef.core import Mode


class Suggestion(object):
    """
    Represent a suggestion in the completion list. A suggestion is made up of the following elements:
        - display: suggestion text (display role)
        - decoration: an optional decoration icon (decoration role)
    """
    def __init__(self, txt, icon=None):
        self.display = txt
        self.decoration = icon


class CompletionModel(object):
    """
    Base class for representing a completion model.

    A completion model is a single list of suggestions associated with a priority.

    This base class can be used directly with a static list of words.
    """
    @property
    def suggestions(self):
        return self._suggestions

    def __init__(self, words, priority=0):
        """
        Create a basic completion model based
        :param words:
        :param priority:
        :return:
        """
        self.priority = priority
        self._suggestions = []

    def update(self, source_code, line, col, filename, encoding):
        """ Non-static completion model should overrides this method to update
        their suggestion list.

        This method is called whenever
        """
        pass


class DocumentWordsCompletionModel(CompletionModel):
    """
    Provides suggestions based on the current document words.
    """

    def split(self, txt, seps):
        """
        Split the document in a meaningful list of words.
        :param txt:
        :param seps:
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
            except:
                pass
        return set(words)

    def update(self, source_code, line, col, filename, encoding):
        """
        Update the suggestion list.
        :param source_code: document text
        :param line: current line number (starting at 1)
        :param col: current column number (starting at 0)
        :param filename: the document filename if any
        :param encoding: the document encoding if any
        :return:
        """
        words = self.split(
            source_code, ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{', '}', '|', ':', '"',
                          "'", "<", ">", "?", ",", ".", "/", ";", '[', ']', '\\', '\n', '\t', '-', '=', ' '])
        self._suggestions[:] = []
        for w in words:
            self._suggestions.append(Suggestion(w, QIcon(":/icons/rc/text-generic.png")))

    def __init__(self):
        super(DocumentWordsCompletionModel, self).__init__(0)


class CodeCompletionMode(Mode):
    """
    Code completion mode provides code completion to the text edit.

    The list of suggestion is supplied by a CodeCompletionModel. The mode can
    use several completion model with an order of priority. For example, in a
    python editor, we might have a smart completion model that would be use
    primarily and another basic document word completion as a fallback system
    when the smart system fails to provide enough suggestions.

    The mode use a QCompleter to provides the list of suggestions.
    """
    IDENTIFIER = "Code completion"
    DESCRIPTION = "Provides code completion though completion models"

    def __init__(self):
        super(CodeCompletionMode, self).__init__(self.IDENTIFIER, self.DESCRIPTION)
        self.completer = QCompleter()
        self.completer.activated.connect(self.insertCompletion)
        self.completer.highlighted.connect(self.onHighlighted)
        #: List of completion models
        self._models = [DocumentWordsCompletionModel()]

    def install(self, editor):
        super(CodeCompletionMode, self).install(editor)
        self.editor.codeEdit.keyPressed.connect(self.onKeyPressed)
        self.editor.codeEdit.textChanged.connect(self.onTextChanged)
        self.editor.codeEdit.focusedIn.connect(self.onFocusIn)
        self.completer.setWidget(editor.codeEdit)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitive)

    def onStateChanged(self, state):
        pass

    def containsAny(self, str, set):
        """Check whether 'str' contains ANY of the chars in 'set'"""
        return 1 in [c in str for c in set]

    def onFocusIn(self, event):
        self.completer.setWidget(self.editor.codeEdit)

    def onHighlighted(self, completion):
        self.currentCompletion = completion

    def onTextChanged(self):
        completionPrefix = self.textUnderCursor()
        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-= "
        # hide popup if completion prefix len < 3 or end of word
        if len(completionPrefix) < 3 or self.containsAny(completionPrefix, eow):
            self.completer.popup().hide()
            return
        if completionPrefix != self.completer.completionPrefix():
            self.updateModels(completionPrefix)
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
        c = self.completer
        cr = self.editor.codeEdit.cursorRect()
        cr.setWidth(c.popup().sizeHintForColumn(0) + c.popup().verticalScrollBar().sizeHint().width())
        c.complete(cr)  # popup it up!

    def onKeyPressed(self, event):
        if self.completer.popup().isVisible():
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.insertCompletion(self.currentCompletion)
                self.completer.popup().hide()
                event.setAccepted(True)
                return  # let the completer do default behavior
            elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_Backtab:
                self.completer.popup().hide()
                event.setAccepted(True)
                return  # let the completer do default behavior
        isShortcut = ((event.modifiers() & Qt.ControlModifier > 0) and event.key() == Qt.Key_Space)  # CTRL+SPACE
        if isShortcut:
            completionPrefix = self.textUnderCursor()
            self.updateModels(completionPrefix)
            c = self.completer
            c.setCompletionPrefix(completionPrefix)
            c.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr = self.editor.codeEdit.cursorRect()
            cr.setWidth(c.popup().sizeHintForColumn(0) + c.popup().verticalScrollBar().sizeHint().width())
            c.complete(cr)  # popup it up!

    def textUnderCursor(self):
        tc = self.editor.codeEdit.textCursor()
        tc.movePosition ( QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        return tc.selectedText()

    def updateModels(self, completionPrefix):
        sorted_models = sorted(self._models, key=lambda mdl: mdl.priority, reverse=True)
        tc = self.editor.codeEdit.textCursor()
        line = tc.blockNumber() + 1
        col = tc.columnNumber()
        fn = self.editor.codeEdit.filename
        encoding = self.editor.codeEdit.encoding
        cc_model = QStandardItemModel()
        cptSuggestion = 0
        for model in sorted_models:
            model.update(self.editor.codeEdit.toPlainText(), line, col, fn, encoding)
            for s in model.suggestions:
                if s.display != completionPrefix:
                    item = QStandardItem()
                    item.setData(s.display, Qt.DisplayRole)
                    if s.decoration is not None:
                        item.setData(s.decoration, Qt.DecorationRole)
                    cc_model.appendRow(item)
                    cptSuggestion += 1
            if cptSuggestion >= 50:
                break
        self.completer.setModel(cc_model)

    def insertCompletion(self, completion=""):
        tc = self.editor.codeEdit.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        tc.insertText(completion)
        self.editor.codeEdit.setTextCursor(tc)
