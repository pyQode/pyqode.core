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
PCEF is a code editor framework for python qt applications.
"""
__import__('pkg_resources').declare_namespace(__name__)

import logging
__logger = logging.getLogger("pcef")
import os
import sys

#
# PCEF VERSION
#
__version__ = "1.0.0-dev"

# Detect python3
if sys.version_info[0] == 3:
    python3 = True
else:
    python3 = False

#
# configure and exposes qt
#
from pcef.qt import QtCore
from pcef.qt import QtGui
qt_api = os.environ["QT_API"]

from pcef import core

#
# Public api
#
# # -- all
# from pcef import exceptions
# from pcef.constants import PanelPosition
# # -- core
# from pcef.core import QGenericCodeEdit
# from pcef.core import system
# from pcef.core.decoration import TextDecoration
# from pcef.core.editor import QCodeEdit
# from pcef.core.mode import Mode
# from pcef.core.modes import CaretLineHighlighterMode
# from pcef.core.modes import RightMarginMode
# from pcef.core.modes import PygmentsHighlighterMode
# from pcef.core.panel import Panel
# from pcef.core.panels import LineNumberPanel
# from pcef.core.properties import PropertyRegistry
# from pcef.core.system import TextStyle
