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
Contains pyqode dialogs windows.
"""
from PyQt4 import QtGui
from pyqode.core.ui import dlg_goto_line_ui


class GoToLineDialog(QtGui.QDialog, dlg_goto_line_ui.Ui_Dialog):
    def __init__(self, parent, current_line, line_count):
        QtGui.QDialog.__init__(self, parent)
        dlg_goto_line_ui.Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.spinBox.setValue(current_line)
        self.spinBox.setMaximum(line_count)
        self.lblCurrentLine.setText("%d" % current_line)
        self.lblLineCount.setText("%d" % line_count)
        self.buttonBox.button(self.buttonBox.Ok).setText("Go")
        self.buttonBox.button(self.buttonBox.Cancel).setText(
            "I'm going nowhere")
        self.spinBox.setFocus()

    @classmethod
    def get_line(cls, parent, current_line, line_count):
        dlg = GoToLineDialog(parent, current_line, line_count)
        if dlg.exec_() == dlg.Accepted:
            return dlg.spinBox.value(), True
        return current_line, False
