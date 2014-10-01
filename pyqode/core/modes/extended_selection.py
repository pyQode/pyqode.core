"""
This module contains the extended selection mode.
"""
from pyqode.qt import QtCore, QtWidgets, QtGui
from pyqode.core.api import Mode, TextHelper


class ExtendedSelectionMode(Mode):
    """ Adds extended selection capabilities (Ctrl/Alt + Double click).

    This mode adds extended selections capabilities to CodeEdit.

    Extended selection is a feature that can be found in the Ulipad editor:
    https://code.google.com/p/ulipad

    It consists in adding a few shortcuts and contextual action to do some
    smarter selections. This mode adds the following new kind of selections:

        - word selection: select word under cursor
        - extended word selection: select word under cursor including
          continuation characters such as ".".
        - matched selection: select text inside quotes or parenthesis
        - line selection: select the whole line
        - select all: select entire document

    Extended selection and matched selection can be performed by combining
    ctrl or alt with a double click (modifiers are configurable through
    ``extended_sel_modifier`` or ``matched_sel_modifier``).

    """

    def __init__(self):
        super(ExtendedSelectionMode, self).__init__()
        self.extended_sel_modifier = QtCore.Qt.ControlModifier
        self.matched_sel_modifier = QtCore.Qt.AltModifier
        self.continuation_characters = ('.',)
        self.word_sel_shortcut = QtGui.QKeySequence('Ctrl+W')
        self.action_select_word = QtWidgets.QAction(self.editor)
        self.action_select_word.setText('Select word')
        self.action_select_word.setShortcut(self.word_sel_shortcut)
        self.action_select_word.triggered.connect(self.perform_word_selection)

        self.extended_sel_shortcut = QtGui.QKeySequence('Ctrl+Shift+W')
        self.action_select_extended_word = QtWidgets.QAction(self.editor)
        self.action_select_extended_word.setText('Select extended word')
        self.action_select_extended_word.setShortcut(
            self.extended_sel_shortcut)
        self.action_select_extended_word.triggered.connect(
            self.perform_extended_selection)

        self.matched_sel_shortcut = QtGui.QKeySequence('Ctrl+E')
        self.action_select_matched = QtWidgets.QAction(self.editor)
        self.action_select_matched.setText('Matched select')
        self.action_select_matched.setShortcut(self.matched_sel_shortcut)
        self.action_select_matched.triggered.connect(
            self.perform_matched_selection)

        self.line_sel_shortcut = QtGui.QKeySequence('Ctrl+Shift+R')
        self.action_select_line = QtWidgets.QAction(self.editor)
        self.action_select_line.setText('Select line')
        self.action_select_line.setShortcut(self.line_sel_shortcut)
        self.action_select_line.triggered.connect(self.perform_line_selection)

    def create_menu(self):
        # setup menu
        menu = QtWidgets.QMenu(self.editor)
        menu.setTitle('Selection')
        menu.menuAction().setIcon(self.editor.action_select_all.icon())
        # setup actions
        menu.addAction(self.action_select_word)
        menu.addAction(self.action_select_extended_word)
        menu.addAction(self.action_select_matched)
        menu.addAction(self.action_select_line)
        menu.addSeparator()
        menu.addAction(self.editor.action_select_all)
        return menu

    def on_install(self, editor):
        super(ExtendedSelectionMode, self).on_install(editor)
        try:
            self.editor.remove_action(self.editor.action_select_all)
        except ValueError:
            pass
        else:
            self.editor.insert_action(self.create_menu().menuAction(),
                                      self.editor.action_duplicate_line)

    def on_state_changed(self, state):
        if state:
            self.editor.mouse_double_clicked.connect(self._on_double_click)
        else:
            self.editor.mouse_double_clicked.disconnect(self._on_double_click)

    def _on_double_click(self, event):
        modifiers = event.modifiers()
        if modifiers & self.extended_sel_modifier:
            self.editor.textCursor().clearSelection()
            self.perform_extended_selection(event=event)
        elif modifiers & self.matched_sel_modifier:
            # self.editor.textCursor().clearSelection()
            self.perform_matched_selection(event=event)
        elif int(modifiers) == QtCore.Qt.NoModifier:
            self.perform_word_selection(event=event)

    def perform_word_selection(self, event=None):
        self.editor.setTextCursor(
            TextHelper(self.editor).word_under_cursor(True))
        if event:
            event.accept()

    def perform_extended_selection(self, event=None):
        TextHelper(self.editor).select_extended_word(
            continuation_chars=self.continuation_characters)
        if event:
            event.accept()

    def perform_matched_selection(self, event):
        selected = TextHelper(self.editor).match_select()
        if selected and event:
            event.accept()

    def perform_line_selection(self):
        TextHelper(self.editor).select_whole_line()
