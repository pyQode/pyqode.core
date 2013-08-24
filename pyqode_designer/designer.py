#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
Run this script to run qt designer with the pyqode plugins.

Requires
---------

On linux you need to install python-qt and python-qt-dev.

On windows you just have to install PyQt with its designer.

Usage
-----

You can try the pyqode qt designer plugin without installing pyqode, just run
designer.pyw from the source package.

If pyqode is installed, this script is installed into the Scripts folder on
windows or in a standard bin folder on linux. Open a terminal and run
**pyqode_designer**.
"""
import os
os.environ.setdefault("QT_API", "PyQt")
import pkg_resources
import subprocess
import sys


def get_pth_sep():
    """
    Gets platform dependand path separator
    """
    if sys.platform == "win32":
        sep = ';'
    else:
        sep = ':'
    return sep


def set_plugins_path(env, sep):
    """
    Sets PYQTDESIGNERPATH
    """
    paths = ""
    dict = {}
    for entrypoint in pkg_resources.iter_entry_points("pyqode_plugins"):
        plugin = entrypoint.load()
        pth = os.path.dirname(plugin.__file__)
        if not pth in dict:
            paths += pth + sep
            dict[pth] = None
    if 'PYQTDESIGNERPATH' in env:
        pyqt_designer_path = env['PYQTDESIGNERPATH']
        env['PYQTDESIGNERPATH'] = pyqt_designer_path + sep + paths
    else:
        env['PYQTDESIGNERPATH'] = paths
    print("pyQode plugins paths: %s" % env["PYQTDESIGNERPATH"])


def run(env):
    """
    Runs qt designer with our customised environment.
    """
    p = None
    try:
        p = subprocess.Popen(["designer"], env=env)
        if p.wait():
            raise OSError()
    except OSError:
        try:
            p = subprocess.Popen(["designer-qt4"], env=env)
            if p.wait():
                raise OSError()
        except OSError:
            try:
                p = subprocess.Popen(["designer-qt4"], env=env)
                if p.wait():
                    raise OSError()
            except OSError:
                print("Failed to start Qt Designer")
    if p:
        return p.wait()
    return -1


def check_env(env):
    """
    Ensures all key and values are strings on windows.
    """
    if sys.platform == "win32":
        win_env = {}
        for key, value in env.items():
            win_env[str(key)] = str(value)
        env = win_env
    return env


def main():
    """
    Runs the Qt Designer with the correct plugin path.
    """
    sep = get_pth_sep()
    env = os.environ.copy()
    set_plugins_path(env, sep)
    env = check_env(env)
    return run(env)


if __name__ == "__main__":
    # import pyqode
    sys.exit(main())
