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
This example show the various way to force using the PySide bindings instead
of PyQt4 which is the default.

When using PySide the easiest way is just to import any PySide module/package
before pcef
"""
import os
import sys
# first import something from PySide
from PySide.QtGui import QApplication
# then import any pcef package
import pcef.core


def main():
    app = QApplication(sys.argv)
    editor = pcef.core.QGenericCodeEdit()
    editor.show()
    # show the api pcef is currently using
    editor.setPlainText("PCEF using the %s qt bindings" % os.environ["QT_API"])
    app.exec_()

if __name__ == "__main__":
    main()

