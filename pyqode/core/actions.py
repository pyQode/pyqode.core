# -*- coding: utf-8 -*-
"""
This module contains the global default definitions for actions shortcuts
and icons.

It works very much like the settings and style module. CodeEdit and the core
modes/panels will use the values defined in this module when instantiated.
This make it easy for the user to modify CodeEdit actions globally.
Widgets already created can be refreshed using
:meth:`pyqode.core.frontend.CodeEdit.refresh_actions`.

Example usage::

    from pyqode.core import actions

    actions.search.text = 'Look for text'
    actions.search.shortcut = 'Ctrl+L'
    actions.search.icon = ':my-icons/my-super-search-icon.png'

    editor.refresh_actions()

CodeEdit actions
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
from PyQt5 import QtGui, QtWidgets
# pylint: disable=C0103


class Action:
    """
    Utility class used to describe a QAction:
        - text: text of the action (used as QAction text)
        - shortcut: QtGui.QKeySequence or string used to setup the action
          shortcut.
        - icon: optional icon associated with the action.

    """
    def __init__(self, text, shortcut='', icon=('', '')):
        """
        :param text: text of the action
        :param shortcut: QtGui.QKeySequence string associated with the action.
            Optional.
        :param icon: icon associated with the action. This can be a string or
            a tuple of strings to create an action from theme (theme, fallback)
        """
        self.text = text
        self.shortcut = shortcut
        self.icon = icon

    def make_icon(self):
        """ Make an icon from the action icon definition """
        if isinstance(self.icon, tuple):
            theme, icon = self.icon
            return QtGui.QIcon.fromTheme(theme, QtGui.QIcon(icon))
        else:
            QtGui.QIcon(self.icon)

    def make_action(self, parent):
        """ Make a QAction out of the action properties """
        a = QtWidgets.QAction(parent)
        a.setText(self.text)
        a.setShortcut(self.shortcut)
        if self.icon:
            a.setIcon(self.make_icon())
        return a

    def __repr__(self):
        return ('Action(%r, shortcut=%r icon=%r)' %
                (self.text, self.shortcut, self.icon))

# ----------------
# CodeEdit actions
# ----------------
#: Undo action. Uses the standard (platform specific) shortcut
undo = Action('Undo', shortcut=QtGui.QKeySequence.Undo,
              icon=('edit-undo', ':/pyqode-icons/rc/edit-undo.png'))

#: Redo action. Uses the standard (platform specific) shortcut
redo = Action('Redo', shortcut=QtGui.QKeySequence.Redo,
              icon=('edit-redo', ':/pyqode-icons/rc/edit-redo.png'))

#: Copy action. Uses the standard (platform specific) shortcut
copy = Action('Copy', shortcut=QtGui.QKeySequence.Copy,
              icon=('edit-copy', ":/pyqode-icons/rc/edit-copy.png"))

#: Cut action. Uses the standard (platform specific) shortcut
cut = Action('Cut', shortcut=QtGui.QKeySequence.Cut,
             icon=('edit-cut', ":/pyqode-icons/rc/edit-cut.png"))

#: Paste action. Uses the standard (platform specific) shortcut
paste = Action('Paste', shortcut=QtGui.QKeySequence.Paste,
               icon=('edit-paste', ':/pyqode-icons/rc/edit-paste.png'))

#: Delete action. Uses the standard (platform specific) shortcut
delete = Action('Delete', shortcut=QtGui.QKeySequence.Delete,
                icon=('edit-delete', ':/pyqode-icons/rc/edit-delete.png'))

#: Select all action. Uses the standard (platform specific) shortcut
select_all = Action('Select all', shortcut=QtGui.QKeySequence.SelectAll,
                    icon=('edit-select-all',
                          ':/pyqode-icons/rc/edit-select-all.png'))

#: Indent action: TAB
indent = Action('Indent', shortcut='Tab',
                icon=('format-indent-more',
                      ':/pyqode-icons/rc/format-indent-more.png'))

#: Unindent action: TAB
unindent = Action('Un-indent', shortcut='Shift+Tab',
                  icon=('format-indent-more',
                        ':/pyqode-icons/rc/format-indent-more.png'))

#: Go to line action. CTRL+G.
goto_line = Action('Go to line', shortcut='Ctrl+G',
                   icon=('start-here', ':/pyqode-icons/rc/goto-line.png'))

#: Duplicate line action: CTRL-D.
duplicate_line = Action('Duplicate line', shortcut='Ctrl+D',
                        icon=None)

# ----------------
# Search panel actions
# ----------------
#: Find action. Uses the standard (platform specific) shortcut.
find = Action('Find', shortcut=QtGui.QKeySequence.Find,
              icon=('edit-find', ':/pyqode-icons/rc/edit-find.png'))

#: Replace action. Uses the standard (platform specific) shortcut.
replace = Action('Replace', shortcut=QtGui.QKeySequence.Replace,
                 icon=('edit-find-replace',
                       ':/pyqode-icons/rc/edit-find-replace.png'))

#: Find previous occurrence action. Uses the standard (platform specific)
#: shortcut.
find_previous = Action('Find previous',
                       shortcut=QtGui.QKeySequence.FindPrevious,
                       icon=('go-up', ':/pyqode-icons/rc/go-up.png'))

#: Find next occurrence action. Uses the standard (platform specific) shortcut.
find_next = Action('Find next', shortcut=QtGui.QKeySequence.FindNext,
                   icon=('go-down', ':/pyqode-icons/rc/go-down.png'))

#: Close search panel action. Uses the standard (platform specific) shortcut.
close_search_panel = Action('Close search panel',
                            shortcut=QtGui.QKeySequence.Close,
                            icon=('application-exit',
                                  ':/pyqode-icons/rc/close.png'))

# ----------------
# Case converter actions
# ----------------
#: Convert to lower case action.
to_lower = Action('Convert to lower case', shortcut='Ctrl+U',
                  icon=None)

#: Convert to upper case action.
to_upper = Action('Convert to UPPER CASE', shortcut='Ctrl+Shift+U',
                  icon=None)
