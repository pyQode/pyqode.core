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
This modules contains the python specific code completion model.

Python code completion is achieved by the use of the awesome **jedi** library
(https://github.com/davidhalter/jedi)

"""
from collections import deque
from PySide.QtCore import QPoint, Qt, QThread, Signal
from PySide.QtGui import QToolTip, QTextCursor
from jedi.api_classes import CallDef
from jedi import Script
from pcef.core import Mode


class CalltipRequest(object):
    def __init__(self, source_code="", line=0, col=1, filename="", encoding=""):
        self.source_code = source_code
        self.line = line
        self.col = col
        self.filename = filename
        self.encoding = encoding


class PythonCalltipMode(Mode, QThread):
    IDENTIFIER = "Python calltips mode"
    DESCRIPTION = "Provides call tips in python function/methods calls"

    __callResultsAvailable = Signal(CallDef, CalltipRequest)
    __callResultsCollectFailed = Signal()

    def _onStateChanged(self, state):
        if state is True:
            self.editor.codeEdit.keyReleased.connect(self.__onKeyReleased)
            self.__callResultsAvailable.connect(self.__apply_results)
            self.__callResultsCollectFailed.connect(self.__apply_results)
            self.start()
        else:
            self.editor.codeEdit.keyReleased.disconnect(self.__onKeyReleased)
            self.__callResultsAvailable.disconnect(self.__apply_results)
            self.__callResultsCollectFailed.disconnect(self.__apply_results)
            self.__is_running = False
            self.wait()

    def run(self, *args, **kwargs):
        self.__is_running = True
        while self.__is_running:
            if len(self.__request_queue):
                request = self.__request_queue.pop()
                self.__exec_request(request)
            self.msleep(1)

    def __onKeyReleased(self, event):
        if event.key() == Qt.Key_ParenLeft or \
                event.key() == Qt.Key_Comma or \
                event.key() == Qt.Key_Space:
            tc = self.editor.codeEdit.textCursor()
            line = tc.blockNumber() + 1
            col = tc.columnNumber()
            fn = self.editor.codeEdit.tagFilename
            encoding = self.editor.codeEdit.tagEncoding
            source = self.editor.codeEdit.toPlainText()
            self.__request_queue.append(
                CalltipRequest(source_code=source, line=line, col=col,
                               filename=fn, encoding=encoding))
        else:
            QToolTip.hideText()

    def __exec_request(self, request):
        script = Script(request.source_code, request.line, request.col,
                        request.filename, request.encoding)
        try:
            call = script.get_in_function_call()
            if call:
                self.__callResultsAvailable.emit(call, request)
            else:
                self.__callResultsCollectFailed.emit()
        except:
            self.__callResultsCollectFailed.emit()

    def __apply_results(self, call=None, request=None):
            # QToolTip.hideText()
            if call:
                # create a formatted calltip (current index appear in bold)
                calltip = "<nobr>{0}.{1}(".format(
                    call.module.name, call.call_name)
                for i, param in enumerate(call.params):
                    if i != 0:
                        calltip += ", "
                    if i == call.index:
                        calltip += "<b>"
                    calltip += unicode(param.token_list[0])
                    if i == call.index:
                        calltip += "</b>"
                calltip += ')</nobr>'
                # set tool tip position at the start of the bracket
                charWidth = self.editor.codeEdit.fm.width('A')
                w_offset = (request.col - call.bracket_start[1]) * charWidth
                position = QPoint(
                    self.editor.codeEdit.cursorRect().x() - w_offset,
                    self.editor.codeEdit.cursorRect().y())
                position = self.editor.codeEdit.mapToGlobal(position)
                # show tooltip
                QToolTip.showText(position, calltip, self.editor.codeEdit)
            else:
                QToolTip.hideText()

    def __init__(self):
        super(PythonCalltipMode, self).__init__(
            self.IDENTIFIER, self.DESCRIPTION)
        QThread.__init__(self)
        self.__request_queue = deque()
        self.__is_running = False