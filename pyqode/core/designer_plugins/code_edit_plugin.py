# -*- coding: utf-8 -*-
"""
This module contains the CodeEdit designer plugin.
"""
from pyqode.core import frontend
from pyqode.core.designer_plugins import WidgetPlugin
# pylint: disable=missing-docstring, invalid-name, interface-not-implemented


class CodeEditPlugin(WidgetPlugin):
    """
    Designer plugin for CodeEdit.
    """
    def klass(self):
        return frontend.CodeEdit

    def objectName(self):
        return 'codeEdit'
