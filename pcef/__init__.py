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
except ImportError:
    python_support = False
    pass  # python not supported


#
# Public api
#
from pcef import exceptions
# -- Core
from pcef import core
from core.editor import QCodeEdit
from core import QGenericCodeEdit
from core.mode import Mode
from core.panel import Panel
from constants import PanelPosition
from core.panels import LineNumberPanel
from core.properties import PropertyRegistry
from core import utils
# -- Python if python is installed
if python_support:
    pass
