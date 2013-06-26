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
This example show how to use pcef with the PyQt bindings.

For PyQt the most important thing is that you must use the sip API version 2 for
QString and QVariant. You can import some PyQt modules as long as you use the
correct API version::

    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)

The easiest way to use pcef with PyQt is simply to import pcef before any PyQt
module (PyQt is automatically selected by default).

**This is only needed for python 2,** python3 bindings already use the new sip
API. With python3 you're free to import any modules in the order you want**
"""
import os
import sys
if sys.version_info[0] == 2:
    # With python 2, the order of import matters!
    # Import a pcef package or class before PyQt to force the SIP API to version
    #  2 automatically
    import pcef.core
    # then use PyQt as usually
    from PyQt4.QtGui import QApplication
else:
    # With python3, do as you want :)
    from PyQt4.QtGui import QApplication
    import pcef.core


def main():
    app = QApplication(sys.argv)
    editor = pcef.core.QCodeEdit()
    editor.show()
    # show the api pcef is currently using
    editor.setPlainText("PCEF using the %s qt bindings" % os.environ["QT_API"])
    app.exec_()

if __name__ == "__main__":
    main()

