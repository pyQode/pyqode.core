# -*- coding: utf-8 -*-
""" Contains the AutoCompleteMode """
from PyQt4 import QtGui
from pyqode.core.editor import Mode


class AutoCompleteMode(Mode):
    """
    Generic auto complete mode that automatically completes the following
    symbols:

        - " -> "
        - ' -> '
        - ( -> )
        - [ -> ]
        - { -> }
    """
    #: Auto complete mapping, maps input key with completion text.
    MAPPING = {'"': '"', "'": "'", "(": ")", "{": "}", "[": "]"}

    def _on_state_changed(self, state):
        if state:
            self.editor.post_key_pressed.connect(self._on_post_key_pressed)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.post_key_pressed.disconnect(self._on_post_key_pressed)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_post_key_pressed(self, e):
        if e.isAccepted():
            return
        txt = e.text()
        tc = self.editor.textCursor()
        tc.movePosition(QtGui.QTextCursor.WordRight,
                        QtGui.QTextCursor.KeepAnchor)
        next_char = tc.selectedText()
        if len(next_char):
            next_char = next_char[0]
        else:
            next_char = None
        if txt in self.MAPPING:
            to_insert = self.MAPPING[txt]
            if (not next_char or next_char in self.MAPPING.keys() or
                    next_char in self.MAPPING.values() or
                    next_char.isspace()):
                tc = self.editor.textCursor()
                p = tc.position()
                tc.insertText(to_insert)
                tc.setPosition(p)
                self.editor.setTextCursor(tc)

    def _on_key_pressed(self, e):
        txt = e.text()
        tc = self.editor.textCursor()
        tc.movePosition(QtGui.QTextCursor.Right,
                        QtGui.QTextCursor.KeepAnchor)
        try:
            next_char = tc.selectedText()[0]
        except IndexError:
            next_char = ''
        if txt and next_char == txt and next_char in self.MAPPING:
            e.accept()
            tc.clearSelection()
            self.editor.setTextCursor(tc)
            return
        if e.text() == ')' or e.text() == ']' or e.text() == '}':
            tc = self.editor.textCursor()
            tc.movePosition(tc.Right, tc.KeepAnchor, 1)
            if (tc.selectedText() == ')' or tc.selectedText() == ']' or
                    tc.selectedText() == '}'):
                tc.clearSelection()
                self.editor.setTextCursor(tc)
                e.accept()
