# -*- coding: utf-8 -*-
"""
This file contains all the pyQode QtDesigner plugins.

Installation:
==================

run designer.py (Qt Designer must be installed on your system and must be
in your path on Windows, pyqode-core must be installed)
"""
import pyqode.core.code_edit

# Define this mapping to help the PySide's form builder create the correct
# widget
PLUGINS_TYPES = {'QCodeEdit': pyqode.core.code_edit.QCodeEdit}

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
            QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self,
                                                              parent=parent)
            self.initialized = False

        def initialize(self, form_editor):
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

except ImportError:
    print("Cannot use pyqode plugins without PyQt4")
