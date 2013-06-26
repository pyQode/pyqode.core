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
This example show the various way to force using the PySide bindings instead
of PyQt4 which is the default.

When using PySide the easiest way is just to import any PySide module/package
before pcef
"""
import sys
# first something from PySide, here the mandatory QApplication
from PySide.QtGui import QApplication
# then import pcef
import pcef


def main():
    app = QApplication(sys.argv)
    editor = pcef.core.QCodeEdit()
    editor.show()
    # show the api pcef is currently using
    editor.setPlainText("PCEF using the %s qt bindings" % pcef.qt_api)
    app.exec_()

if __name__ == "__main__":
    main()

