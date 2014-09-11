# -*- coding: utf-8 -*-
""" Contains the AutoCompleteMode """
import logging
from pyqode.core.api import TextHelper
from pyqode.core.api.mode import Mode


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

    def __init__(self):
        super(AutoCompleteMode, self).__init__()
        self.logger = logging.getLogger(__name__)
        self._ignore_post = False

    def on_state_changed(self, state):
        if state:
            self.editor.post_key_pressed.connect(self._on_post_key_pressed)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.post_key_pressed.disconnect(self._on_post_key_pressed)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_post_key_pressed(self, event):
        if not event.isAccepted() and not self._ignore_post:
            txt = event.text()
            next_char = TextHelper(self.editor).get_right_character()
            if txt in self.MAPPING:
                to_insert = self.MAPPING[txt]
                if (not next_char or next_char in self.MAPPING.keys() or
                        next_char in self.MAPPING.values() or
                        next_char.isspace()):
                    TextHelper(self.editor).insert_text(to_insert)
        self._ignore_post = False

    def _on_key_pressed(self, event):
        txt = event.text()
        if self.editor.textCursor().hasSelection():
            self._ignore_post = True
            return
        next_char = TextHelper(self.editor).get_right_character()
        self.logger.debug('next char: %s', next_char)
        ignore = False
        if txt and next_char == txt and next_char in self.MAPPING:
            ignore = True
        elif event.text() == ')' or event.text() == ']' or event.text() == '}':
            if next_char == ')' or next_char == ']' or next_char == '}':
                ignore = True
        if ignore:
            event.accept()
            self.logger.debug('clear selection and move right')
            TextHelper(self.editor).clear_selection()
            TextHelper(self.editor).move_right()
