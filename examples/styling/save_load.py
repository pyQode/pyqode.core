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
This example show how to save and load a PropertyRegistry (style or settings).

We will use two QCodeEdit. For the first, we will change change some style
properties to create a simple dark style that we will save to a file.

We will then load this file to setup the style of the second editor instance.

(The file is saved to user home directory and deleted when the application
terminate.
"""
import os
import sys
from pyqode.qt import QtGui
import pyqode.core


def main():
    app = QtGui.QApplication(sys.argv)

    # this is the path the file that will contains our modified style.
    file_path = os.path.join(os.path.expanduser("~"), "dark_style.json")

    # Editor 01: change its style than save it to a file
    editor_01 = pyqode.core.QCodeEdit()
    editor_01.setWindowTitle("Editor 01")
    editor_01.style.setValue("background", "#222222")
    editor_01.style.setValue("foreground", "#888888")
    editor_01.style.save(file_path)
    print(editor_01.style.dump())
    editor_01.show()

    # Editor 02: style loaded from the file we just saved
    editor_02 = pyqode.core.QCodeEdit()
    editor_02.setWindowTitle("Editor 02")
    editor_02.style.open(file_path)
    editor_02.show()

    # not needed anymore
    os.remove(file_path)

    # run
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
