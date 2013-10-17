#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
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
