#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
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

From the command line using the **--pyside** or **--pyqt** options ::

    python pcef_app.py --pyqt

By settings the QT_API environment variable to "pyside" or "pyqt" at the first
line of your main script::

    import os
    os.environ.setdefault("QT_API", "pyside")

If nothing is found in sys.arg or in the environment variables, PCEF will try
to detect which API has already been imported by the client code
(be aware of the vampire killer bees if you use PyQt4).

PCEF will choose PyQt if nothing has been specified or imported and if PyQt
is available.

If no qt bindings were found, **the application will exit with return code -1**
and a meaningful log message in the terminal

Usage
------------------------
To access the Qt bindings you just need to import pcef and prefix your
Qt classes by pcef.QtGui. ::

    import os
    import sys
    import pcef


    app = pcef.QtGui.QApplication(sys.argv)
    editor = pcef.QCodeEdit()
    # show the QT api in the window title
    editor.setWindowTitle(os.environ["QT_API"])
    editor.show()
    app.exec_()
"""
import logging
import os
import sys
# check if a qt bindings has already been imported
try:
    from_env = os.environ["QT_API"]
except KeyError:
    from_env = ""
if "PyQt4" in sys.modules or "--pyqt" in sys.argv or from_env == "pyqt":
    os.environ.setdefault("QT_API", "pyqt")
elif "PySide" in sys.modules or "--pyside" in sys.argv or from_env == "pyside":
    os.environ.setdefault("QT_API", "pyside")
else:
    logging.warning("PCEF: no qt bindings were already imported...")
    try:
        import PyQt4
    except ImportError:
        # try pyside
        try:
            import PySide
        except ImportError:
            # Fatal error, no qt bindings found
            logging.critical("PCEF: PyQt4 and PySide not found, exiting with "
                             "return code -1")
            print "PCEF: Nore PyQt4 and nore PySide not found, exiting with " \
                  "return code -1"
            os.environ.setdefault("QT_API", None)
            sys.exit(-1)
        else:
            os.environ.setdefault("QT_API", "pyside")
    else:
        os.environ.setdefault("QT_API", "pyqt")
    logging.warning("PCEF: will use %s" % os.environ["QT_API"])
logging.info("PCEF: using %s" % os.environ["QT_API"])
# setup pyqt api to version 2
if os.environ["QT_API"] == "pyqt":
    import sip
    try:
        sip.setapi("QString", 2)
        sip.setapi("QVariant", 2)
    except:
        logging.critical("PCEF: failed to set pyqt api to version 2"
                         "\nTo solve this problem, import "
                         "pcef before any other PyQt modules "
                         "in your main script...")