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

Python code completion is achieved by the use of the awesome **jedi** library (https://github.com/davidhalter/jedi)
"""
from PySide.QtCore import QPoint, Qt
from PySide.QtGui import QToolTip, QTextCursor
from jedi import Script
from pcef.core import Mode


class PythonCalltipMode(Mode):
    IDENTIFIER = "Python calltips mode"
    DESCRIPTION = "Provides call tips in python function/methods calls"

    def _onStateChanged(self, state):
        if state is True:
            self.editor.codeEdit.keyReleased.connect(self.__onTextChanged)
        else:
            self.editor.codeEdit.keyReleased.disconnect(self.__onTextChanged)

    def __onTextChanged(self, event):
        # don't try to provide calltips when user is scrolling up/down
        # if event.key() == Qt.Key_Down or event.key() == Qt.Key_Up:
        #     QToolTip.hideText()
        #     return

        if event.key() == Qt.Key_ParenLeft or event.key() == Qt.Key_Comma:
            tc = self.editor.codeEdit.textCursor()
            line = tc.blockNumber() + 1
            col = tc.columnNumber()
            fn = self.editor.codeEdit.tagFilename
            encoding = self.editor.codeEdit.tagEncoding
            source = self.editor.codeEdit.toPlainText()
            script = Script(source, line, col, fn, encoding)
            try:
                call = script.get_in_function_call()
            except:
                call = None
            # QToolTip.hideText()
            if call is not None:
                # create a formatted calltip (current index appear in bold)
                calltip = "<nobr>{0}.{1}(".format(call.module.name, call.call_name)
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
                w_offset = (col - call.bracket_start[1]) * charWidth
                position = QPoint(self.editor.codeEdit.cursorRect().x() - w_offset,
                                  self.editor.codeEdit.cursorRect().y())
                position = self.editor.codeEdit.mapToGlobal(position)
                # show tooltip
                QToolTip.showText(position, calltip, self.editor.codeEdit)
            else:
                QToolTip.hideText()

    def __init__(self):
        super(PythonCalltipMode, self).__init__(self.IDENTIFIER, self.DESCRIPTION)