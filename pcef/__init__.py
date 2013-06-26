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
import logging
__logger = logging.getLogger("pcef")
import os
import sys

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


import pkg_resources
pkg_resources.declare_namespace(__name__)