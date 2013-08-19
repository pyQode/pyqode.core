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
This example show the various way to force using the PySide bindings instead
of PyQt4 which is the default.

When using PySide the easiest way is just to import any PySide module/package
before pyqode
"""
import os
import sys
# first import something from PySide
from PySide.QtGui import QApplication
# then import any pyqode package
import pyqode.core


def main():
    app = QApplication(sys.argv)
    editor = pyqode.core.QGenericCodeEdit()
    editor.show()
    # show the api pyqode is currently using
    editor.setPlainText("pyQode using the %s qt bindings" % os.environ["QT_API"])
    app.exec_()

if __name__ == "__main__":
    main()

