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
This example show how to use pyqode with the PyQt bindings.

For PyQt the most important thing is that you must use the sip API version 2 for
QString and QVariant. You can import some PyQt modules as long as you use the
correct API version::

    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)

The easiest way to use pyqode with PyQt is simply to import pyqode before any PyQt
module (PyQt is automatically selected by default).

**This is only needed for python 2,** python3 bindings already use the new sip
API. With python3 you're free to import any modules in the order you want**
"""
import os
import sys
# tell pyqode to use PyQt4
os.environ['QT_API'] = "PyQt4"
if sys.version_info[0] == 2:
    # With python 2, the order of import matters!
    # You must import a pyqode package or class before PyQt (to automatically
    # set the sip API to version 2)
    import pyqode.core
    # then use PyQt as usually
    from PyQt4.QtGui import QApplication
else:
    # With python3, do as you want :)
    from PyQt4.QtGui import QApplication
    import pyqode.core


def main():
    app = QApplication(sys.argv)
    editor = pyqode.core.QGenericCodeEdit()
    editor.show()
    # show the api pyqode is currently using
    editor.setPlainText("pyQode using %s " % os.environ["QT_API"])
    app.exec_()

if __name__ == "__main__":
    main()

