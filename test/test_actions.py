# -*- coding: utf-8 -*-
"""
Test scripts for the actions module.
"""
from PyQt5 import QtWidgets, QtGui
from pyqode.core import actions

from .helpers import preserve_actions


@preserve_actions
def test_actions(editor):
    assert actions.delete.shortcut == QtGui.QKeySequence.Delete
    actions.delete.shortcut = 'Ctrl+D'
    adelete = None
    for action in editor.actions():
        if action.text() == 'Delete':
            adelete = action
            break
    if adelete:
        assert adelete.shortcut() == QtGui.QKeySequence.Delete
    editor.refresh_actions()
    if adelete:
        assert adelete.shortcut() == 'Ctrl+D'
