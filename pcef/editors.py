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
from modes.ident import AutoIndentMode
from pcef.base import QCodeEditor
from pcef.modes.clh import HighlightLineMode
from pcef.modes.margin import RightMarginMode
from pcef.modes.sh import SyntaxHighlighterMode
from pcef.modes.zoom import EditorZoomMode
from pcef.panels.line_numbers import QLineNumberPanel
from pcef.panels.folding import QFoldPanel
from pcef.panels.search_and_replace import QSearchPanel


class QGenericEditor(QCodeEditor):
    """A generic (language independent) code editor widget.
    It comes with the following modes/panels installed:
        - syntax highlighting mode using pygments (see the pygments project for
          the complete list of supported languages)
        - code completion mode (not implemented)
        - right margin mode
        - active line highlighting mode
        - line number panel
        - folding panel (not implemented)
        - document search and replace panel/mode (not implemented)

    It also populates the text edit context menu with a set of default actions.
    (some modes might also add their own menu entry or sub-menus).
    """

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    @property
    def rightMarginMode(self):
        """ Returns the right margin mode instance.
        :return: RightMarginMode
        """
        return self.modes[RightMarginMode.IDENTIFIER]

    @property
    def syntaxHighlightingMode(self):
        """ Returns the syntax hilighting mode instance.
        :return: SyntaxHighlightingMode
        """
        return self.modes[SyntaxHighlighterMode.IDENTIFIER]

    @property
    def highlightLineMode(self):
        """ Returns the highlight active line mode instance.
        :return: HighlightLineMode
        """
        return self.modes[HighlightLineMode.IDENTIFIER]

    @property
    def lineNumberPanel(self):
        """ Returns the line number panel instance.
        :return: QLineNumberPanel
        """
        return self.panels[QLineNumberPanel.IDENTIFIER]

    @property
    def foldPanel(self):
        """ Returns the fold panel instance
        :return: QFoldPanel
        """
        return self.panels[QFoldPanel.IDENTIFIER]

    #---------------------------------------------------------------------------
    # Methods
    #---------------------------------------------------------------------------
    def _installActions(self):
        """ Install generic actions """
        self.textEdit.addAction(self.ui.actionUndo)
        self.textEdit.addAction(self.ui.actionRedo)
        self.textEdit.addSeparator()
        self.textEdit.addAction(self.ui.actionCopy)
        self.textEdit.addAction(self.ui.actionCut)
        self.textEdit.addAction(self.ui.actionPaste)
        self.textEdit.addSeparator()
        self.textEdit.addAction(self.ui.actionSelectAll)
        self.textEdit.addSeparator()
        self.textEdit.addAction(self.ui.actionIndent)
        self.ui.actionUnindent.setShortcut("Shift+Tab")  # unable to set it in
        # the designer
        self.textEdit.addAction(self.ui.actionUnindent)

    def __init__(self, parent=None):
        QCodeEditor.__init__(self, parent)

        # Install actions
        self._installActions()

        # Install modes
        self.installMode(RightMarginMode())
        self.installMode(SyntaxHighlighterMode())
        self.installMode(HighlightLineMode())
        self.installMode(EditorZoomMode())
        self.installMode(AutoIndentMode())

        # Install panels
        self.installPanel(QFoldPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(QLineNumberPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(QSearchPanel(), self.PANEL_ZONE_BOTTOM)

        # Manual slot connections
        self.on_textEdit_redoAvailable(False)
        self.on_textEdit_undoAvailable(False)
        self.ui.textEdit.setUndoRedoEnabled(True)
        self.on_textEdit_copyAvailable(False)

    #---------------------------------------------------------------------------
    # Slots
    #---------------------------------------------------------------------------
    @Slot(bool)
    def on_textEdit_undoAvailable(self, available):
        self.ui.actionUndo.setEnabled(available)

    @Slot(bool)
    def on_textEdit_redoAvailable(self, available):
        self.ui.actionRedo.setEnabled(available)

    @Slot(bool)
    def on_textEdit_copyAvailable(self, available):
        self.ui.actionCopy.setEnabled(available)
        self.ui.actionCut.setEnabled(available)

    @Slot()
    def on_actionUndo_triggered(self):
        self.textEdit.undo()

    @Slot()
    def on_actionRedo_triggered(self):
        self.textEdit.redo()

    @Slot()
    def on_actionPaste_triggered(self):
        self.textEdit.paste()

    @Slot()
    def on_actionCopy_triggered(self):
        self.textEdit.copy()

    @Slot()
    def on_actionCut_triggered(self):
        self.textEdit.cut()

    @Slot()
    def on_actionIndent_triggered(self):
        self.textEdit.indent(self.TAB_SIZE)

    @Slot()
    def on_actionUnindent_triggered(self):
        self.textEdit.unIndent(self.TAB_SIZE)

    @Slot()
    def on_actionSelectAll_triggered(self):
        self.textEdit.selectAll()
