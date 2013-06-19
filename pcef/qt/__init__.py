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

From the command line using the **--PyQt** or **--PySide** options ::

    python pcef_app.py --PyQt

By settings the QT_API environment variable to "PyQt" or "PySide" at the first
line of your main script::

    import os
    os.environ.setdefault("QT_API", "PyQt")

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
__logger = logging.getLogger("pcef")
import os
import sys
argv = []
try:
    argv = sys.argv
except:
    pass

# check if a qt bindings has already been imported
try:
    from_env = os.environ["QT_API"]
except KeyError:
    from_env = ""
if "PyQt4" in sys.modules or "--PyQt" in argv or from_env == "PyQt":
    os.environ.setdefault("QT_API", "PyQt")
elif "PySide" in sys.modules or "--PySide" in argv or from_env == "PySide":
    os.environ.setdefault("QT_API", "PySide")
else:
    __logger.warning("No qt bindings specified, pcef will pick up one on its "
                     "own...")
    try:
        import PyQt4
    except ImportError:
        # try PyQt
        try:
            import PySide
        except ImportError:
            # Fatal error, no qt bindings found
            __logger.critical("PyQt4 and PySide not found, exiting with "
                              "return code -1")
            print("PyQt4 and PySide not found, exiting with return code -1")
            os.environ.setdefault("QT_API", None)
            sys.exit(-1)
        else:
            os.environ.setdefault("QT_API", "PySide")
    else:
        os.environ.setdefault("QT_API", "PyQt")
    __logger.warning("The chosen qt binding is %s" % os.environ["QT_API"])
__logger.info("Using %s" % os.environ["QT_API"])
# setup PyQt api to version 2
if os.environ["QT_API"] == "PyQt" and sys.version_info[0] == 2:
    import sip
    try:
        sip.setapi("QString", 2)
        sip.setapi("QVariant", 2)
    except:
        __logger.critical("PCEF: failed to set PyQt api to version 2"
                        "\nTo solve this problem, import "
                        "pcef before any other PyQt modules "
                        "in your main script...")