#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
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
This module contains the search and replace panel
"""
from PyQt4 import QtCore, QtGui

from pyqode.core.api import constants
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.editor import Panel
from pyqode.core.api.system import DelayJobRunner, drift_color
from pyqode.core.ui.search_panel_ui import Ui_SearchPanel


class SearchAndReplacePanel(Panel, DelayJobRunner, Ui_SearchPanel):
    """
    This panel allow the user to search and replace some text in the current
    editor.

    It uses the QTextDocument API to search for some text. Search operation is
    performed in a background thread.

    The search panel can also be used programatically.

    To do that, the client code first requests a search using
    :meth:`requestSearch` and connects to
    :attr:`search_finished`.

    The results of the search can then be retrieved using
    :attr:`cptOccurrences` and :meth:`getOccurrences`.

    The client code may now navigate through occurrences using
    :meth:`selectNext` or :meth:`selectPrevious`, or replace the occurrences
    with a specific text using :meth:`replaceOccurrence` or :meth:`replaceAll`.
    """
    #: The panel identifier
    IDENTIFIER = "searchAndReplacePanel"
    #: The panel description
    DESCRIPTION = "Search and replace text in the editor"

    STYLESHEET = """SearchAndReplacePanel
    {
        background-color: %(bck)s;
        color: %(color)s;
    }

    QPushButton
    {
        color: %(color)s;
        background-color: transparent;
        padding: 5px;
        border: none;
    }

    QPushButton:hover
    {
        background-color: %(highlight)s;
        border: none;
        border-radius: 5px;
        color: %(color)s;
    }

    QPushButton:pressed, QCheckBox:pressed
    {
        border: 1px solid %(bck)s;
    }

    QPushButton:disabled
    {
        color: %(highlight)s;
    }

    QCheckBox
    {
        padding: 4px;
        color: %(color)s;
    }

    QCheckBox:hover
    {
            background-color: %(highlight)s;
            color: %(color)s;
            border-radius: 5px;
    }
    """
    _KEYS = ["panelBackground", "background", "panelForeground",
             "panelHighlight"]

    #: Signal emitted when a search operation finished
    search_finished = QtCore.pyqtSignal()

    @property
    def background(self):
        return self.editor.style.value("searchOccurrenceBackground")

    @background.setter
    def background(self, value):
        self.editor.style.set_value("searchOccurrenceBackground", value)

    @property
    def foreground(self):
        return self.editor.style.value("searchOccurrenceForeground")

    @foreground.setter
    def foreground(self, value):
        self.editor.set_value("searchOccurrenceForeground", value)

    def refresh_icons(self, use_theme=True):
        values = [
            ("edit-find", "Find",
             [self.actionSearch], [self.labelSearch]),
            ("edit-find-replace", "Replace",
             [self.actionActionSearchAndReplace], [self.labelReplace]),
            ("go-down", "Next",
             [self.actionFindNext, self.pushButtonNext], []),
            ("go-up", "Previous",
             [self.actionFindPrevious, self.pushButtonPrevious], []),
            ("application-exit", "Close", [self.pushButtonClose], []),
        ]
        for theme, name, actions, labels in values:
            icon = constants.ICONS[name]
            if use_theme:
                icon = QtGui.QIcon.fromTheme(theme, QtGui.QIcon(icon))
            else:
                icon = QtGui.QIcon(icon)
            for action in actions:
                action.setIcon(icon)
            for label in labels:
                label.setPixmap(icon.pixmap(16, 16))

    def __init__(self):
        Panel.__init__(self)
        DelayJobRunner.__init__(self, self, nb_threads_max=1, delay=500)
        Ui_SearchPanel.__init__(self)
        self.setupUi(self)

        #: Occurrences counter
        self.cpt_occurences = 0
        self._previous_stylesheet = ""
        self._separator = None
        self._decorations = []
        self._mutex = QtCore.QMutex()
        self._occurrences = []
        self._current_occurrence = -1
        self._update_buttons(txt="")
        self.lineEditSearch.installEventFilter(self)
        self.lineEditReplace.installEventFilter(self)
        self.refresh_icons()

    def _on_install(self, editor):
        Panel._on_install(self, editor)
        self._reset_stylesheet()
        self.on_pushButtonClose_clicked()
        self.editor.style.add_property("searchOccurrenceBackground",
                                       constants.SEARCH_OCCURRENCES_BACKGROUND)
        self.editor.style.add_property("searchOccurrenceForeground",
                                       constants.SEARCH_OCCURRENCES_FOREGROUND)

    def _on_style_changed(self, section, key):
        Panel._on_style_changed(self, section, key)
        if key in self._KEYS or not key:
            self._reset_stylesheet()
        if not key or key in ["searchOccurrenceBackground",
                              "searchOccurrenceForeground"]:
            self._refresh_decorations()

    def _refresh_decorations(self):
        for d in self._decorations:
            self.editor.remove_decoration(d)
            d.set_background(QtGui.QBrush(self.background))
            d.set_foreground(QtGui.QBrush(self.foreground))
            self.editor.add_decoration(d)

    def _on_state_changed(self, state):
        Panel._on_state_changed(self, state)
        if state:
            # add menus
            self._separator = self.editor.add_separator()
            self.editor.add_action(self.actionSearch)
            self.editor.add_action(self.actionActionSearchAndReplace)
            self.editor.add_action(self.actionFindNext)
            self.editor.add_action(self.actionFindPrevious)
            # requestSearch slot
            self.editor.textChanged.connect(self.request_search)
            self.lineEditSearch.textChanged.connect(self.request_search)
            self.checkBoxCase.stateChanged.connect(self.request_search)
            self.checkBoxWholeWords.stateChanged.connect(self.request_search)
            # navigation slots
            self.pushButtonNext.clicked.connect(self.select_next)
            self.actionFindNext.triggered.connect(self.select_next)
            self.pushButtonPrevious.clicked.connect(self.select_previous)
            self.actionFindPrevious.triggered.connect(self.select_previous)
            # replace slots
            self.pushButtonReplace.clicked.connect(self.replace)
            self.pushButtonReplaceAll.clicked.connect(self.replace_all)
            # internal updates slots
            self.lineEditReplace.textChanged.connect(self._update_buttons)
            self.search_finished.connect(self._on_search_finished)
        else:
            # remove menus
            if self._separator is not None:
                self.editor.remove_action(self._separator)
            self.editor.remove_action(self.actionSearch)
            self.editor.remove_action(
                self.actionActionSearchAndReplace)
            self.editor.remove_action(self.actionFindNext)
            self.editor.remove_action(self.actionFindPrevious)
            # requestSearch slot
            self.editor.textChanged.disconnect(self.request_search)
            self.lineEditSearch.textChanged.disconnect(self.request_search)
            self.checkBoxCase.stateChanged.disconnect(self.request_search)
            self.checkBoxWholeWords.stateChanged.disconnect(
                self.request_search)
            # navigation slots
            self.pushButtonNext.clicked.disconnect(self.select_next)
            self.actionFindNext.triggered.disconnect(self.select_next)
            self.pushButtonPrevious.clicked.disconnect(self.select_previous)
            # replace slots
            self.pushButtonReplace.clicked.disconnect(self.replace)
            self.pushButtonReplaceAll.clicked.disconnect(self.replace_all)
            # internal updates slots
            self.lineEditReplace.textChanged.disconnect(self._update_buttons)
            self.search_finished.connect(self._on_search_finished)

    def close_panel(self):
        """
        Closes the panel
        """
        self.hide()
        self.lineEditReplace.clear()
        self.lineEditSearch.clear()

    @QtCore.pyqtSlot()
    def on_pushButtonClose_clicked(self):
        self.close_panel()

    @QtCore.pyqtSlot()
    def on_actionSearch_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.hide()
        self.show()
        new_text = self.editor.selected_text()
        old_text = self.lineEditSearch.text()
        text_changed = new_text != old_text
        self.lineEditSearch.setText(new_text)
        self.lineEditSearch.selectAll()
        self.lineEditSearch.setFocus()
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        if not text_changed:
            self.request_search(new_text)

    @QtCore.pyqtSlot()
    def on_actionActionSearchAndReplace_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.show()
        self.show()
        new_txt = self.editor.selected_text()
        old_txt = self.lineEditSearch.text()
        txt_changed = new_txt != old_txt
        self.lineEditSearch.setText(new_txt)
        self.lineEditReplace.clear()
        self.lineEditReplace.setFocus()
        if not txt_changed:
            self.request_search(new_txt)

    def focusOutEvent(self, event):
        self.stop_job()
        self.cancel_requests()
        Panel.focusOutEvent(self, event)

    def request_search(self, txt=None):
        """
        Requests a search operation.

        :param txt: The text to replace. If None, the content of lineEditSearch
                    is used instead.
        """
        if txt is None or isinstance(txt, int):
            txt = self.lineEditSearch.text()
        if txt:
            self.request_job(self._exec_search, True,
                             txt, self.editor.document().clone(),
                             self.editor.textCursor(),
                             self._search_flags())
        else:
            self.cancel_requests()
            self.stop_job()
            self._clear_occurrences()
            self._on_search_finished()

    def get_occurences(self):
        """
        Returns the list of text occurrences.

        An occurrence is a tuple that contains start and end positions.

        :return: List of tuple(int, int)
        """
        self._mutex.lock()
        retval = []
        for occ in self._occurrences:
            retval.append(occ)
        self._mutex.unlock()
        return retval

    def select_next(self):
        """
        Selects the next occurrence.

        :return: True in case of success, false if no occurrence could be
                 selected.
        """
        cr = self._current_occurrence()
        occurrences = self.get_occurences()
        if (cr == -1 or
                cr == len(occurrences) - 1):
            cr = 0
        else:
            cr += 1
        self._set_current_occurrence(cr)
        try:
            tc = self.editor.textCursor()
            tc.setPosition(occurrences[cr][0])
            tc.setPosition(occurrences[cr][1], tc.KeepAnchor)
            self.editor.setTextCursor(tc)
            return True
        except IndexError:
            return False

    def select_previous(self):
        """
        Selects previous occurrence.

        :return: True in case of success, false if no occurrence could be
                 selected.
        """
        cr = self._current_occurrence()
        occurrences = self.get_occurences()
        if (cr == -1 or
                cr == 0):
            cr = len(occurrences) - 1
        else:
            cr -= 1
        self._set_current_occurrence(cr)
        try:
            tc = self.editor.textCursor()
            tc.setPosition(occurrences[cr][0])
            tc.setPosition(occurrences[cr][1], tc.KeepAnchor)
            self.editor.setTextCursor(tc)
            return True
        except IndexError:
            return False

    def replace(self, text=None):
        """
        Replaces the selected occurrence.

        :param text: The replacement text. If it is None, the lineEditReplace's
                     text is used instead.

        :return True if the text could be replace properly, False if there is
                no more occurrences to replace.
        """
        if text is None or isinstance(text, bool):
            text = self.lineEditReplace.text()
        cr = self._current_occurrence()
        occurrences = self.get_occurences()
        if cr == -1:
            self.select_next()
            cr = self._current_occurrence()
        try:
            # prevent search request due to editor textChanged
            try:
                self.editor.textChanged.disconnect(self.request_search)
            except (RuntimeError, TypeError):
                # already disconnected
                pass
            occ = occurrences[cr]
            tc = self.editor.textCursor()
            tc.setPosition(occ[0])
            tc.setPosition(occ[1], tc.KeepAnchor)
            len_to_replace = len(tc.selectedText())
            len_replacement = len(text)
            offset = len_replacement - len_to_replace
            tc.insertText(text)
            self.editor.setTextCursor(tc)
            self._remove_occurrence(cr, offset)
            cr -= 1
            self._set_current_occurrence(cr)
            self.select_next()
            self.cpt_occurences = len(self.get_occurences())
            self._update_label_matches()
            self._update_buttons()
            return True
        except IndexError:
            return False
        finally:
            self.editor.textChanged.connect(self.request_search)

    def replace_all(self, text=None):
        """
        Replaces all occurrences in the editor's document.

        :param text: The replacement text. If None, the content of the lineEdit
                     replace will be used instead
        """
        tc = self.editor.textCursor()
        tc.beginEditBlock()
        remains = self.replace(text=text)
        while remains:
            remains = self.replace(text=text)
        tc.endEditBlock()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if (event.key() == QtCore.Qt.Key_Tab or
                    event.key() == QtCore.Qt.Key_Backtab):
                return True
            elif (event.key() == QtCore.Qt.Key_Return or
                    event.key() == QtCore.Qt.Key_Enter):
                if obj == self.lineEditReplace:
                    if event.modifiers() & QtCore.Qt.ControlModifier:
                        self.replace_all()
                    else:
                        self.replace()
                elif obj == self.lineEditSearch:
                    self.select_next()
                return True
            elif event.key() == QtCore.Qt.Key_Escape:
                self.on_pushButtonClose_clicked()
        return Panel.eventFilter(self, obj, event)

    def _search_flags(self):
        """ Returns the user search flag """
        flags = QtGui.QTextDocument.FindFlags(0)
        if self.checkBoxCase.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.checkBoxWholeWords.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        return flags

    def _exec_search(self, text, doc, original_cursor, flags):
        self._mutex.lock()
        self._occurrences[:] = []
        self._current_occurrence = -1
        if text:
            matches = 0
            cursor = doc.find(text, 0, flags)
            while not cursor.isNull():
                if self._compare_cursors(cursor, original_cursor):
                    self._current_occurrence = matches
                self._occurrences.append((cursor.selectionStart(),
                                          cursor.selectionEnd()))
                cursor.setPosition(cursor.position() + 1)
                cursor = doc.find(text, cursor, flags)
                matches += 1
        self._mutex.unlock()
        self.search_finished.emit()

    def _update_label_matches(self):
        self.labelMatches.setText("{0} matches".format(self.cpt_occurences))
        color = "#DD0000"
        if self.cpt_occurences:
            color = "#00DD00"
        self.labelMatches.setStyleSheet("color: %s" % color)
        if self.lineEditSearch.text() == "":
            self.labelMatches.clear()

    def _on_search_finished(self):
        self._clear_decorations()
        occurrences = self.get_occurences()
        for occurrence in occurrences:
            deco = self._create_decoration(occurrence[0],
                                           occurrence[1])
            self._decorations.append(deco)
            self.editor.add_decoration(deco)
        self.cpt_occurences = len(occurrences)
        if not self.cpt_occurences:
            self._current_occurrence = -1
        self._update_label_matches()
        self._update_buttons(txt=self.lineEditReplace.text())

    def _reset_stylesheet(self):
        highlight = drift_color(self.editor.palette().window().color())
        stylesheet = self.STYLESHEET % {
            "bck": self.editor.palette().window().color().name(),
            "color": self.editor.palette().windowText().color().name(),
            "highlight": highlight.name()}
        if stylesheet != self._previous_stylesheet:
            self.setStyleSheet(stylesheet)
            self._previous_stylesheet = stylesheet

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        self._reset_stylesheet()

    def _current_occurrence(self):
        self._mutex.lock()
        ret_val = self._current_occurrence
        self._mutex.unlock()
        return ret_val

    def _clear_occurrences(self):
        self._mutex.lock()
        self._occurrences[:] = []
        self._mutex.unlock()

    def _create_decoration(self, selection_start, selection_end):
        """ Creates the text occurences decoration """
        deco = TextDecoration(self.editor.document(), selection_start,
                              selection_end)
        deco.set_background(QtGui.QBrush(self.background))
        deco.set_foreground(QtGui.QBrush(self.foreground))
        deco.draw_order = 1
        return deco

    def _clear_decorations(self):
        """ Remove all decorations """
        for deco in self._decorations:
            self.editor.remove_decoration(deco)
        self._decorations[:] = []

    def _set_current_occurrence(self, cr):
        self._mutex.lock()
        self._current_occurrence = cr
        self._mutex.unlock()

    @staticmethod
    def _compare_cursors(a, b):
        return (a.selectionStart() == b.selectionStart() and
                a.selectionEnd() == b.selectionEnd())

    def _remove_occurrence(self, i, offset=0):
        self._mutex.lock()
        self._occurrences.pop(i)
        if offset:
            updated_occurences = []
            for j, occ in enumerate(self._occurrences):
                if j >= i:
                    updated_occurences.append(
                        (occ[0] + offset, occ[1] + offset))
                else:
                    updated_occurences.append((occ[0], occ[1]))
            self._occurrences = updated_occurences
        self._mutex.unlock()

    def _update_buttons(self, txt=""):
        enable = self.cpt_occurences > 1
        self.pushButtonNext.setEnabled(enable)
        self.pushButtonPrevious.setEnabled(enable)
        self.actionFindNext.setEnabled(enable)
        self.actionFindPrevious.setEnabled(enable)
        enable = (txt != self.lineEditSearch.text() and
                  self.cpt_occurences)
        self.pushButtonReplace.setEnabled(enable)
        self.pushButtonReplaceAll.setEnabled(enable)
