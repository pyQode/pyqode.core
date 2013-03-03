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
import os
from PySide.QtGui import QColor
from subprocess import Popen, PIPE, STDOUT
from PySide.QtCore import QThread, Signal
import sys
from pcef.core import Mode, TextDecoration, cursorForPosition


class CheckerThread(QThread):
    """
    A checker thread launch a process and retrieve its output. A signal is emitted anytime a new output is available.

    The execute method takes a command line to run.
    """
    #: Signal emitted when the result of the command line is available. The signal is emitted with the output string.
    outputAvailable = Signal(str)

    def __init__(self):
        QThread.__init__(self)
        self.__cmd_queue = deque()
        self.is_running = False

    def execute(self, command_line):
        self.__cmd_queue.appendleft(command_line)

    def run(self, *args, **kwargs):
        self.is_running = True
        while self.is_running:
            if len(self.__cmd_queue):
                cmd = self.__cmd_queue.pop()
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                output = p.stdout.read()
                self.outputAvailable.emit(output)
            self.msleep(1)


class Pep8CheckerMode(Mode, CheckerThread):

    def __init__(self):
        super(Pep8CheckerMode, self).__init__("PEP8", "Check for PEP8 violation on the fly")
        CheckerThread.__init__(self)
        self.__decorations = []

    def _onStateChanged(self, state):
        if state:
            self.editor.codeEdit.textSaved.connect(self.__run_pep8)
            self.editor.codeEdit.newTextSet.connect(self.__run_pep8)
            self.outputAvailable.connect(self.__apply_results)
            self.start()
        else:
            self.editor.codeEdit.textSaved.disconnect(self.__run_pep8)
            self.editor.codeEdit.newTextSet.disconnect(self.__run_pep8)
            self.outputAvailable.disconnect(self.__apply_results)
            self.is_running = False
            self.wait()

    def __clear_decorations(self):
        for deco in self.__decorations:
            self.editor.codeEdit.removeDecoration(deco)
        self.__decorations[:] = []

    def __apply_results(self, raw_results):
        """
        Apply squiggle on all lines

        :param raw_results: raw results from pep8.py
        :type raw_results: str
        """
        self.__clear_decorations()
        lines = raw_results.splitlines()
        current_cursor = self.editor.codeEdit.textCursor()
        hbar_pos = self.editor.codeEdit.horizontalScrollBar().sliderPosition()
        vbar_pos = self.editor.codeEdit.verticalScrollBar().sliderPosition()
        for line in lines:
            try:
                offset = 0
                if sys.platform == "win32":
                    offset = 1
                tokens = line.split(':')
                line_nr = int(tokens[1 + offset])
                col_nr = int(tokens[2 + offset])
                message = tokens[3 + offset]
                c = cursorForPosition(self.editor.codeEdit, line_nr, col_nr, selectEndOfLine=True)
                deco = TextDecoration(c, draw_order=1)
                deco.setSpellchecking(color=self.color)
                self.__decorations.append(deco)
                self.editor.codeEdit.addDecoration(deco)
            except:
                pass
        self.editor.codeEdit.setTextCursor(current_cursor)
        self.editor.codeEdit.horizontalScrollBar().setSliderPosition(hbar_pos)
        self.editor.codeEdit.verticalScrollBar().setSliderPosition(vbar_pos)

    def __run_pep8(self):
        cmd = "pep8 %s" % self.editor.codeEdit.tagFilename
        self.execute(cmd)

    def _onStyleChanged(self):
        self.color = QColor(self.editor.currentStyle.warningColor)
        self.__run_pep8()