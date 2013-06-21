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
Run this script to run qt designer with the pcef plugins.

Requires
---------

On linux you need to install python-qt and python-qt-dev.

On windows you just have to install PyQt with its designer.

Usage
-----

You can try the pcef qt designer plugin without installing pcef, just run
designer.py from the source package.

If pcef is installed, this script is installed into the Scripts folder on
windows or in a standard bin folder on linux. Open a terminal and run
**pcef_designer**
"""
import os
import subprocess
import sys
os.environ.setdefault("QT_API", "PyQt")
import pcef
from PyQt4 import QtCore, QtGui


def main():
    print("PCEF DESIGNER")
    # path separator are different on windows
    if sys.platform == "win32":
        sep = ';'
    else:
        sep = ':'

    # start qt gui system
    app = QtGui.QApplication(sys.argv)

    # read environment variables
    env = os.environ.copy()

    # let the user try pcef without installing
    import pcef

    dir = QtCore.QFileInfo(pcef.__file__).dir()
    dir.cdUp()
    pcef_path = dir.path()
    if 'PYTHONPATH' in env:
        python_pth = env['PYTHONPATH']
        if pcef_path not in python_pth.split(sep):
            env['PYTHONPATH'] = python_pth + sep + pcef_path
    else:
        env['PYTHONPATH'] = pcef_path
    print(pcef_path)

    # define plugin path
    plugins_path = os.path.join(pcef_path, "pcef", "plugins")
    if 'PYQTDESIGNERPATH' in env:
        pyqt_designer_path = env['PYQTDESIGNERPATH']
        if plugins_path not in pyqt_designer_path.split(sep):
            env['PYQTDESIGNERPATH'] = pyqt_designer_path + sep + plugins_path
    else:
        env['PYQTDESIGNERPATH'] = plugins_path
    print(plugins_path)

    # ensure every keys and values are strings
    if sys.platform == "win32":
        win_env = {}
        for key, value in env.items():
            win_env[str(key)] = str(value)
        env = win_env

    # run designer
    try:
        p = subprocess.Popen(["designer"], env=env)
    except OSError:
        try:
            p = subprocess.Popen(["designer-qt4"], env=env)
        except OSError:
            try:
                p = subprocess.Popen(["designer-qt4"], env=env)
            except OSError:
                print("Failed to start Qt Designer")
    if p:
        return p.wait()
    return -1

if __name__ == "__main__":
    sys.exit(main())

