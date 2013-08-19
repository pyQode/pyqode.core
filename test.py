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
This is a simple test script to that is meant to be run by Travis CI to ensure
everything works properly foreach bindings on each supported python
version (2.7, 3.2).

It runs a QApplication and shows a QGenericCodeEdit for 500ms.
"""
import sys
from pyqode.qt import QtCore, QtGui
from pyqode.core import QGenericCodeEdit


def leave():
    app = QtGui.QApplication.instance()
    app.exit(0)


def main():
    app = QtGui.QApplication(sys.argv)
    editor = QGenericCodeEdit()
    editor.openFile(__file__)
    editor.show()
    QtCore.QTimer.singleShot(500, leave)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
