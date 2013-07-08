#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
This script calls the PyQt ui compiler on all ui files found in the cwd.
(It also compiles the qrc files to *_rc.py)
"""
import glob
import os


def replace_rc_imports(filename, suffix="_pyqt"):
    with open(filename, "r") as f:
        content = f.read()
    new_content = ""
    lines = content.splitlines()
    for l in lines:
        if l.startswith("import"):
            to_replace = l.split(" ")[1]
            replacement = "ui.{0}{1}".format(to_replace, suffix)
            l = l.replace(to_replace, replacement)
        new_content += "%s\n" % l
    with open(filename, "w") as f:
        f.write(new_content)


def compile_pyqt_ui(base, name):
    # python 3
    cmd = "pyuic4 -w {0} > {1}_ui3_pyqt.py ".format(name, base)
    print(cmd)
    os.system(cmd)
    replace_rc_imports("{0}_ui3_pyqt.py".format(base), suffix="3_pyqt")
    # replace import *_rc by pcef.core.ui.*_rc3
    # python 2
    cmd = "pyuic4 {0} > {1}_ui_pyqt.py ".format(name, base)
    print(cmd)
    os.system(cmd)
    replace_rc_imports("{0}_ui_pyqt.py".format(base), suffix="_pyqt")


def compile_pyside_ui(base, name):
    # python 3
    cmd = "pyside-uic {0} > {1}_ui3_pyside.py ".format(name, base)
    print(cmd)
    os.system(cmd)
    replace_rc_imports("{0}_ui3_pyside.py".format(base), suffix="3_pyside")
    # replace import *_rc by pcef.core.ui.*_rc3
    # python 2
    cmd = "pyside-uic {0} > {1}_ui_pyside.py ".format(name, base)
    print(cmd)
    os.system(cmd)
    replace_rc_imports("{0}_ui_pyside.py".format(base), suffix="_pyside")


def compile_pyqt_rc(base, name):
    # python 3
    cmd = "pyrcc4 -py3 {0} > {1}_rc3_pyqt.py".format(name, base)
    print(cmd)
    os.system(cmd)
    # python 2
    cmd = "pyrcc4 {0} > {1}_rc_pyqt.py".format(name, base)
    print(cmd)
    os.system(cmd)


def compile_pyside_rc(base, name):
    # python 3
    cmd = "pyside-rcc -py3 {0} > {1}_rc3_pyside.py".format(name, base)
    print(cmd)
    os.system(cmd)
    # python 2
    cmd = "pyside-rcc {0} > {1}_rc_pyside.py".format(name, base)
    print(cmd)
    os.system(cmd)


def compile_ui():
    for name in glob.glob("*.ui"):
        base = name.split(".")[0]
        compile_pyqt_ui(base, name)
        compile_pyside_ui(base, name)


def compile_rc():
    for name in glob.glob("*.qrc"):
        base = name.split(".")[0]
        compile_pyqt_rc(base, name)
        compile_pyside_rc(base, name)


if __name__ == "__main__":
    compile_ui()
    compile_rc()



