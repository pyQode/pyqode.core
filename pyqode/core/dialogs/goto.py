from pyqode.core._forms import dlg_goto_line_ui
from pyqode.qt import QtWidgets

__author__ = 'colin'


class DlgGotoLine(QtWidgets.QDialog, dlg_goto_line_ui.Ui_Dialog):
    """
    Goto line dialog.
    """
    def __init__(self, parent, current_line, line_count):
        QtWidgets.QDialog.__init__(self, parent)
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
        """
        Gets user selected line.

        :returns: tuple(line, status) status is False if the dialog has been
            rejected.
        """
        dlg = DlgGotoLine(parent, current_line, line_count)
        if dlg.exec_() == dlg.Accepted:
            return dlg.spinBox.value(), True
        return current_line, False
