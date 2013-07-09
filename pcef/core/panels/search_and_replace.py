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
from pcef.core import constants
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
        self.cptMatches = 0
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
            self.editor.textChanged.connect(self.requestSearch)
            self.lineEditSearch.textChanged.connect(self.requestSearch)
            self.checkBoxCase.stateChanged.connect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.connect(self.requestSearch)
        else:
            if self.__separator:
                self.editor.contextMenu.removeAction(self.__separator)
            self.editor.contextMenu.removeAction(self.actionSearch)
            self.editor.contextMenu.removeAction(
                self.actionActionSearchAndReplace)
            self.editor.textChanged.disconnect(self.requestSearch)
            self.lineEditSearch.textChanged.disconnect(self.requestSearch)
            self.checkBoxCase.stateChanged.disconnect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.disconnect(self.requestSearch)

    @QtCore.Slot()
    def on_pushButtonClose_clicked(self):
        self.hide()

    @QtCore.Slot()
    def on_actionSearch_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.hide()
        self.show()
        self.lineEditSearch.setText(self.editor.selectedText())
        self.lineEditSearch.selectAll()
        self.lineEditSearch.setFocus()

    @QtCore.Slot()
    def on_actionActionSearchAndReplace_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.show()
        self.show()
        self.lineEditSearch.setText(self.editor.selectedText())
        self.lineEditReplace.setText(self.editor.selectedText())
        self.lineEditReplace.selectAll()
        self.lineEditReplace.setFocus()

    @QtCore.Slot(str)
    def requestSearch(self, txt=""):
        if txt == "" or isinstance(txt, int):
            txt = self.lineEditSearch.text()
        if txt:
            self.requestJob(self.__execSearch, txt, self.editor.document().clone(),
                            self.__getUserSearchFlag())
        else:
            self.cancelRequests()
            self.stopJob()
            self.__clearOccurrences()
            self.__onSearchFinished()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if (event.key() == QtCore.Qt.Key_Tab or
                    event.key() == QtCore.Qt.Key_Backtab):
                return True
            elif (event.key() == QtCore.Qt.Key_Return or
                    event.key() == QtCore.Qt.Key_Enter):
                if obj == self.lineEditReplace:
                    print("Replace current selection")
                elif obj == self.lineEditSearch:
                    print("Search next")
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

    def __execSearch(self, text, doc, flags):
        self.mutex.lock()
        self.__occurrences[:] = []
        if text:
            cptMatches = 0
            cursor = doc.find(text, 0, flags)
            while not cursor.isNull():
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
            deco = self.__createDecoration(occurrence[0], occurrence[1])
            self._decorations.append(deco)
            self.editor.addDecoration(deco)
        self.cptMatches = len(occurrences)
        self.__updateLabels()

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
        for start, stop in self.__occurrences:
            retval.append((start, stop))
        self.mutex.unlock()
        return retval

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
        return deco

    def __clearDecorations(self):
        """ Remove all decorations """
        for deco in self._decorations:
            self.editor.removeDecoration(deco)
        self._decorations[:] = []
