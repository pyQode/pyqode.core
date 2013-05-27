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
Detects the qt bindings to use (PyQt4 or PySide)

If a specific qt bindings has already been imported or is specified in sys.argv,
PCEF will use this bindings.
Else PCEF will first try to import and use PyQt4, if it fails it will
attempt to import and use PySide.

You can force to use one specific bindings by appending ["--pyside"] or
["--pyqt"] to sys.argv::

    # force the use of pyside:
    import sys
    sys.argv += ["--pyside"]
    import pcef  # will use pyside


The qt package is automatically imported when importing pcef which other
application to write qt bindings independant applications::

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
if "PyQt4" in sys.modules or "--pyqt" in sys.argv:
    os.environ.setdefault("QT_API", "pyqt")
elif "PySide" in sys.modules or "--pyside" in sys.argv:
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
        logging.critical("PCEF: failed to set pyqt api to version 2, exiting "
                         "with return code -1.\nTo solve this problem, import "
                         "pcef before any other PyQt modules "
                         "in your main script...")
        sys.exit(-1)