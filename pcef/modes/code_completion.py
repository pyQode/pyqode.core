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
from PySide.QtCore import Qt
from PySide.QtGui import QStandardItemModel, QCompleter, QTextCursor, QPlainTextEdit
from pcef.base import Mode


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
    Represents a completion model. A model is a single list of suggestions associated with a priority.
    """
    @property
    def suggestions(self):
        return self._suggestions

    def __init__(self, wordList=None, priority=0):
        self.priority = priority
        self._suggestions = []
        for word in wordList:
            self._suggestions.append(Suggestion(word))

    def update(self, source_code, line, col, filename, encoding):
        """ Non-static completion model should overrides this method to update
        their suggestion list.

        This method is called whenever
        """
        pass


def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars in 'set'"""
    return 1 in [c in str for c in set]


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

    def install(self, editor):
        super(CodeCompletionMode, self).install(editor)
        self.editor.textEdit.keyPressed.connect(self.onKeyPressed)
        self.editor.textEdit.focusedIn.connect(self.onFocusIn)
        self.completer.setWidget(editor.textEdit)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitive)

    def _onStateChanged(self, state):
        pass

    def onFocusIn(self, event):
        self.completer.setWidget(self.editor.textEdit)

    def onHighlighted(self, completion):
        self.currentCompletion = completion

    def onKeyPressed(self, event):
        if self.completer.popup().isVisible():
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                print "Insert completion"
                self.insertCompletion(self.currentCompletion)
                self.completer.popup().hide()
                event.setAccepted(True)
                return  # let the completer do default behavior
            elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_Backtab:
                self.completer.popup().hide()
                event.setAccepted(True)
                return  # let the completer do default behavior
        isShortcut = ((event.modifiers() & Qt.ControlModifier > 0) and event.key() == Qt.Key_Space)  # CTRL+SPACE
        if not isShortcut and not event.isAccepted():
            QPlainTextEdit.keyPressEvent(self.editor.textEdit, event)
            event.setAccepted(True)
        completionPrefix = self.textUnderCursor()
        ctrlOrShift = event.modifiers() & Qt.ControlModifier > 0 or event.modifiers() & Qt.ShiftModifier > 0
        isEmptyText = completionPrefix == ""
        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-= "
        hasModifier = (event.modifiers() != Qt.NoModifier) and not ctrlOrShift
        if isShortcut is False and (hasModifier or isEmptyText or len(completionPrefix) < 3 or containsAny(completionPrefix, eow)):
            self.completer.popup().hide()
            event.setAccepted(True)
            return
        if completionPrefix != self.completer.completionPrefix():
            self.updateModels()
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
        c = self.completer
        cr = self.editor.textEdit.cursorRect()
        cr.setWidth(c.popup().sizeHintForColumn(0) + c.popup().verticalScrollBar().sizeHint().width())
        c.complete(cr)  # popup it up!

    def textUnderCursor(self):
        tc = self.editor.textEdit.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def updateModels(self):
        pass

    def insertCompletion(self, completion=""):
        tc = self.editor.textEdit.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        tc.insertText(completion)
        self.editor.textEdit.setTextCursor(tc)
