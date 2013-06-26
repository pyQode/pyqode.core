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
This package contains the core classes of pcef and an example of a generic
code editor widget
"""
#
# exposes public core api
#
from pcef.core import panels
from pcef.core import modes
from pcef.core import constants
from pcef.core.mode import Mode
from pcef.core.panel import Panel
from pcef.core.editor import QCodeEdit
from pcef.core.panels import LineNumberPanel
from pcef.core.modes import CaretLineHighlighterMode
from pcef.core.modes import RightMarginMode
from pcef.core.modes import ZoomMode
from pcef.core.modes import PygmentsHighlighterMode
from pcef.core.modes import AutoIndentMode
from pcef.core.constants import PanelPosition
from pcef.core.decoration import TextDecoration
from pcef.core.properties import PropertyRegistry
from pcef.core.system import TextStyle


#
# Example of a generic code editor widgey
#
class QGenericCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels.

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
        self.installMode(PygmentsHighlighterMode())
        self.installMode(ZoomMode())
        self.installMode(AutoIndentMode())
