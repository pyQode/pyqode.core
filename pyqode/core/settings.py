# -*- coding: utf-8 -*-
"""
This module expose the global settings for pyqode.core.

QCodeEdit and the core modes/panels will use the values defined in this module
when instantiated. This make it easy for the user to modify QCodeEdit settings
globally. Widgets already instantiated can be refreshed using
:meth:`pyqode.core.editor.QCodeEdit.refresh_settings`.

Example usage::

    from pyqode.core import settings

    # show whitespaces
    settings.show_white_spaces = True
    # add c++ code completion triggers
    settings.cc_trigger_symbols.append('->', '::')

    # refresh existing editor, new QCodeEdit instance will use the new settings
    editor.refresh_settings()


QCodeEdit options
~~~~~~~~~~~~~~~~~

.. autodata:: font
.. autodata:: font_size
.. autodata:: background
.. autodata:: foreground
.. autodata:: whitespaces_foreground
.. autodata:: selection_background
.. autodata:: selection_foreground
.. autodata:: caret_line_background
"""
# ----------------
# QCodeEdit settings
# ----------------
show_white_spaces = False
"""
Specify if visual spaces must be highlighted. Default is False

"""

tab_length = 4
"""
The number of spaces that defines a tabulation/indentation. Default is 4
spaces.

"""
use_spaces_instead_of_tabs = True
"""
Tells pyqode to use spaces instead of tabs. Note that tab support is buggy,
most of the pyqode modes are using spaces everywhere. Default is True.

"""

min_indent_column = 0
"""
The minimum indent column, useful for languages such as COBOL where all code
must starts at a column different than 0. Default is 0.

"""

save_on_focus_out = True
"""
Automatically saves the editor content to file when the editor loses focus.
Default is True.

"""

word_separators = [
    '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{', '}', '|',
    ':', '"', "'", "<", ">", "?", ",", ".", "/", ";", '[', ']', '\\', '\n',
    '\t', '=', '-', ' '
]
"""
The list of word separators used by many modes to detect word under cusros or
to split the document words (code completion).

"""

# ----------------
# Code completion settings
# ----------------
cc_trigger_key = ord(' ')  # Qt.Key_Space = ord(' ')
"""
The code completion trigger key: ctrl + KEY. Default is ctrl + space.
"""

cc_trigger_len = 1
"""
The number of characters in the completion prefix required to trigger the code
completion engine. Default is 1, the code completion will start as soon as you
type.
"""

cc_trigger_symbols = ['.']
"""
Symbols that trigger the code completion engine automatically. Default is
['.']. Other languages such as C++ might add '->' and '::' to this list.
"""

cc_show_tooltips = True
"""
Tells the code completion to show completion tooltips when available. Default
is True.
"""

cc_case_sensitive = False
"""
Is the code completion case sensitive? Default is False.
"""

# ----------------
# File watcher settings
# ----------------
file_watcher_auto_reload = False
"""
True to automatically files that changed externally. False to ask the
permission to the user (via a message box). Default is False.
"""

# ----------------
# Right margin settings
# ----------------
right_margin_pos = 79
"""
Specifies the right margin positon. Default is 79, following the PEP8
guidelines.
"""
