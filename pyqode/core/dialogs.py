"""
Contains pyqode dialogs windows.
"""
from pyqode.qt import QtGui
from pyqode.core.ui import dlg_goto_line_ui


class GoToLineDialog(QtGui.QDialog, dlg_goto_line_ui.Ui_Dialog):
    def __init__(self, parent, currentLine, lineCount):
        QtGui.QDialog.__init__(self, parent)
        dlg_goto_line_ui.Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.spinBox.setValue(currentLine)
        self.spinBox.setMaximum(lineCount)
        self.lblCurrentLine.setText("%d" % currentLine)
        self.lblLineCount.setText("%d" % lineCount)
        self.buttonBox.button(self.buttonBox.Ok).setText("Go")
        self.buttonBox.button(self.buttonBox.Cancel).setText("I'm going nowhere")

    @classmethod
    def getLine(cls, parent, currentLine, lineCount):
        dlg = GoToLineDialog(parent, currentLine, lineCount)
        if dlg.exec_() == dlg.Accepted:
            return dlg.spinBox.value(), True
        return currentLine, False



