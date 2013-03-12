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
import sys
from subprocess import Popen, PIPE, STDOUT

from PySide.QtGui import QColor
from PySide.QtCore import Signal, QRunnable, QObject, QThreadPool
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
        self.__decorations = []
        self.__markers = []
        self.base_cmd = base_cmd
        self.checkers_panel = None
        self.colors = {ERROR_TYPE_WARNING: "#FF0000",
                       ERROR_TYPE_SYNTAX: "#FFFF00"}

    def _onStateChanged(self, state):
        if state:
            self.editor.codeEdit.textSaved.connect(self.__run_cmd)
            self.editor.codeEdit.newTextSet.connect(self.__run_cmd)
            if hasattr(self.editor, "checkers_panel"):
                self.checkers_panel = self.editor.checkers_panel
        else:
            self.editor.codeEdit.textSaved.disconnect(self.__run_cmd)
            self.editor.codeEdit.newTextSet.disconnect(self.__run_cmd)
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
        self.__clear_decorations()
        self.__clear_markers()
        current_cursor = self.editor.codeEdit.textCursor()
        hbar_pos = self.editor.codeEdit.horizontalScrollBar().sliderPosition()
        vbar_pos = self.editor.codeEdit.verticalScrollBar().sliderPosition()
        self.onResultsAvailable(raw_results)
        self.editor.codeEdit.setTextCursor(current_cursor)
        self.editor.codeEdit.horizontalScrollBar().setSliderPosition(hbar_pos)
        self.editor.codeEdit.verticalScrollBar().setSliderPosition(vbar_pos)

    def onResultsAvailable(self, raw_results):
        raise NotImplementedError("The checker mode %s does not implement "
                                  "onResultsAvailable" % self.name)

    def __run_cmd(self):
        filename = self.editor.codeEdit.tagFilename
        if filename and self.__thread_pool.maxThreadCount() == 0:
            cmd = "{0} {1}".format(
                self.base_cmd, self.editor.codeEdit.tagFilename)
            runner = RunnableChecker()
            runner.connect(self.__apply_results)
            runner.cmd = cmd
            self.__thread_pool.start(runner)

    def _onStyleChanged(self):
        self.colors[ERROR_TYPE_WARNING] = QColor(
            self.editor.currentStyle.warningColor)
        self.colors[ERROR_TYPE_SYNTAX] = QColor(
            self.editor.currentStyle.errorColor)
        self.__run_cmd()


class PEP8CheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PEP8 results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                offset = 0
                if sys.platform == "win32":
                    offset = 1
                tokens = line.split(':')
                line_nr = int(tokens[1 + offset])
                col_nr = int(tokens[2 + offset])
                message = "PEP8: %s" % tokens[3 + offset]
                self.addError(
                    ERROR_TYPE_WARNING, line_nr, col_nr, message, True)
            except:
                pass

    def __init__(self):
        super(PEP8CheckerMode, self).__init__(
            "PEP8 Checker", "Check python code style using pep8.py",
            base_cmd="pep8")


class PyFlakesCheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PyFlakes results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                tokens = line.split(':')
                nb_tokens = len(tokens)
                line_nr = int(tokens[nb_tokens - 2])
                message = "PyFlakes: %s" % tokens[nb_tokens - 1]
                error_type = ERROR_TYPE_SYNTAX
                # todo properly separate error messages from warning messages
                if "used" in message:
                    error_type = ERROR_TYPE_WARNING
                self.addError(error_type, line_nr, column=1, message=message,
                              selectLine=True)
            except ValueError:
                pass

    def __init__(self):
        super(PyFlakesCheckerMode, self).__init__(
            "PyFlakes Checker", "Checks python syntax errors using pyflakes.py",
            base_cmd="pyflakes")


class PyLintCheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PyFlakes results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                tokens = line.split(':')
                nb_tokens = len(tokens)
                line_nr = int(tokens[nb_tokens - 2])
                message = "PyLint: %s" % tokens[nb_tokens - 1]
                error_type = ERROR_TYPE_SYNTAX
                if "[W" in message:
                    error_type = ERROR_TYPE_WARNING
                self.addError(error_type, line_nr, column=1, message=message,
                              selectLine=True)
            except ValueError:
                pass

    def __init__(self):
        super(PyLintCheckerMode, self).__init__(
            "Pylint Checker", "Checks python syntax errors using pylint.py",
            base_cmd="pylint -f parseable -rn -dC,R")