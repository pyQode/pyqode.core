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
Qt resource compiler scripts. Compiles for pyside and pyqt.

Scans the directories recursively (starting for the cwd) for qrc files then
compile each qrc file (NAME.qrc) to:
    - NAME_pyqt_rc.py
    - NAME_pyside_rc.py
"""
import fnmatch
import os

def findQrcFilesRecursively(root=os.getcwd()):
    matches = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, '*.qrc'):
            matches.append(os.path.join(root, filename))
    return matches


def compile_rc(root=os.getcwd()):
    matches = findQrcFilesRecursively(root)
    for name in matches:
        base = name.split(".")[0]
        cmd = "pyrcc4 -py3 {0} > {1}_pyqt_rc.py".format(name, base)
        print(cmd)
        os.system(cmd)
        cmd = "pyside-rcc -py3 {0} > {1}_pyside_rc.py".format(name, base)
        print(cmd)
        os.system(cmd)


if __name__ == "__main__":
    compile_rc()