# -*- coding: utf-8 -*-
"""
This package contains the ui files and their compiled version.

.. warning: To make it easy to use the *.ui and *.qrc with all python version
            and different qt bindings, we compile the ui and qrc file using
            pyuic4/pyrcc4 (with -py3 switchà then manually edit those files
            to import QtCore and QtGui from PyQt4 instead of PyQt4.

            The compile_ui script automates this task, simply run it to update
            all *.ui/*.qrc.
"""
