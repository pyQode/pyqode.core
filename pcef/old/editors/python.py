#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains a pre-configured python editor class ready to be used in your
PySide application.
"""
from pcef.modes.indent import AutoIndentMode
from pcef.modes.python.folder import PyFolderMode
from pcef.modes.python.py_indent import PyAutoIndentMode
from pcef.editors.generic import GenericEditor
from pcef.modes.python.py_cc import PythonCompletionModel
from pcef.modes.python.calltips import PythonCalltipMode
from pcef.modes.python.checkers import PEP8CheckerMode
from pcef.modes.python.checkers import PyFlakesCheckerMode
from pcef.modes.python.checkers import PyLintCheckerMode
from pcef.panels.folding import FoldPanel
from pcef.panels.lines import LineNumberPanel
from pcef.panels.misc import CheckersMarkerPanel
from pcef.panels.search import SearchPanel


class PythonEditor(GenericEditor):
    """
    Extends the Generic editor to add python support:
        - code completion using jedi
        - different background checkers based on pylint, pyflakes and pep8. Checkers are triggered when the editor
          content is saved using pcef.saveFileFromEditor
        - code folder mode (add/remove fold indicator on the fold panel when the text change)
        - smart indenter mode specific to python
    """

    @property
    def checkers_panel(self):
        return self.panel("Checkers marker panel")

    def _installPanels(self):
        self.installPanel(FoldPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(CheckersMarkerPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(LineNumberPanel(), self.PANEL_ZONE_LEFT)
        self.installPanel(SearchPanel(), self.PANEL_ZONE_BOTTOM)

    def _installModes(self):
        super(PythonEditor, self)._installModes()
        self.installMode(PythonCalltipMode())
        self.installMode(PEP8CheckerMode())
        self.installMode(PyFlakesCheckerMode())
        self.installMode(PyLintCheckerMode())
        self.uninstallMode(AutoIndentMode.IDENTIFIER)
        self.installMode(PyAutoIndentMode())
        self.installMode(PyFolderMode())

    def __init__(self, parent=None):
        super(PythonEditor, self).__init__(parent)
        self.codeCompletionMode.addModel(PythonCompletionModel(priority=2))

