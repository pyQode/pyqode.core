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
This example show how to save and load a PropertyRegistry (style or settings).

We will use two QCodeEdit. For the first, we will change change some style
properties to create a simple dark style that we will save to a file.

We will then load this file to setup the style of the second editor instance.

(The file is saved to user home directory and deleted when the application
terminate.
"""
import os
import sys
import pcef


def main():
    app = pcef.QtGui.QApplication(sys.argv)

    # this is the path the file that will contains our modified style.
    file_path = os.path.join(os.path.expanduser("~"), "dark_style.json")

    # Editor 01: change its style than save it to a file
    editor_01 = pcef.QCodeEdit()
    editor_01.setWindowTitle("Editor 01")
    editor_01.style.setValue("background", "#222222")
    editor_01.style.setValue("foreground", "#888888")
    editor_01.style.save(file_path)
    print(editor_01.style.dump())
    editor_01.show()

    # Editor 02: style loaded from the file we just saved
    editor_02 = pcef.QCodeEdit()
    editor_02.setWindowTitle("Editor 02")
    editor_02.style.open(file_path)
    editor_02.show()

    # not needed anymore
    os.remove(file_path)

    # run
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
