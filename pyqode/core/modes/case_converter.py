"""
Contains a case converter mode.
"""
import sys
from PyQt4 import QtCore, QtGui
from pyqode.core.editor import Mode
from pyqode.core.api import system


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

    @system.keep_tc_pos
    def to_lower(self, *args):
        tc = self.editor.textCursor()
        tc.insertText(tc.selectedText().lower())
        self.editor.setTextCursor(tc)

    @system.keep_tc_pos
    def to_upper(self, *args):
        tc = self.editor.textCursor()
        tc.insertText(tc.selectedText().upper())
        self.editor.setTextCursor(tc)

    def _create_actions(self):
        self.action_to_lower = QtGui.QAction(self.editor)
        self.action_to_lower.setText("Convert to lower case")
        self.action_to_lower.setShortcut("Ctrl+U")
        self.action_to_lower.triggered.connect(self.to_lower)

        self.action_to_upper = QtGui.QAction(self.editor)
        self.action_to_upper.setText("Convert to UPPER CASE")
        self.action_to_upper.setShortcut("Ctrl+Shift+U")
        self.action_to_upper.triggered.connect(self.to_upper)

        self._actions_created = True

    def _on_state_changed(self, state):
        if state:
            if not self._actions_created:
                self._create_actions()
            self.separator = self.editor.add_separator()
            self.editor.add_action(self.action_to_lower)
            self.editor.add_action(self.action_to_upper)
        else:
            self.editor.remove_action(self.action_to_lower)
            self.editor.remove_action(self.action_to_upper)
            self.editor.remove_action(self.separator)
