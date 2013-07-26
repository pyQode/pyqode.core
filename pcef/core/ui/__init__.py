#! /usr/bin/env python2.7
# coding: latin-1
# Copyright 2012,
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""
Contains the ui needed by the various widgets. (Resources/Icons are stored in
the rc subdirectory.
"""
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