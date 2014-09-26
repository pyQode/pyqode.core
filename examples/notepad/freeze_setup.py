#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This setup script build a frozen distribution of the application (with the
python interpreter and 3rd party libraries embedded) for Windows.

Run the following command to freeze the app (the frozen executable can be
found in the bin folder::

    python freeze_setup.py build

"""
import os
import sys
from cx_Freeze import setup, Executable
import shutil

from pyqode.core.modes import PYGMENTS_STYLES


def read_version():
    """
    Reads the version without self importing
    """
    with open("notepad/__init__.py") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                return l.split("=")[1].strip().replace('"', "").replace("'", '')


# automatically build when run without arguments
if len(sys.argv) == 1:
    sys.argv.append("build")

# Build options
options = {"excludes": ["PyQt5.uic.port_v3", "PySide", "tcltk", "jedi"],
           "namespace_packages": ["pyqode.core"],
           "include_msvcr": True,
           "build_exe": "bin",
           "includes": ["pkg_resources"] +
                       ["pygments.styles.%s" % style for style in PYGMENTS_STYLES
                        if not 'darcula' in style and not 'qt' in style]}

# Run the cxFreeze setup
setup(name="Notepad",
      version=read_version(),
      options={"build_exe": options},
      executables=[
          Executable("notepad.py", targetName="Notepad.exe",
                     icon='share/notepad.ico',
                     base="Win32GUI"),
          Executable("notepad/server.py",
                     targetName="server.exe")])

# NOTE: if you are using PyQt5, you will have to copy libEGL.dll manually
try:
    import PyQt5
except ImportError:
    pass  # pyqt4 or pyqside
else:
    shutil.copy(os.path.join(os.path.dirname(PyQt5.__file__), 'libEGL.dll'), 'bin')

