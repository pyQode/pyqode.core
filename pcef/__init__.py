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
import os

#
# PCEF VERSION
#
__version__ = "1.0.0-dev"


#
# configure and exposes qt
#
from pcef import qt
from qt import QtCore
from qt import QtGui
qt_api = os.environ["QT_API"]


#
# Detect features support
#
try:
    from pcef import python
    python_support = True
except ImportError as e:
    print e.message
    python_support = False
    pass  # python not supported
print "Python support", python_support

#
# Public api
#
# -- all
from pcef import exceptions
from constants import PanelPosition
# -- core
from pcef import core
from core import QGenericCodeEdit
from core import system
from core.decoration import TextDecoration
from core.editor import QCodeEdit
from core.mode import Mode
from core.modes import CaretLineHighlighterMode
from core.modes import RightMarginMode
from core.modes import PygmentsHighlighterMode
from core.panel import Panel
from core.panels import LineNumberPanel
from core.properties import PropertyRegistry
# -- python if python is installed
if python_support:
    from pcef import python
    from python import QPythonCodeEdit
    # from python.modes import
    # from python.panels import
