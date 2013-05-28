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
This package contains the core class of pcef
"""
from pcef.core import panels
from pcef.core import modes


#
# Utility functions to get pre-configured editors
#
def genericEditor():
    """
    Gets a pre-configured generic editor.

    **Panels:**
        * line number panel
        * search and replace panel

    **Modes:**
        * document word completion
        * generic syntax highlighter (pygments)
        *

    :rtype: pcef.QCodeEdit
    """
    import pcef
    editor = pcef.QCodeEdit()
    editor.setLineWrapMode(pcef.QCodeEdit.NoWrap)
    editor.setWindowTitle("PCEF - Generic Editor")
    editor.installPanel(pcef.LineNumberPanel(), pcef.PanelPosition.LEFT)
    return editor
