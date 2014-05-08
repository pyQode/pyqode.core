# -*- coding: utf-8 -*-
""" Contains the AutoCompleteMode """
import logging
from pyqode.core.frontend import Mode, text


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
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def _on_state_changed(self, state):
        if state:
            self.editor.post_key_pressed.connect(self._on_post_key_pressed)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.post_key_pressed.disconnect(self._on_post_key_pressed)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_post_key_pressed(self, e):
        if not e.isAccepted():
            txt = e.text()
            next_char = text.get_right_character(self.editor)
            if txt in self.MAPPING:
                to_insert = self.MAPPING[txt]
                if (not next_char or next_char in self.MAPPING.keys() or
                        next_char in self.MAPPING.values() or
                        next_char.isspace()):
                    text.insert_text(self.editor, to_insert)

    def _on_key_pressed(self, e):
        txt = e.text()
        next_char = text.get_right_character(self.editor)
        self.logger.debug('next char: %s' % next_char)
        ignore = False
        if txt and next_char == txt and next_char in self.MAPPING:
            ignore = True
        elif e.text() == ')' or e.text() == ']' or e.text() == '}':
            if next_char == ')' or next_char == ']' or next_char == '}':
                ignore = True
        if ignore:
            e.accept()
            self.logger.debug('clear selection and move right')
            text.clear_selection(self.editor)
            text.move_right(self.editor)
