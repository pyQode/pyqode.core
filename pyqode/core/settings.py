# -*- coding: utf-8 -*-
"""
This module exposes global settings for pyqode.core.

CodeEdit and the core modes/panels will use the values defined in this module
when instantiated. This make it easy for the user to modify CodeEdit settings
globally. Widgets already instantiated can be refreshed using
:meth:`pyqode.core.frontend.CodeEdit.refresh_settings`.

Example usage::

    from pyqode.core import settings

    # show whitespaces
    settings.show_white_spaces = True
    # add c++ code completion triggers
    settings.cc_trigger_symbols.append('->', '::')

    # refresh existing editor, new CodeEdit instance will use the new settings
    editor.refresh_settings()


CodeEdit options
~~~~~~~~~~~~~~~~~

.. autodata:: show_white_spaces
.. autodata:: tab_length
.. autodata:: use_spaces_instead_of_tabs
.. autodata:: min_indent_column
.. autodata:: save_on_focus_out
.. autodata:: word_separators
.. autodata:: cc_trigger_key
.. autodata:: cc_trigger_len
.. autodata:: cc_trigger_symbols
.. autodata:: cc_show_tooltips
.. autodata:: cc_case_sensitive
.. autodata:: file_watcher_auto_reload
.. autodata:: right_margin_pos

"""
# pylint: disable=C0103
# ----------------
# CodeEdit settings
# ----------------
#: Specify if visual spaces must be highlighted. Default is False.
#:
#: Requires a call to refresh_settings on existing CodeEdit instance for the
#: change to be propagated.
show_white_spaces = False

#: The number of spaces that defines a tabulation/indentation. Default is 4
#: spaces.
#:
#: Does not require a call to refresh_settings as this setting is read
#: dynamically, as needed
tab_length = 4

#: Tells pyqode to use spaces instead of tabs. Note that tab support is buggy,
#: most of the pyqode modes are using spaces everywhere. Default is True.
#:
#: Does not require a call to refresh_settings as this setting is read
#: dynamically, as needed
use_spaces_instead_of_tabs = True

#: The minimum indent column, useful for languages such as COBOL where all code
#: must starts at a column different than 0. Default is 0.
#:
#: Does not require a call to refresh_settings as this setting is read
#: dynamically, as needed
min_indent_column = 0

#: Automatically saves the editor content to file when the editor loses focus.
#: Default is True.
#
#: Does not require a call to refresh_settings as this setting is read
#: dynamically, as needed.
save_on_focus_out = True

#: The list of word separators used by many modes to detect word under cursor
#: or to split the document words (code completion).
#:
#: Does not require a call to refresh_settings as this setting is read
#: dynamically, as needed.
word_separators = [
    '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{', '}', '|',
    ':', '"', "'", "<", ">", "?", ",", ".", "/", ";", '[', ']', '\\', '\n',
    '\t', '=', '-', ' '
]

# ----------------
# Code completion settings
# ----------------
#: The code completion trigger key: ctrl + KEY. Default is ctrl + space.
cc_trigger_key = ord(' ')  # Qt.Key_Space = ord(' ')


#: The number of characters in the completion prefix required to trigger the
#: code completion engine. Default is 1, the code completion will start as
#: soon as you type.
cc_trigger_len = 1

#: Symbols that trigger the code completion engine automatically. Default is
#: ['.']. Other languages such as C++ might add '->' and '::' to this list.
cc_trigger_symbols = ['.']

#: Tells the code completion to show completion tooltips when available.
#: Default is True.
cc_show_tooltips = True

#: Is the code completion case sensitive? Default is False.
cc_case_sensitive = False

# ----------------
# File watcher settings
# ----------------
#: True to automatically files that changed externally. False to ask the
#: permission to the user (via a message box). Default is False.
file_watcher_auto_reload = False


# ----------------
# Right margin settings
# ----------------
#: Specifies the right margin positon. Default is 79, following the PEP8
#: guidelines.
right_margin_pos = 79
