# -*- coding: utf-8 -*-
"""
This module contains the global style settings for pyqode.core.

QCodeEdit and the core modes/panels will use the values defined in this module
when instantiated to initialise their style related properties.

This make it easy for the user to modify QCodeEdit style globally.
Widgets already instantiated can be refreshed using
:meth:`pyqode.core.editor.QCodeEdit.refresh_style`.

To change a property on a specific editor, use the corresponding python
property on the editor/mode/panel instance.

Example usage::

    from pyqode.core import style

    # white on black editor
    style.background = QColor('black')
    style.foreground = QColor('white')

    # refresh existing editor, new QCodeEdit instance will use the new style
    editor.refresh_style()


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


SymbolMatcherMode options
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: matching_braces_background
.. autodata:: matching_braces_foreground
.. autodata:: not_matching_braces_background
.. autodata:: not_matching_brace_foreground


PygmentsSyntaxHighlighterMode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: pygments_style


RightMarginMode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: right_margin_color


SearchAndReplacePanel
~~~~~~~~~~~~~~~~~~~~~

.. autodata:: search_occurrence_background
.. autodata:: search_occurrence_foreground

"""
from PyQt4.QtGui import QColor

# ----------------
# QCodeEdit
# ---------------

font = None
"""
The font family name. Leave it to None to use a platform specific
font(_monospace_ on GNU/Linux, _Consolas_ on Window and _Monaco_ on Mac).
"""

font_size = 10
"""
The font size. Default is 10
"""

background = QColor('white')
"""
The editor's background color. This value is often overridden by the syntax
highlighter mode. Default is white.

"""

foreground = QColor('black')
"""
The editor's foreground. This value is often overridden by the syntax
highlighter mode. Default is black.
"""

whitespaces_foreground = QColor('light gray')
"""
Color of the whitespaces, use when
:attr:`pyqode.core.settings.show_whitespaces` is set to True.
"""

selection_background = None
"""
The text selection background. Leave it to None to use a platform specific
color (from QPalette)
"""

selection_foreground = None
"""
The text selection foreground. Leave it to None to use a platform specific
color (from QPalette)
"""

caret_line_background = None
"""
The color of the current line. Leave it to None to use a color derived from
the background color.
"""

# ----------------
# SymbolMatcherMode
# ----------------
matching_braces_background = QColor('#B4EEB4')
"""
Background color of matching braces.
"""

matching_braces_foreground = QColor('red')
"""
Foreground color of matching braces.
"""

not_matching_braces_background = QColor('transparent')
"""
Background color of not matching braces.
"""

not_matching_brace_foreground = QColor('red')
"""
Foreground color of not matching braces.
"""


# ----------------
# PygmentsSyntaxHighlighterMode
# ----------------
pygments_style = 'default'
"""
The style used by the pygments syntax highlighter mode. Default is 'default'.
The value must be one of :attr:`pygments.styles.STYLE_MAP`.

"""

# ----------------
# RightMarginMode
# ----------------
right_margin_color = QColor('red')
"""
The color of the right margin.
"""

# ----------------
# Search panel style options
# ----------------
search_occurrence_background = QColor('yellow')
"""
Background color of search occurences. Default is yellow.
"""

search_occurrence_foreground = QColor('black')
"""
Foreground color of search occurences. Default is yellow.
"""
