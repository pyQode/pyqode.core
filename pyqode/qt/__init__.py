#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyQode - Python/Qt Code Editor widget
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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

By settings the QT_API environment variable to "PyQt" or "PySide" at the first
line of your main script::

    import os
    os.environ.setdefault("QT_API", "PyQt")

If nothing is found in sys.arg or in the environment variables, pyQode will try
to detect which API has already been imported by the client code
(be aware of the vampire killer bees if you use PyQt4).

pyQode will choose PyQt if nothing has been specified or imported and if PyQt
is available.

If no qt bindings were found, **the application will exit with return code -1**
and a meaningful log message in the terminal

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
__logger = logging.getLogger("pyqode")
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
    return argv


def read_env():
    """
    Safely read QT_API env var

    :return: QT_API value
    """
    try:
        from_env = os.environ["QT_API"]
    except KeyError:
        from_env = ""
    return from_env


def try_pyside():
    """
    Tries to import pyside.

    :return: Return True if pyside can be used
    """
    try:
        import PySide
    except ImportError:
        # Fatal error, no qt bindings found
        __logger.critical("PySide not found!")
        return False
    else:
        os.environ.setdefault("QT_API", "PySide")
        return True


def setup_apiv2():
    """
    Setup apiv2 on the chose binding.
    """
    # setup PyQt api to version 2
    if sys.version_info[0] == 2:
        import sip
        try:
            sip.setapi("QString", 2)
            sip.setapi("QVariant", 2)
        except:
            __logger.critical("pyQode: failed to set PyQt api to version 2"
                              "\nTo solve this problem, import "
                              "pyqode before any other PyQt modules "
                              "in your main script...")


def try_pyqt():
    """
    Tries to import pyqt and setup sip api v2 in case of success

    :return: Return True if pyqt can be used
    """
    try:
        import PyQt4
    except ImportError:
        # Fatal error, no qt bindings found
        __logger.critical("PyQt not found!")
        return False
    else:
        os.environ.setdefault("QT_API", "PyQt")
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
    if "PyQt4" in sys.modules or "--PyQt" in argv or env == "PyQt":
        os.environ.setdefault("QT_API", "PyQt")
        return try_pyqt()
    elif "PySide" in sys.modules or "--PySide" in argv or env == "PySide":
        os.environ.setdefault("QT_API", "PySide")
        return try_pyside()
    else:
        __logger.warning("No qt bindings specified, pyqode will try to pick one "
                         "on its own")
        if not try_pyqt():
            __logger.warning("Cannot use PyQt, will try PySide")
            return try_pyside()
        __logger.warning("The chosen qt binding is %s" % os.environ["QT_API"])
        return True


#
# Select a qt binding
#
if not select():
    __logger.critical("Failed to find a qt bindings, please install "
                      "PyQt or PySide to user pyqode. Returning with "
                      "error code -1")
    sys.exit(-1)
__logger.debug("Using %s" % os.environ["QT_API"])

from pyqode.qt import QtCore, QtGui
from pyqode.qt.ui import loadUi, importRc
__all__ = ["QtCore", "QtGui", "loadUi", "importRc"]
