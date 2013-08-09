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
This file contains all the pyQode QtDesigner plugins.

Installation:
==================

run designer.pyw (Qt Designer must be installed on your system and must be
in your path on Windows, pyqode-core must be installed)
"""
# This only works with PyQt, PySide does not support the QtDesigner module
import os
if not 'QT_API' in os.environ:
    os.environ.setdefault("QT_API", "PyQt")
import pyqode.core

# Define this mapping to help the PySide's form builder create the correct
# widget
PLUGINS_TYPES = {'QCodeEdit': pyqode.core.QCodeEdit,
                 "QGenericCodeEdit": pyqode.core.QGenericCodeEdit}

try:
    from PyQt4 import QtDesigner

    class QCodeEditPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
        """Designer plugin for pyqode.QCodeEdit.
        Also serves as base class for other custom widget plugins."""

        _module = 'pyqode.core'        # path to the widget's module
        _class = 'QCodeEdit'    # name of the widget class
        _name = "QCodeEdit"
        _icon = None
        _type = pyqode.core.QCodeEdit

        def __init__(self, parent=None):
            QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
            self.initialized = False

        def initialize(self, formEditor):
            self.initialized = True

        def isInitialized(self):
            return self.initialized

        def isContainer(self):
            return False

        def icon(self):
            return None

        def domXml(self):
            return '<widget class="%s" name="%s">\n</widget>\n' % (self._class,
                                                                   self.name())

        def group(self):
            return 'pyqode'

        def includeFile(self):
            return self._module

        def name(self):
            return self._name

        def toolTip(self):
            return ''

        def whatsThis(self):
            return ''

        def createWidget(self, parent):
            return pyqode.core.QCodeEdit(parent)

    class QGenericCodeEditPlugin(QCodeEditPlugin):
        _module = 'pyqode.core'        # path to the widget's module
        _class = 'QGenericCodeEdit'    # name of the widget class
        _name = "QGenericCodeEdit"
        _icon = None
        _type = pyqode.core.QGenericCodeEdit

        def createWidget(self, parent):
            return pyqode.core.QGenericCodeEdit(parent)
except ImportError:
    print("Cannot use pyqode plugins without PyQt4")
