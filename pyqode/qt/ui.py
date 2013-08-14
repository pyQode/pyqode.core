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
Provides a binding independent loadUi function.
"""
import os


def loadUi(uiFile, baseInstance):
    """
    Loads an ui file using the selected qt bindings' loadUi

    :param uiFile: The ui file to load

    :param baseInstance: baseInstance
    """
    if os.environ["QT_API"] == "PySide":
        from pyqode.qt.pyside_ui import loadUi as load_ui
    else:
        from pyqode.qt.pyqt_ui import loadUi as load_ui
    try:
        load_ui(uiFile, baseInstance)
    except IOError:
        # maybe we are in a frozen script, in that case user should copy pyqode
        # ui to the root folder
        load_ui(os.path.join("pyqode_ui", os.path.split(uiFile)[1]),
                baseInstance)


def importRc(rcFile):
    """
    Executes the code of the script that corresponds to rcFile.

    Here is the expected rc script file name format :
        ** rcFile base name + suffix + _rc.py**

    Suffix is pyside or pyqt depending on the binding you want to use.

    .. remarks:: you can copy the pyqode.core.ui.translate_ui module next to your
                 qrc files to compile them with the expected format.

    :param rcFile: The qrc filename to import.
    """
    import imp
    base = os.path.splitext(rcFile)[0]
    if os.environ["QT_API"] == "PySide":
        filePath = base + "_pyside_rc.py"
    else:
        filePath = base + "_pyqt_rc.py"
    with open(filePath, "r") as f:
        name = os.path.basename(filePath).replace(".py", "")
        imp.load_module(name, f, filePath,
                        ("", "r", 1))
