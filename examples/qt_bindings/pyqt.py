#!/usr/bin/env python2
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
correct API version.

The best way to use pcef with PyQt is simply to import pcef before any PyQt
module (PyQt is automatically selected by default).
"""
import sys
# first import pcef, this will choose PyQt by default and setup the correct sip
# API.
# We could force PyQt by setting up the QT_API env var or by importing PyQt4
# only before pcef::
#   import os
#   os.environ.setdefault("QT_API", "PyQt")
# or::
#   import PyQt4
import pcef.core
# then use PyQt as usually
from PyQt4.QtGui import QApplication


def main():
    app = QApplication(sys.argv)
    editor = pcef.core.QCodeEdit()
    editor.show()
    # show the api pcef is currently using
    editor.setPlainText("PCEF using the %s qt bindings" % pcef.qt_api)
    app.exec_()

if __name__ == "__main__":
    main()

