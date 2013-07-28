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
Loads ui dynamically from ui file for PyQt4 applications
"""
from PyQt4 import uic


def loadUi(uiFile, baseInstance):
    """
    Load ui using PyQt.uic.loadUi

    :param uiFile: The ui file to load
    :param baseInstance: The base instance which will receive the ui.
    """
    uic.loadUi(uiFile, baseInstance,)
