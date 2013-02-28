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
from PySide.QtGui import QColor
from subprocess import Popen, PIPE, STDOUT
from PySide.QtCore import QThread, Signal
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

    def execute(self, command_line):
        self.__cmd_queue.appendleft(command_line)

    def run(self, *args, **kwargs):
        while True:
            if len(self.__cmd_queue):
                cmd = self.__cmd_queue.pop()
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
                self.outputAvailable.emit(output)
            self.msleep(100)


class Pep8CheckerMode(Mode):
    def __init__(self):
        super(Pep8CheckerMode, self).__init__("PEP8", "Check for PEP8 violation on the fly")
        self.__checker_thread = CheckerThread()
        self.__checker_thread.outputAvailable.connect(self.__apply_results)
        self.__checker_thread.start()
        self.__decorations = []

    def _onStateChanged(self, state):
        if state:
            self.editor.codeEdit.textSaved.connect(self.__run_pep8)
            self.editor.codeEdit.newTextSet.connect(self.__run_pep8)
        else:
            self.editor.codeEdit.textSaved.disconnect(self.__run_pep8)
            self.editor.codeEdit.newTextSet.connect(self.__run_pep8)

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
        for line in lines:
            tokens = line.split(':')
            line_nr = int(tokens[1])
            col_nr = int(tokens[2])
            message = tokens[3]
            c = cursorForPosition(self.editor.codeEdit, line_nr, col_nr, selectEndOfLine=True)
            deco = TextDecoration(c, draw_order=1)
            deco.setSpellchecking(color=self.color)
            self.__decorations.append(deco)
            self.editor.codeEdit.addDecoration(deco)
        self.editor.codeEdit.setTextCursor(current_cursor)

    def __run_pep8(self):
        self.__checker_thread.execute("pep8 %s" % self.editor.codeEdit.tagFilename)

    def _onStyleChanged(self):
        self.color = QColor(self.editor.currentStyle.warningColor)
        self.__run_pep8()