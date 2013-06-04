#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# PCEF
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This package contains python specific modes, panels and editors.
"""
from pcef.python import panels
from pcef.python import modes

from pcef.core.editor import QCodeEdit
from pcef.core.panels import LineNumberPanel
from pcef.core.modes import CaretLineHighlighterMode
from pcef.core.modes import RightMarginMode
from pcef.core.modes import ZoomMode
from pcef.python.modes import PythonHighlighterMode
from pcef.constants import PanelPosition



class QPythonCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels specifics to
    a python code editor widget

    **Panels:**
        * line number panel
        * search and replace panel

    **Modes:**
        * document word completion
        * generic syntax highlighter (pygments)
    """
    def __init__(self, parent=None):
        QCodeEdit.__init__(self, parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("PCEF - Generic Editor")
        self.installPanel(LineNumberPanel(), PanelPosition.LEFT)
        self.installMode(CaretLineHighlighterMode())
        self.installMode(RightMarginMode())
        self.installMode(PythonHighlighterMode(self.document()))
        self.installMode(ZoomMode())
