# -*- coding: utf-8 -*-
"""
This module contains the global default definitions for actions shortcuts
and icons.

It works very much like the settings and style module. QCodeEdit and the core
modes/panels will use the values defined in this module when instantiated.
This make it easy for the user to modify QCodeEdit actions globally.
Widgets already created can be refreshed using
:meth:`pyqode.core.editor.QCodeEdit.refresh_actions`.

Example usage::

    from pyqode.core import actions

    actions.search.text = 'Look for text'
    actions.search.shortcut = 'Ctrl+L'
    actions.search.icon = ':my-icons/my-super-search-icon.png'

    editor.refresh_actions()

QCodeEdit actions
~~~~~~~~~~~~~~~~~

.. autodata:: undo
.. autodata:: redo
.. autodata:: copy
.. autodata:: cut
.. autodata:: paste
.. autodata:: delete
.. autodata:: select_all
.. autodata:: indent
.. autodata:: unindent
.. autodata:: goto_line
.. autodata:: duplicate_line

SearchAndReplacePanel actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: find
.. autodata:: replace
.. autodata:: find_previous
.. autodata:: find_next
.. autodata:: close_search_panel


CaseConverterMode actions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: to_lower
.. autodata:: to_upper

"""
from PyQt4.QtGui import QKeySequence


class Action:
    """
    Utility class used to describe a QAction:
        - text: text of the action (used as QAction text)
        - shortcut: QKeySequence or string used to setup the action shortcut.
        - icon: optional icon associated with the action.

    """
    def __init__(self, text, shortcut='', icon=None):
        """
        :param text: text of the action
        :param shortcut: QKeySequence string associated with the action.
            Optional.
        :param icon: icon associated with the action. This can be a string or
            a tuple of strings to create an action from theme (theme, fallback)
        """
        self.text = text
        self.shortcut = shortcut
        self.icon = icon

    def __repr__(self):
        return ('Action(%r, shortcut=%r icon=%r)' %
                (self.text, self.shortcut, self.icon))

# ----------------
# QCodeEdit actions
# ----------------
undo = Action('Undo', shortcut=QKeySequence.Undo,
              icon=('edit-undo', ':/pyqode-icons/rc/edit-undo.png'))
"""
Undo action. Uses the standard (platform specific) shortcut
"""

redo = Action('Redo', shortcut=QKeySequence.Redo,
              icon=('edit-redo', ':/pyqode-icons/rc/edit-redo.png'))
"""
Redo action. Uses the standard (platform specific) shortcut
"""

copy = Action('Copy', shortcut=QKeySequence.Copy,
              icon=('edit-copy', ":/pyqode-icons/rc/edit-copy.png"))
"""
Copy action. Uses the standard (platform specific) shortcut
"""

cut = Action('Cut', shortcut=QKeySequence.Cut,
             icon=('edit-cut', ":/pyqode-icons/rc/edit-cut.png"))
"""
Cut action. Uses the standard (platform specific) shortcut
"""

paste = Action('Paste', shortcut=QKeySequence.Paste,
               icon=('edit-paste', ':/pyqode-icons/rc/edit-paste.png'))
"""
Paste action. Uses the standard (platform specific) shortcut
"""

delete = Action('Delete', shortcut=QKeySequence.Delete,
                icon=('edit-delete', ':/pyqode-icons/rc/edit-delete.png'))
"""
Delete action. Uses the standard (platform specific) shortcut
"""

select_all = Action('Select all', shortcut=QKeySequence.SelectAll,
                    icon=('edit-select-all',
                          ':/pyqode-icons/rc/edit-select-all.png'))
"""
Select all action. Uses the standard (platform specific) shortcut
"""

indent = Action('Indent', shortcut='Tab',
                icon=('format-indent-more',
                      ':/pyqode-icons/rc/format-indent-more.png'))
"""
Indent action: TAB
"""

unindent = Action('Un-indent', shortcut='Shift+Tab',
                  icon=('format-indent-more',
                        ':/pyqode-icons/rc/format-indent-more.png'))
"""
Unindent action: TAB
"""

goto_line = Action('Go to line', shortcut='Ctrl+G',
                   icon=('start-here', ':/pyqode-icons/rc/goto-line.png'))
"""
Go to line action. CTRL+G.
"""

duplicate_line = Action('Duplicate line', shortcut='Ctrl+D',
                        icon=None)
"""
Duplicate line action: CTRL-D.
"""

# ----------------
# Search panel actions
# ----------------
find = Action('Find', shortcut=QKeySequence.Find,
              icon=('edit-find', ':/pyqode-icons/rc/edit-find.png'))
"""
Find action. Uses the standard (platform specific) shortcut.
"""

replace = Action('Replace', shortcut=QKeySequence.Replace,
                 icon=('edit-find-replace',
                       ':/pyqode-icons/rc/edit-find-replace.png'))
"""
Replace action. Uses the standard (platform specific) shortcut.
"""

find_previous = Action('Find previous', shortcut=QKeySequence.FindPrevious,
                       icon=('go-up', ':/pyqode-icons/rc/go-up.png'))
"""
Find previous occurrence action. Uses the standard (platform specific)
shortcut.
"""

find_next = Action('Find next', shortcut=QKeySequence.FindNext,
                   icon=('go-down', ':/pyqode-icons/rc/go-down.png'))
"""
Find next occurrence action. Uses the standard (platform specific) shortcut.
"""

close_search_panel = Action('Close search panel', shortcut=QKeySequence.Close,
                            icon=('application-exit',
                                  ':/pyqode-icons/rc/close.png'))
"""
Close search panel action. Uses the standard (platform specific) shortcut.
"""


# ----------------
# Case converter actions
# ----------------
to_lower = Action('Convert to lower case', shortcut='Ctrl+U',
                  icon=None)
"""
Convert to lower case action.
"""

to_upper = Action('Convert to UPPER CASE', shortcut='Ctrl+Shift+U',
                  icon=None)
"""
Convert to upper case action.
"""
