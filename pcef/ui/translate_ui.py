#! /usr/bin/env python2.7
# coding: latin-1
#-------------------------------------------------------------------------------
# Copyright 2012, DTM
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
#-------------------------------------------------------------------------------
"""
This script call the pyside ui compiler on all ui files found in the cwd.
(It also compile the qrc files to *_rc.py)
"""
import glob
import os

# compile ui files
for name in glob.glob("*.ui"):
    base = name.split(".")[0]
    pyside_cmd = "pyside-uic {0} > {1}_ui.py".format(name, base)
    print pyside_cmd
    os.system(pyside_cmd)

for name in glob.glob("*.qrc"):
    base = name.split(".")[0]
    pyside_cmd = "pyside-rcc {0} > {1}_rc.py".format(name, base)
    print pyside_cmd
    os.system(pyside_cmd)


