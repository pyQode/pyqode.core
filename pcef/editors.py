#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains a series of pre-configured editors classes ready to be used in your
PySide application
"""
from PySide.QtCore import Slot

from pcef.core import CodeEditorWidget
from pcef.modes.indent import AutoIndentMode
from pcef.modes.clh import HighlightLineMode
from pcef.modes.margin import RightMarginMode
from pcef.modes.sh import SyntaxHighlighterMode
from pcef.modes.zoom import EditorZoomMode
from pcef.modes.code_completion import CodeCompletionMode
from pcef.panels.line_numbers import QLineNumberPanel
from pcef.panels.folding import QFoldPanel
from pcef.panels.search_and_replace import QSearchPanel


class QGenericEditor(CodeEditorWidget):
    """
    A generic (language independent) pre-configured code editor widget.

    **Installed modes**:

        * :class:`pcef.modes.code_completion.CodeCompletionMode`
        * :class:`pcef.modes.margin.RightMarginMode`
        * :class:`pcef.modes.sh.SyntaxHighlighterMode`
        * :class:`pcef.modes.clh.HighlightLineMode`
        * :class:`pcef.modes.zoom.EditorZoomMode`
        * :class:`pcef.modes.indent.AutoIndentMode`

    **Installed panels**:

        * :class:`pcef.panels.line_numbers.QLineNumberPanel`
        * :class:`pcef.panels.folding.QFoldPanel`
        * :class:`pcef.panels.search_and_replace.QSearchPanel`

    It also populates the text edit context menu with a set of default actions.
    (some modes might also add their own menu entry or sub-menus).
    """

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    @property
    def rightMarginMode(self):
        """
        :returns: the right margin mode instance.
        :rtype: pcef.modes.margin.RightMarginMode
        """
        return self.modes[RightMarginMode.IDENTIFIER]

    @property
    def syntaxHighlightingMode(self):
        """
        :returns: the syntax highlighting mode instance.
        :rtype: pcef.modes.sh.SyntaxHighlighterMod
        """
        return self.modes[SyntaxHighlighterMode.IDENTIFIER]

    @property
    def highlightLineMode(self):
        """
        :returns: the highlight active line mode instance.
        :rtype: pcef.modes.clh.HighlightLineMode
        """
        return self.modes[HighlightLineMode.IDENTIFIER]

    @property
    def zoomMode(self):
        """
        :returns: the editor zoom mode.
        :rtype: pcef.modes.zoom.EditorZoomMode
        """
        return self.modes[EditorZoomMode.IDENTIFIER]

    @property
    def autoIndentMode(self):
        """
        :returns: the editor auto indent mode
        :rtype: pcef.modes.indent.AutoIndentMode
        """
        return self.modes[AutoIndentMode.IDENTIFIER]

    @property
    def codeCompletionMode(self):
        """
        :returns: the code completion mode.
        :rtype: pcef.modes.code_completion.CodeCompletionMode
        """
        return self.modes[CodeCompletionMode.IDENTIFIER]

    @property
    def lineNumberPanel(self):
        """
        :returns: the line number Panel instance.
        :return: pcef.panels.line_numbers.QLineNumberPanel
        """
        return self.panels[QLineNumberPanel.IDENTIFIER]

    @property
    def foldPanel(self):
        """
        returns: the fold Panel instance
        :rtype: pcef.panels.folding.QFoldPanel
        """
        return self.panels[QFoldPanel.IDENTIFIER]

    @property
    def searchPanel(self):
        """
        :returns: the search and replace panel instance

        :return: pcef.panels.search_and_replace.QSearchPanel
        """
        return self.panels[QSearchPanel.IDENTIFIER]

    #---------------------------------------------------------------------------
    # Methods
    #---------------------------------------------------------------------------
    def __init__(self, parent=None):
        CodeEditorWidget.__init__(self, parent)

        # Install actions
        self._installActions()

        # Install panels
        self.installPanel(QFoldPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(QLineNumberPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(QSearchPanel(), self.PANEL_ZONE_BOTTOM)

        # Install modes
        self.installMode(CodeCompletionMode())
        self.installMode(RightMarginMode())
        self.installMode(SyntaxHighlighterMode())
        self.installMode(HighlightLineMode())
        self.installMode(EditorZoomMode())
        self.installMode(AutoIndentMode())

        # Manual slot connections
        self.on_codeEdit_redoAvailable(False)
        self.on_codeEdit_undoAvailable(False)
        self.ui.codeEdit.setUndoRedoEnabled(True)
        self.on_codeEdit_copyAvailable(False)

    def installActions(self):
        self.codeEdit.addAction(self.ui.actionUndo)
        self.codeEdit.addAction(self.ui.actionRedo)
        self.codeEdit.addSeparator()
        self.codeEdit.addAction(self.ui.actionCopy)
        self.codeEdit.addAction(self.ui.actionCut)
        self.codeEdit.addAction(self.ui.actionPaste)
        self.codeEdit.addSeparator()
        self.codeEdit.addAction(self.ui.actionSelectAll)
        self.codeEdit.addSeparator()
        self.codeEdit.addAction(self.ui.actionIndent)
        self.ui.actionUnindent.setShortcut("Shift+Tab")  # unable to set it in
        # the designer
        self.codeEdit.addAction(self.ui.actionUnindent)

    #---------------------------------------------------------------------------
    # Slots
    #---------------------------------------------------------------------------
    @Slot(bool)
    def on_codeEdit_undoAvailable(self, available):
        self.ui.actionUndo.setEnabled(available)

    @Slot(bool)
    def on_codeEdit_redoAvailable(self, available):
        self.ui.actionRedo.setEnabled(available)

    @Slot(bool)
    def on_codeEdit_copyAvailable(self, available):
        self.ui.actionCopy.setEnabled(available)
        self.ui.actionCut.setEnabled(available)

    @Slot()
    def on_actionUndo_triggered(self):
        self.codeEdit.undo()

    @Slot()
    def on_actionRedo_triggered(self):
        self.codeEdit.redo()

    @Slot()
    def on_actionPaste_triggered(self):
        self.codeEdit.paste()

    @Slot()
    def on_actionCopy_triggered(self):
        self.codeEdit.copy()

    @Slot()
    def on_actionCut_triggered(self):
        self.codeEdit.cut()

    @Slot()
    def on_actionIndent_triggered(self):
        self.codeEdit.indent(self.TAB_SIZE)

    @Slot()
    def on_actionUnindent_triggered(self):
        self.codeEdit.unIndent(self.TAB_SIZE)

    @Slot()
    def on_actionSelectAll_triggered(self):
        self.codeEdit.selectAll()
