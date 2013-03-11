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
Contains a pre-configured python editor class ready to be used in your
PySide application.
"""
from pcef.editors.generic import GenericEditor
from pcef.modes.python.py_cc import PythonCompletionModel
from pcef.modes.python.calltips import PythonCalltipMode
from pcef.modes.python.checkers import PEP8CheckerMode
from pcef.modes.python.checkers import PyFlakesCheckerMode
from pcef.modes.python.checkers import PyLintCheckerMode
from pcef.panels.misc import CheckersMarkerPanel


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

    def __init__(self, parent=None):
        super(PythonEditor, self).__init__(parent)
        self.codeCompletionMode.addModel(PythonCompletionModel(priority=2))
        self.installMode(PythonCalltipMode())
        self.installPanel(CheckersMarkerPanel(), self.PANEL_ZONE_LEFT)
        self.installMode(PEP8CheckerMode())
        self.installMode(PyFlakesCheckerMode())
        self.installMode(PyLintCheckerMode())
