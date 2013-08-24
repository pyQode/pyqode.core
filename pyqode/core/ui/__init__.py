#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
Contains the ui needed by the various widgets. (Resources/Icons are stored in
the rc subdirectory.
"""
import os
import pyqode.qt


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
        pyqode.qt.importRc(rcFile)
    pyqode.qt.loadUi(uiFile, baseInstance)
