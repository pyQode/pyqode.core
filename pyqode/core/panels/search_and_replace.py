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
This module contains the search and replace panel
"""
from pyqode.qt import QtCore, QtGui
from pyqode.core import constants
from pyqode.core.decoration import TextDecoration
from pyqode.core.panel import Panel
from pyqode.core.system import DelayJobRunner, driftColor
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
    :attr:`searchFinished`.

    The results of the search can then be retrieved using
    :attr:`cptOccurrences` and :meth:`getOccurrences`.

    The client code may now navigate through occurrences using :meth:`selectNext`
    or :meth:`selectPrevious`, or replace the occurrences with a specific
    text using :meth:`replaceOccurrence` or :meth:`replaceAll`.

    Here the properties added by the mode to
    :attr:`pyqode.core.QCodeEdit.style`:

    =========================== ====================== ======= ====================== =====================
    Key                         Section                Type    Default value          Description
    =========================== ====================== ======= ====================== =====================
    searchOccurrenceBackground  General                QColor  #FFFF00                Search occurrences background. Default is Yellow.
    searchOccurrenceForeground  General                QColor  #000000                Search occurrences foreground. Default is Black.
    =========================== ====================== ======= ====================== =====================
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
    searchFinished = QtCore.Signal()

    @property
    def background(self):
        return self.editor.style.value("searchOccurrenceBackground")

    @background.setter
    def background(self, value):
        self.editor.setValue("searchOccurrenceBackground", value)

    @property
    def foreground(self):
        return self.editor.style.value("searchOccurrenceForeground")

    @foreground.setter
    def foreground(self, value):
        self.editor.setValue("searchOccurrenceForeground", value)

    def __init__(self):
        Panel.__init__(self)
        DelayJobRunner.__init__(self, self, nbThreadsMax=1, delay=500)
        Ui_SearchPanel.__init__(self)
        self.setupUi(self)

        #: Occurrences counter
        self.cptOccurrences = 0
        self.__previousStylesheet = ""
        self.__separator = None
        self.__decorations = []
        self.__mutex = QtCore.QMutex()
        self.__occurrences = []
        self.__current_occurrence = -1
        self.__updateButtons(txt="")
        self.lineEditSearch.installEventFilter(self)
        self.lineEditReplace.installEventFilter(self)
        findIcon = QtGui.QIcon.fromTheme(
            "edit-find", QtGui.QIcon(":/pyqode-icons/rc/edit-find.png"))
        replaceIcon = QtGui.QIcon.fromTheme(
            "edit-find-replace",
            QtGui.QIcon(":/pyqode-icons/rc/edit-find-replace.png"))
        nextIcon = QtGui.QIcon.fromTheme(
            "go-down", QtGui.QIcon(":/pyqode-icons/rc/go-down.png"))
        previousIcon = QtGui.QIcon.fromTheme(
            "go-up", QtGui.QIcon(":/pyqode-icons/rc/go-up.png"))
        closeIcon = QtGui.QIcon.fromTheme(
            "application-exit", QtGui.QIcon(":/pyqode-icons/rc/close.png"))
        self.actionSearch.setIcon(findIcon)
        self.labelSearch.setPixmap(findIcon.pixmap(16, 16))
        self.actionActionSearchAndReplace.setIcon(replaceIcon)
        self.labelReplace.setPixmap(replaceIcon.pixmap(16, 16))
        self.actionFindNext.setIcon(nextIcon)
        self.pushButtonNext.setIcon(nextIcon)
        self.actionFindPrevious.setIcon(previousIcon)
        self.pushButtonPrevious.setIcon(previousIcon)
        self.pushButtonClose.setIcon(closeIcon)

    def _onInstall(self, editor):
        Panel._onInstall(self, editor)
        self.__resetStylesheet()
        self.on_pushButtonClose_clicked()
        self.editor.style.addProperty("searchOccurrenceBackground",
                                      constants.SEARCH_OCCURRENCES_BACKGROUND)
        self.editor.style.addProperty("searchOccurrenceForeground",
                                      constants.SEARCH_OCCURRENCES_FOREGROUND)

    def _onStyleChanged(self, section, key):
        Panel._onStyleChanged(self, section, key)
        if key in self._KEYS or not key:
            self.__resetStylesheet()
        if not key or key in ["searchOccurrenceBackground",
                              "searchOccurrenceForeground"]:
            self._refreshDecorations()

    def _refreshDecorations(self):
        for d in self.__decorations:
            self.editor.removeDecoration(d)
            d.setBackground(QtGui.QBrush(self.background))
            d.setForeground(QtGui.QBrush(self.foreground))
            self.editor.addDecoration(d)

    def _onStateChanged(self, state):
        Panel._onStateChanged(self, state)
        if state:
            # add menus
            self.__separator = self.editor.addSeparator()
            self.editor.addAction(self.actionSearch)
            self.editor.addAction(self.actionActionSearchAndReplace)
            self.editor.addAction(self.actionFindNext)
            self.editor.addAction(self.actionFindPrevious)
            # requestSearch slot
            self.editor.textChanged.connect(self.requestSearch)
            self.lineEditSearch.textChanged.connect(self.requestSearch)
            self.checkBoxCase.stateChanged.connect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.connect(self.requestSearch)
            # navigation slots
            self.pushButtonNext.clicked.connect(self.selectNext)
            self.actionFindNext.triggered.connect(self.selectNext)
            self.pushButtonPrevious.clicked.connect(self.selectPrevious)
            self.actionFindPrevious.triggered.connect(self.selectPrevious)
            # replace slots
            self.pushButtonReplace.clicked.connect(self.replaceCurrent)
            self.pushButtonReplaceAll.clicked.connect(self.replaceAll)
            # internal updates slots
            self.lineEditReplace.textChanged.connect(self.__updateButtons)
            self.searchFinished.connect(self.__onSearchFinished)
        else:
            # remove menus
            if self.__separator is not None:
                self.editor.removeAction(self.__separator)
            self.editor.removeAction(self.actionSearch)
            self.editor.removeAction(
                self.actionActionSearchAndReplace)
            self.editor.removeAction(self.actionFindNext)
            self.editor.removeAction(self.actionFindPrevious)
            # requestSearch slot
            self.editor.textChanged.disconnect(self.requestSearch)
            self.lineEditSearch.textChanged.disconnect(self.requestSearch)
            self.checkBoxCase.stateChanged.disconnect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.disconnect(self.requestSearch)
            # navigation slots
            self.pushButtonNext.clicked.disconnect(self.selectNext)
            self.actionFindNext.triggered.disconnect(self.selectNext)
            self.pushButtonPrevious.clicked.disconnect(self.selectPrevious)
            # replace slots
            self.pushButtonReplace.clicked.disconnect(self.replaceCurrent)
            self.pushButtonReplaceAll.clicked.disconnect(self.replaceAll)
            # internal updates slots
            self.lineEditReplace.textChanged.disconnect(self.__updateButtons)
            self.searchFinished.connect(self.__onSearchFinished)

    def closePanel(self):
        """
        Closes the panel
        """
        self.hide()
        self.lineEditReplace.clear()
        self.lineEditSearch.clear()

    @QtCore.Slot()
    def on_pushButtonClose_clicked(self):
        self.closePanel()

    @QtCore.Slot()
    def on_actionSearch_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.hide()
        self.show()
        newText = self.editor.selectedText()
        oldText = self.lineEditSearch.text()
        textChanged = newText != oldText
        self.lineEditSearch.setText(newText)
        self.lineEditSearch.selectAll()
        self.lineEditSearch.setFocus()
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        if not textChanged:
            self.requestSearch(newText)

    @QtCore.Slot()
    def on_actionActionSearchAndReplace_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.show()
        self.show()
        newText = self.editor.selectedText()
        oldText = self.lineEditSearch.text()
        textChanged = newText != oldText
        self.lineEditSearch.setText(newText)
        self.lineEditReplace.clear()
        self.lineEditReplace.setFocus()
        if not textChanged:
            self.requestSearch(newText)

    def focusOutEvent(self, event):
        self.stopJob()
        self.cancelRequests()
        Panel.focusOutEvent(self, event)

    def requestSearch(self, txt=None):
        """
        Requests a search operation.

        :param txt: The text to replace. If None, the content of lineEditSearch
                    is used instead.
        """
        if txt is None or isinstance(txt, int):
            txt = self.lineEditSearch.text()
        if txt:
            self.requestJob(self.__execSearch, True,
                            txt, self.editor.document().clone(),
                            self.editor.textCursor(),
                            self.__getUserSearchFlag())
        else:
            self.cancelRequests()
            self.stopJob()
            self.__clearOccurrences()
            self.__onSearchFinished()

    def getOccurrences(self):
        """
        Returns the list of text occurrences.

        An occurrence is a tuple that contains start and end positions.

        :return: List of tuple(int, int)
        """
        self.__mutex.lock()
        retval = []
        for occ in self.__occurrences:
            retval.append(occ)
        self.__mutex.unlock()
        return retval

    def selectNext(self):
        """
        Selects the next occurrence.

        :return: True in case of success, false if no occurrence could be
                 selected.
        """
        cr = self.__getCurrentOccurrence()
        occurrences = self.getOccurrences()
        if (cr == -1 or
                cr == len(occurrences) - 1):
            cr = 0
        else:
            cr += 1
        self.__setCurrentOccurrence(cr)
        try:
            tc = self.editor.textCursor()
            tc.setPosition(occurrences[cr][0])
            tc.setPosition(occurrences[cr][1], tc.KeepAnchor)
            self.editor.setTextCursor(tc)
            return True
        except IndexError:
            return False

    def selectPrevious(self):
        """
        Selects previous occurrence.

        :return: True in case of success, false if no occurrence could be
                 selected.
        """
        cr = self.__getCurrentOccurrence()
        occurrences = self.getOccurrences()
        if (cr == -1 or
                cr == 0):
            cr = len(occurrences) - 1
        else:
            cr -= 1
        self.__setCurrentOccurrence(cr)
        try:
            tc = self.editor.textCursor()
            tc.setPosition(occurrences[cr][0])
            tc.setPosition(occurrences[cr][1], tc.KeepAnchor)
            self.editor.setTextCursor(tc)
            return True
        except IndexError:
            return False

    def replaceCurrent(self, text=None):
        """
        Replaces the selected occurrence.

        :param text: The replacement text. If it is None, the lineEditReplace's
                     text is used instead.

        :return True if the text could be replace properly, False if there is
                no more occurrences to replace.
        """
        if text is None or isinstance(text, bool):
            text = self.lineEditReplace.text()
        cr = self.__getCurrentOccurrence()
        occurrences = self.getOccurrences()
        if cr == -1:
            self.selectNext()
        try:
            try:
                self.editor.textChanged.disconnect(self.requestSearch)
            except RuntimeError:
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
            self.editor.textChanged.connect(self.requestSearch)
            # prevent search request due to editor textChanged
            self.__removeOccurrence(cr, offset)
            cr -= 1
            self.__setCurrentOccurrence(cr)
            self.selectNext()
            self.cptOccurrences = len(self.getOccurrences())
            self.__updateLabels()
            self.__updateButtons()
            return True
        except IndexError:
            return False

    def replaceAll(self, text=None):
        """
        Replaces all occurrences in the editor's document.

        :param text: The replacement text. If None, the content of the lineEdit
                     replace will be used instead
        """
        remains = self.replaceCurrent(text=text)
        while remains:
            remains = self.replaceCurrent(text=text)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if (event.key() == QtCore.Qt.Key_Tab or
                    event.key() == QtCore.Qt.Key_Backtab):
                return True
            elif (event.key() == QtCore.Qt.Key_Return or
                    event.key() == QtCore.Qt.Key_Enter):
                if obj == self.lineEditReplace:
                    if event.modifiers() & QtCore.Qt.ControlModifier:
                        self.replaceAll()
                    else:
                        self.replaceCurrent()
                elif obj == self.lineEditSearch:
                    self.selectNext()
                return True
            elif event.key() == QtCore.Qt.Key_Escape:
                self.on_pushButtonClose_clicked()
        return Panel.eventFilter(self, obj, event)

    def __getUserSearchFlag(self):
        """ Returns the user search flag """
        searchFlag = QtGui.QTextDocument.FindFlags(0)
        if self.checkBoxCase.isChecked():
            searchFlag |= QtGui.QTextDocument.FindCaseSensitively
        if self.checkBoxWholeWords.isChecked():
            searchFlag |= QtGui.QTextDocument.FindWholeWords
        return searchFlag

    def __execSearch(self, text, doc, originalCursor, flags):
        self.__mutex.lock()
        self.__occurrences[:] = []
        self.__current_occurrence = -1
        if text:
            cptMatches = 0
            cursor = doc.find(text, 0, flags)
            while not cursor.isNull():
                if self.__compareCursors(cursor, originalCursor):
                    self.__current_occurrence = cptMatches
                self.__occurrences.append((cursor.selectionStart(),
                                          cursor.selectionEnd()))
                cursor.setPosition(cursor.position() + 1)
                cursor = doc.find(text, cursor, flags)
                cptMatches += 1
        self.__mutex.unlock()
        self.searchFinished.emit()

    def __updateLabels(self):
        self.labelMatches.setText("{0} matches".format(self.cptOccurrences))
        color = "#DD0000"
        if self.cptOccurrences:
            color = "#00DD00"
        self.labelMatches.setStyleSheet("color: %s" % color)
        if self.lineEditSearch.text() == "":
            self.labelMatches.clear()

    def __onSearchFinished(self):
        self.__clearDecorations()
        occurrences = self.getOccurrences()
        for occurrence in occurrences:
            deco = self.__createDecoration(occurrence[0],
                                           occurrence[1])
            self.__decorations.append(deco)
            self.editor.addDecoration(deco)
        self.cptOccurrences = len(occurrences)
        if not self.cptOccurrences:
            self.__current_occurrence = -1
        self.__updateLabels()
        self.__updateButtons(txt=self.lineEditReplace.text())

    def __resetStylesheet(self):
        highlight = driftColor(self.editor.palette().window().color())
        stylesheet = self.STYLESHEET % {
            "bck": self.editor.palette().window().color().name(),
            "color": self.editor.palette().windowText().color().name(),
            "highlight": highlight.name()}
        if stylesheet != self.__previousStylesheet:
            self.setStyleSheet(stylesheet)
            self.__previousStylesheet = stylesheet

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        self.__resetStylesheet()

    def __getCurrentOccurrence(self):
        self.__mutex.lock()
        retVal = self.__current_occurrence
        self.__mutex.unlock()
        return retVal

    def __clearOccurrences(self):
        self.__mutex.lock()
        self.__occurrences[:] = []
        self.__mutex.unlock()

    def __createDecoration(self, selection_start, selection_end):
        """ Creates the text occurences decoration """
        deco = TextDecoration(self.editor.document(), selection_start,
                              selection_end)
        deco.setBackground(QtGui.QBrush(self.background))
        deco.setForeground(QtGui.QBrush(self.foreground))
        deco.draw_order = 1
        return deco

    def __clearDecorations(self):
        """ Remove all decorations """
        for deco in self.__decorations:
            self.editor.removeDecoration(deco)
        self.__decorations[:] = []

    def __setCurrentOccurrence(self, cr):
        self.__mutex.lock()
        self.__current_occurrence = cr
        self.__mutex.unlock()

    @staticmethod
    def __compareCursors(a, b):
        return (a.selectionStart() == b.selectionStart() and
                a.selectionEnd() == b.selectionEnd())

    def __removeOccurrence(self, i, offset=0):
        self.__mutex.lock()
        self.__occurrences.pop(i)
        if offset:
            updated_occurences = []
            for j, occ in enumerate(self.__occurrences):
                if j >= i:
                    updated_occurences.append(
                        (occ[0] + offset, occ[1] + offset))
                else:
                    updated_occurences.append((occ[0], occ[1]))
            self.__occurrences = updated_occurences
        self.__mutex.unlock()

    def __updateButtons(self, txt=""):
        enable = self.cptOccurrences > 1
        self.pushButtonNext.setEnabled(enable)
        self.pushButtonPrevious.setEnabled(enable)
        self.actionFindNext.setEnabled(enable)
        self.actionFindPrevious.setEnabled(enable)
        enable = (txt != self.lineEditSearch.text() and
                  bool(self.cptOccurrences))
        self.pushButtonReplace.setEnabled(enable)
        self.pushButtonReplaceAll.setEnabled(enable)
