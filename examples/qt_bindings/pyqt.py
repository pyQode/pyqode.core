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
if sys.version_info[0] == 2:
    # With python 2, the order of import matters!
    # Import a pyqode package or class before PyQt to force the SIP API to version
    #  2 automatically
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
    editor.setPlainText("pyQode using the %s qt bindings" % os.environ["QT_API"])
    app.exec_()

if __name__ == "__main__":
    main()

