# -*- coding: utf-8 -*-
"""
Contains a case converter mode.
"""
from PyQt4 import QtCore, QtGui

from pyqode.core import actions
from pyqode.core.frontend import Mode, text


class CaseConverterMode(Mode):
    """
    Converts selected text to lower case or UPPER case.

    It does so by append two new menu entries to the editor's context menu:
      - *Convert to lower case*: ctrl-u
      - *Convert to UPPER CASE*: ctrl+shift+u
    """
    def __init__(self):
        Mode.__init__(self)
        self._actions_created = False

    @QtCore.pyqtSlot()
    def to_upper(self, *args):
        text.selected_text_to_upper(self.editor)

    @QtCore.pyqtSlot()
    def to_lower(self, *args):
        text.selected_text_to_lower(self.editor)

    def _create_actions(self):
        self.action_to_lower = QtGui.QAction(self.editor)
        self.action_to_lower.triggered.connect(self.to_lower)
        self.action_to_upper = QtGui.QAction(self.editor)
        self.action_to_upper.triggered.connect(self.to_upper)
        self._actions_created = True
        self.refresh_actions()

    def refresh_actions(self):
        self.action_to_lower.setText(actions.to_lower.text)
        self.action_to_lower.setShortcut(actions.to_upper.shortcut)
        self.action_to_upper.setText(actions.to_upper.text)
        self.action_to_upper.setShortcut(actions.to_upper.shortcut)

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
