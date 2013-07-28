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
import os
import pcef.qt


def loadUi(uiFileName, baseInstance, rcFilename=None):
    """
    Loads an ui file from the ui package and load the specified qrc (must
    already be compiled)

    :param uiFileName: The ui file name (without path)

    :param baseInstance: The baseInstance on which the ui is built

    :param rcFilename: The optional qrc file to load
    """
    uiFile = os.path.join(os.path.abspath(os.path.join(__file__, "..")),
                          uiFileName)
    if rcFilename:
        rcFile = os.path.join(os.path.abspath(os.path.join(__file__, "..")),
                              rcFilename)
        pcef.qt.importRc(rcFile)
    pcef.qt.loadUi(uiFile, baseInstance)