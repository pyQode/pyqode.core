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
Create an abstraction layer over the qt bindings to use.

Requirements
---------------
  - PyQt4 or PySide
  - For PyQt4, you must use the sip API version 2 for QString and QVariant
    otherwise you will be purchased by fanatic vampire killer bees on a deadly
    minefield... :(

Force a specific Qt bindings
-----------------------------

From the command line using the **--PyQt** or **--PySide** options ::

    python pyqode_app.py --PyQt

By settings the QT_API environment variable to "pyqt" or "pyside" at the first
line of your main script::

    import os
    os.environ.setdefault("QT_API", "PyQt")

If nothing is found in sys.arg or in the environment variables, pyQode will try
to detect which API has already been imported by the client code
(be aware of the vampire killer bees if you use PyQt4).

pyQode will choose PyQt if nothing has been specified or imported and if PyQt
is available.

If no qt bindings were found a RuntimeError is raised.

Usage
------------------------
To access the Qt bindings you just need to import pyqode and prefix your
Qt classes by QtGui. ::

    import os
    import sys
    import pyqode


    app = QtGui.QApplication(sys.argv)
    editor = pyqode.QCodeEdit()
    # show the QT api in the window title
    editor.setWindowTitle(os.environ["QT_API"])
    editor.show()
    app.exec_()
"""
import logging
_logger = logging.getLogger("pyqode")
import os
import sys


def read_args():
    """
    Safely read command line args

    :return: sys.argv or empty list
    """
    try:
        argv = sys.argv
    except:
        argv = []
    return [arg.lower() for arg in argv]


def read_env():
    """
    Safely read QT_API env var

    :return: QT_API value
    """
    try:
        from_env = os.environ["QT_API"].lower()
    except KeyError:
        from_env = ""
    return from_env


def check_pyside(argv, env):
    return "PySide" in sys.modules or "--pyside" in argv or env == "pyside"


def try_pyside():
    """
    Tries to import pyside.

    :return: Return True if pyside can be used
    """
    try:
        import PySide
    except ImportError:
        # Fatal error, no qt bindings found
        _logger.critical("PySide not found!")
        return False
    else:
        os.environ["QT_API"] = "PySide"
        return True


def setup_apiv2():
    """
    Setup apiv2 on the chose binding.
    """
    # setup PyQt api to version 2
    if sys.version_info[0] == 2:
        try:
            import sip
            sip.setapi("QString", 2)
            sip.setapi("QVariant", 2)
        except:
            _logger.critical("pyQode: failed to set PyQt api to version 2"
                              "\nTo solve this problem, import "
                              "pyqode before any other PyQt modules "
                              "in your main script...")


def check_pyqt4(argv, env):
    return ("PyQt4" in sys.modules or "--pyqt4" in argv or "--pyqt" in argv
            or env == "pyqt" or env == "pyqt4")


def try_pyqt4():
    """
    Tries to import pyqt and setup sip api v2 in case of success

    :return: Return True if pyqt can be used
    """
    try:
        import PyQt4
    except ImportError:
        # Fatal error, no qt bindings found
        _logger.critical("PyQt not found!")
        return False
    else:
        os.environ["QT_API"] = "PyQt4"
        setup_apiv2()
        return True


def select():
    """
    Selects a qt bindings. The selected qt bindings is set to the
    QT_API environment variable.

    :return: True if a binding could be selected.
    """
    argv = read_args()
    env = read_env()
    if check_pyqt4(argv, env):
        return try_pyqt4()
    elif check_pyside(argv, env):
        return try_pyside()
    else:
        _logger.warning("No qt bindings specified, pyqode will try to pick one "
                         "on its own")
        if not try_pyqt4():
            _logger.warning("Cannot use PyQt, will try PySide")
            return try_pyside()
        _logger.warning("The chosen qt binding is %s" % os.environ["QT_API"])
        return True


#
# Select a qt binding
#
if not select():
    _logger.critical("Failed to find a qt bindings, please install "
                      "PyQt or PySide to user pyqode. Returning with "
                      "error code.")
    raise RuntimeError("No Qt bindings found")
    #sys.exit(-1)
# __logger.debug("Using %s" % os.environ["QT_API"])

from pyqode.qt import QtCore, QtGui
__all__ = ["QtCore", "QtGui"]
