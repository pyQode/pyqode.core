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
Bindings independant QtGui module
"""
import os
try:
    if os.environ['QT_API'] == 'PyQt4':
        from PyQt4.QtGui import *
    else:
        from PySide.QtGui import *
except TypeError:

    class QColor(object):
        def __init__(self, *args, **kwargs):
            pass

    class QTextEdit(object):
        class ExtraSelection(object):
            pass

    class QPlainTextEdit(object):
        pass

    class QPaintEvent(object):
        pass

    class QKeyEvent(object):
        pass

    class QMouseEvent(object):
        pass

    class QWheelEvent(object):
        pass

    class QFocusEvent(object):
        pass

    class QWidget(object):
        pass

    class QTextBlockUserData(object):
        pass

    class QSyntaxHighlighter(object):
        pass

    class QTextCursor(object):
        pass

    class QTextBlock(object):
        pass

    class QTextDocument(object):
        pass

    class QTextCharFormat(object):
        pass

    class QFont(object):
        pass

    class QTableWidget(object):
        pass

    class QIcon(object):
        pass

    class Foo(object):
        pass

    class QTextEdit(object):
        ExtraSelection = Foo
        pass

    class QColor(object):
        def __init__(self, *args, **kwargs):
            pass

    class QDialog(object):
        pass

    class QTabBar(object):
        pass

    class QTabWidget:
        pass
