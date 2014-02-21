"""
Contains a case converter mode.
"""
import sys
from pyqode.qt import QtCore, QtGui
from pyqode.core.mode import Mode


class CaseConverterMode(Mode):
    """
    Converts selected text to lower case or UPPER case.

    It does so by append two new menu entries to the editor's context menu:
      - *Convert to lower case*: ctrl-u
      - *Convert to UPPER CASE*: ctrl+shift+u
    """
    IDENTIFIER = "caseConverterMode"
    DESCRIPTION = __doc__

    def __init__(self):
        Mode.__init__(self)
        self._actions_created = False

    def toLower(self):
        tc = self.editor.textCursor()
        tc.insertText(tc.selectedText().lower())
        self.editor.setTextCursor(tc)

    def toUpper(self):
        tc = self.editor.textCursor()
        tc.insertText(tc.selectedText().upper())
        self.editor.setTextCursor(tc)

    def _create_actions(self):
        self.aToLower = QtGui.QAction(self.editor)
        self.aToLower.setText("Convert to lower case")
        self.aToLower.setShortcut("Ctrl+U")
        self.aToLower.triggered.connect(self.toLower)

        self.aToUpper = QtGui.QAction(self.editor)
        self.aToUpper.setText("Convert to UPPER CASE")
        self.aToUpper.setShortcut("Ctrl+Shift+U")
        self.aToUpper.triggered.connect(self.toUpper)

        self._actions_created = True

    def _onStateChanged(self, state):
        if state:
            if not self._actions_created:
                self._create_actions()
            self.separator = self.editor.addSeparator()
            self.editor.addAction(self.aToLower)
            self.editor.addAction(self.aToUpper)
        else:
            self.editor.removeAction(self.aToLower)
            self.editor.removeAction(self.aToUpper)
            self.editor.removeAction(self.separator)

