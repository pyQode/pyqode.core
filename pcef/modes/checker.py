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
"""
Contains the base class for checker modes (syntax,...)
"""
from subprocess import Popen, PIPE, STDOUT

from PySide.QtGui import QColor
from PySide.QtCore import Signal, QRunnable, QObject, QThreadPool, QTimer
from pcef.core import Mode
from pcef.code_edit import TextDecoration, cursorForPosition


class ResultsEvent(QObject):
    signal = Signal(str)


class RunnableChecker(QRunnable):
    # outputAvailable = Signal(str)

    def __init__(self):
        super(RunnableChecker, self).__init__()
        self.cmd = ""
        self.event = ResultsEvent()

    def __del__(self):
        self.event = None

    def connect(self, resultsHandler):
        self.event.signal.connect(resultsHandler)

    def disconnect(self, resultsHandler):
        self.event.signal.disconnect(resultsHandler)

    def run(self, *args, **kwargs):
        p = Popen(self.cmd, shell=True, stdin=PIPE, stdout=PIPE,
                  stderr=STDOUT)
        try:
            output = p.stdout.read()
            if p.stderr:
                output += p.stderr.read()
            self.event.signal.emit(output)
        except IOError:
            pass


#: Checker warning error type (pep8,...)
ERROR_TYPE_WARNING = 0
#: Checker syntax error type (pyflakes,...)
ERROR_TYPE_SYNTAX = 1


class CheckerMode(Mode):

    def __init__(self, name, description, base_cmd):
        super(CheckerMode, self).__init__(name, description)
        self.__thread_pool = QThreadPool()
        self.__thread_pool.setMaxThreadCount(1)
        self.__thread_counter = 0
        self.__timer = QTimer()
        self.__timer.timeout.connect(self._runCmd)
        self.__timer.setInterval(500)
        self.__decorations = []
        self.__markers = []
        self.__canceled = False
        self.base_cmd = base_cmd
        self.checkers_panel = None
        self.colors = {ERROR_TYPE_WARNING: "#FF0000",
                       ERROR_TYPE_SYNTAX: "#FFFF00"}

    def _onStateChanged(self, state):
        if state:
            self.editor.codeEdit.textSaved.connect(self.__onTextChanged)
            self.editor.codeEdit.newTextSet.connect(self.__onTextChanged)
            if hasattr(self.editor, "checkers_panel"):
                self.checkers_panel = self.editor.checkers_panel
        else:
            self.editor.codeEdit.textSaved.disconnect(self.__onTextChanged)
            self.editor.codeEdit.newTextSet.disconnect(self.__onTextChanged)
            self.checkers_panel = None

    def __clear_decorations(self):
        for deco in self.__decorations:
            self.editor.codeEdit.removeDecoration(deco)
        self.__decorations[:] = []

    def __clear_markers(self):
        for marker in self.__markers:
            if self.checkers_panel:
                try:
                    self.checkers_panel.removeMarker(marker)
                except ValueError:
                    pass
        self.__markers[:] = []

    def addError(self, error_type, line, column=1, message=None,
                 selectLine=True):
        assert error_type in self.colors and self.colors[error_type] is not None
        selectLine = selectLine or not column
        c = cursorForPosition(self.editor.codeEdit, line, column,
                              selectEndOfLine=selectLine)
        deco = TextDecoration(c, draw_order=error_type + 1, tooltip=message)
        deco.setSpellchecking(color=QColor(self.colors[error_type]))
        self.__decorations.append(deco)
        self.editor.codeEdit.addDecoration(deco)
        if self.checkers_panel:
            self.__markers.append(
                self.checkers_panel.addCheckerMarker(error_type, line, message))

    def __apply_results(self, raw_results):
        """
        Apply squiggle on all lines

        :param raw_results: raw results from pep8.py
        :type raw_results: str
        """
        # prepare context
        self.__clear_decorations()
        self.__clear_markers()
        current_cursor = self.editor.codeEdit.textCursor()
        hbar_pos = self.editor.codeEdit.horizontalScrollBar().sliderPosition()
        vbar_pos = self.editor.codeEdit.verticalScrollBar().sliderPosition()
        # let specific checkers do the main job
        self.onResultsAvailable(raw_results)
        # restore context
        self.editor.codeEdit.setTextCursor(current_cursor)
        self.editor.codeEdit.horizontalScrollBar().setSliderPosition(hbar_pos)
        self.editor.codeEdit.verticalScrollBar().setSliderPosition(vbar_pos)
        self.__thread_counter -= 1

    def onResultsAvailable(self, raw_results):
        raise NotImplementedError("The checker mode %s does not implement "
                                  "onResultsAvailable" % self.name)

    def _start_runnable(self, runner):
        self.__thread_counter += 1
        self.__thread_pool.start(runner)

    def _runCmd(self):
        self.__timer.stop()
        cmd = "{0} {1}".format(
            self.base_cmd, self.editor.codeEdit.tagFilename)
        runner = RunnableChecker()
        runner.connect(self.__apply_results)
        runner.cmd = cmd
        self._start_runnable(runner)

    def __onTextChanged(self):
        filename = self.editor.codeEdit.tagFilename
        if filename and self.__thread_counter == 0:
            self.__timer.stop()
            self.__timer.start()

    def _onStyleChanged(self):
        self.colors[ERROR_TYPE_WARNING] = QColor(
            self.editor.currentStyle.warningColor)
        self.colors[ERROR_TYPE_SYNTAX] = QColor(
            self.editor.currentStyle.errorColor)
        self.__onTextChanged()

