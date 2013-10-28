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
Bindings independant QtCore module
"""
import os
try:
    if os.environ['QT_API'] == 'PyQt4':
        from PyQt4.QtCore import *
        from PyQt4.Qt import Qt
        from PyQt4.QtCore import pyqtSignal as Signal
        from PyQt4.QtCore import pyqtSlot as Slot
        from PyQt4.QtCore import pyqtProperty as Property
        from PyQt4.QtCore import QT_VERSION_STR as __version__
    else:
        import PySide.QtCore
        __version__ = PySide.QtCore.__version__
        from PySide.QtCore import *
except TypeError:
    class Qt(object):
        blue = None
        red = None

    class QObject(object):
        pass

    class Signal(object):
        def __init__(self, *args):
            pass

    class Slot(object):
        def __init__(self, *args):
            pass

        def __call__(self, *args, **kwargs):
            pass

    class QThread(object):
        pass

    class QEvent(object):
        @staticmethod
        def Type(foo):
            pass

        @staticmethod
        def registerEventType():
            pass

    def qRegisterResourceData(*args):
        pass

    class QRegExp(object):
        pass

    class Property(object):
        def __init__(self, *args, **kwargs):
            pass