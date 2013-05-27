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
PCEF is a code editor framework for python qt applications.
"""
import os

#
# PCEF VERSION
#
__version__ = "0.3.0-dev"


#
# configure and exposes qt
#
from pcef import qt
from qt import QtCore
from qt import QtGui
qt_api = os.environ["QT_API"]
print qt_api


#
# Detect features support
#
try:
    from pcef import python
    python_support = True
except ImportError:
    python_support = False
    pass  # python not supported


#
# Public api
#
# -- Core
from pcef import core
from core.editor import QCodeEdit
from core.mode import Mode
from core.panel import Panel
from core.constants import PanelPosition
from core.panels import LineNumberPanel
from core.properties import PropertyRegistry
from core.utils import findSettingsDirectory
# -- Python if python is installed
if python_support:
    pass


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
    editor = QCodeEdit()
    editor.setLineWrapMode(QCodeEdit.NoWrap)
    editor.setWindowTitle("PCEF - Generic Editor")
    editor.installPanel(LineNumberPanel(), PanelPosition.LEFT)
    return editor
