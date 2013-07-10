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
This module contains the search and replace panel
"""
import sys
import os
usePyQt4 = os.environ['QT_API'] == "PyQt"
usePySide = os.environ['QT_API'] == "PySide"
from pcef.qt import QtCore, QtGui
from pcef.core.decoration import TextDecoration
from pcef.core.system import DelayJobRunner
from pcef.core.panel import Panel


if sys.version_info[0] == 3:
    if usePyQt4:
        from pcef.core.ui.search_panel_ui3_pyqt import Ui_SearchPanel
    elif usePySide:
        from pcef.core.ui.search_panel_ui3_pyside import Ui_SearchPanel
else:
    if usePyQt4:
        from pcef.core.ui.search_panel_ui_pyqt import Ui_SearchPanel
    elif usePySide:
        from pcef.core.ui.search_panel_ui_pyside import Ui_SearchPanel


class SearchAndReplacePanel(Panel, Ui_SearchPanel, DelayJobRunner):
    """
    Search (& replace) Panel. Allow the user to search for content in the editor

    All occurrences are highlighted using text decorations.

    The occurrence under the cursor is selected using the find method of the
    plain text edit. User can go backward and forward.

    The Panel add a few actions to the editor menu(search, replace, next,
    previous, replace, replace all)

    The Panel is shown with ctrl-f for a search, ctrl-r for a search and
    replace.

    The Panel is hidden with ESC or by using the close button (white cross).

    .. note:: The widget use a custom ui designed in Qt Designer
    """
    IDENTIFIER = "searchAndReplacePanel"
    DESCRIPTION = "Search and replace text in the editor"

    #: Stylesheet
    STYLESHEET = """QWidget
    {
        background-color: %(bck)s;
        color: %(color)s;
    }

    QLineEdit
    {
        background-color: %(txt_bck)s;
        border: 1px solid %(highlight)s;
        border-radius: 3px;
    }

    QLineEdit:hover, QLineEdit:focus
    {
        border: 1px solid %(color)s;
        border-radius: 3px;
    }

    QPushButton
    {
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
    }

    QCheckBox:hover
    {
            background-color: %(highlight)s;
            color: %(color)s;
            border-radius: 5px;
    }
    """
    _KEYS = ["panelBackground", "background", "foreground", "panelHighlight"]

    __searchFinished = QtCore.Signal()

    def __init__(self):
        Panel.__init__(self)
        DelayJobRunner.__init__(self, self, nbThreadsMax=1, delay=500)
        Ui_SearchPanel.__init__(self)
        self.setupUi(self)
        self.__separator = None
        self._decorations = []
        self.__searchFinished.connect(self.__onSearchFinished)
        self.mutex = QtCore.QMutex()
        self.__occurrences = []
        self.__current_occurrence = -1
        self.cptMatches = 0
        self.__updateButtons(txt="")
        self.lineEditSearch.installEventFilter(self)
        self.lineEditReplace.installEventFilter(self)

    def install(self, editor):
        Panel.install(self, editor)
        self.__resetStylesheet()
        self.hide()

    def onStyleChanged(self, section, key, value):
        if key in self._KEYS:
            self.__resetStylesheet()

    def onStateChanged(self, state):
        if state:
            self.__separator = self.editor.contextMenu.addSeparator()
            self.editor.contextMenu.addAction(self.actionSearch)
            self.editor.contextMenu.addAction(self.actionActionSearchAndReplace)
            self.editor.contextMenu.addAction(self.actionFindNext)
            self.editor.contextMenu.addAction(self.actionFindPrevious)

            self.editor.textChanged.connect(self.requestSearch)

            self.lineEditSearch.textChanged.connect(self.requestSearch)

            self.checkBoxCase.stateChanged.connect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.connect(self.requestSearch)

            self.pushButtonNext.clicked.connect(self.selectNext)
            self.actionFindNext.triggered.connect(self.selectNext)
            self.pushButtonPrevious.clicked.connect(self.selectPrevious)
            self.actionFindPrevious.triggered.connect(self.selectPrevious)
            self.pushButtonReplace.clicked.connect(self.replaceCurrent)
            self.pushButtonReplaceAll.clicked.connect(self.replaceAll)

            self.lineEditReplace.textChanged.connect(self.__updateButtons)
        else:
            if self.__separator:
                self.editor.contextMenu.removeAction(self.__separator)
            self.editor.contextMenu.removeAction(self.actionSearch)
            self.editor.contextMenu.removeAction(
                self.actionActionSearchAndReplace)
            self.editor.contextMenu.removeAction(self.actionFindNext)
            self.editor.contextMenu.removeAction(self.actionFindPrevious)

            self.editor.textChanged.disconnect(self.requestSearch)
            self.lineEditSearch.textChanged.disconnect(self.requestSearch)
            self.checkBoxCase.stateChanged.disconnect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.disconnect(self.requestSearch)

            self.pushButtonNext.clicked.disconnect(self.selectNext)
            self.actionFindNext.triggered.disconnect(self.selectNext)
            self.pushButtonPrevious.clicked.disconnect(self.selectPrevious)
            self.pushButtonReplace.clicked.disconnect(self.replaceCurrent)
            self.pushButtonReplaceAll.clicked.disconnect(self.replaceAll)

            self.lineEditReplace.textChanged.disconnect(self.__updateButtons)

    @QtCore.Slot()
    def on_pushButtonClose_clicked(self):
        self.hide()
        self.lineEditReplace.clear()
        self.lineEditSearch.clear()

    @QtCore.Slot()
    def on_actionSearch_triggered(self):
        # self.widgetSearch.show()
        # self.widgetReplace.hide()
        # self.show()
        # self.lineEditSearch.setText(self.editor.selectedText())
        # self.lineEditSearch.selectAll()
        # self.lineEditSearch.setFocus()
        self.widgetSearch.show()
        self.widgetReplace.hide()
        self.show()
        newText = self.editor.selectedText()
        oldText = self.lineEditSearch.text()
        textChanged = newText != oldText
        self.lineEditSearch.setText(newText)
        self.lineEditSearch.selectAll()
        self.lineEditSearch.setFocus()
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

    def requestSearch(self, txt=""):
        if txt == "" or isinstance(txt, int):
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

    def selectNext(self):
        cr = self.__getCurrentOccurrence()
        occurrences = self.__getOccurrences()
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
        cr = self.__getCurrentOccurrence()
        occurrences = self.__getOccurrences()
        if (cr == -1 or
                cr == 0):
            cr = len(occurrences) - 1
        else:
            cr -= 1
        self.__setCurrentOccurrence(cr)
        try:
            tc = self.editor.textCursor()
            tc.setPosition(occurrences[0])
            tc.setPosition(occurrences[1], tc.KeepAnchor)
            self.editor.setTextCursor(tc)
            return True
        except IndexError:
            return False

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
        self.mutex.lock()
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
        self.mutex.unlock()
        self.__searchFinished.emit()

    def __updateLabels(self):
        self.labelMatches.setText("{0} matches".format(self.cptMatches))
        color = "#DD0000"
        if self.cptMatches:
            color = "#00DD00"
        self.labelMatches.setStyleSheet("color: %s" % color)

    def __onSearchFinished(self):
        self.__clearDecorations()
        occurrences = self.__getOccurrences()
        for occurrence in occurrences:
            deco = self.__createDecoration(occurrence[0],
                                           occurrence[1])
            self._decorations.append(deco)
            self.editor.addDecoration(deco)
        self.cptMatches = len(occurrences)
        if not self.cptMatches:
            self.__current_occurrence = -1
        elif self.__getCurrentOccurrence() == -1:
            self.selectNext()
        self.__updateLabels()
        self.__updateButtons(txt=self.lineEditReplace.text())

    def __resetStylesheet(self):
        stylesheet = self.STYLESHEET % {
            "bck": self.editor.style.value(self._KEYS[0]).name(),
            "txt_bck": self.editor.style.value(self._KEYS[1]).name(),
            "color": self.editor.style.value(self._KEYS[2]).name(),
            "highlight": self.editor.style.value(self._KEYS[3]).name()}
        self.setStyleSheet(stylesheet)

    def __getOccurrences(self):
        self.mutex.lock()
        retval = []
        for occ in self.__occurrences:
            retval.append(occ)
        self.mutex.unlock()
        return retval

    def __getCurrentOccurrence(self):
        self.mutex.lock()
        retVal = self.__current_occurrence
        self.mutex.unlock()
        return retVal

    def __clearOccurrences(self):
        self.mutex.lock()
        self.__occurrences[:] = []
        self.mutex.unlock()

    def __createDecoration(self, selection_start, selection_end):
        """ Creates the text occurences decoration """
        deco = TextDecoration(self.editor.document(), selection_start,
                              selection_end)
        deco.setBackground(QtGui.QBrush(QtGui.QColor("#FFFF00")))
        deco.setForeground(QtGui.QBrush(QtGui.QColor("#000000")))
        deco.draw_order = 1
        return deco

    def __clearDecorations(self):
        """ Remove all decorations """
        for deco in self._decorations:
            self.editor.removeDecoration(deco)
        self._decorations[:] = []

    def __setCurrentOccurrence(self, cr):
        self.mutex.lock()
        self.__current_occurrence = cr
        self.mutex.unlock()

    def __compareCursors(self, a, b):
        assert isinstance(a, QtGui.QTextCursor)
        assert isinstance(b, QtGui.QTextCursor)
        return (a.selectionStart() == b.selectionStart() and
                a.selectionEnd() == b.selectionEnd())

    def __removeOccurrence(self, i, offset=0):
        self.mutex.lock()
        self.__occurrences.pop(i)
        if offset:
            updated_occurences = []
            for occ in self.__occurrences:
                updated_occurences.append((occ[0] + offset, occ[1] + offset))
            self.__occurrences = updated_occurences
        self.mutex.unlock()

    def replaceCurrent(self, text=None):
        """
        Replaces the selected occurrence by text. µ

        If text is None or bool then the content of lineEditReplace is used.
        """
        if text is None or isinstance(text, bool):
            text = self.lineEditReplace.text()
        cr = self.__getCurrentOccurrence()
        occurrences = self.__getOccurrences()
        if cr == -1:
            self.selectNext()
        try:
            self.editor.textChanged.disconnect(self.requestSearch)
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
            self.cptMatches = len(self.__getOccurrences())
            self.__updateLabels()
            self.__updateButtons()
            return True
        except IndexError:
            return False

    def replaceAll(self):
        remains = self.replaceCurrent()
        while remains:
            remains = self.replaceCurrent()

    def __updateButtons(self, txt=""):
        enable = self.cptMatches > 1
        self.pushButtonNext.setEnabled(enable)
        self.pushButtonPrevious.setEnabled(enable)
        self.actionFindNext.setEnabled(enable)
        self.actionFindPrevious.setEnabled(enable)
        enable = txt != self.lineEditSearch.text() and bool(self.cptMatches)
        self.pushButtonReplace.setEnabled(enable)
        self.pushButtonReplaceAll.setEnabled(enable)